"""Leitura do roteiro de edição (YAML) e conversão de gatilhos em tempos."""

import copy
import difflib
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import transcricao

PADRAO = {
    "saida": None,
    "transcricao": None,
    "resolucao": [1080, 1920],
    "fps": 30,
    "qualidade": 18,
    "layout_padrao": "cheio",
    "tema": {
        "fundo": ["#0b1020", "#1c2541"],
        "destaque": "#facc15",
        "secundaria": "#38bdf8",
        "texto": "#ffffff",
        "positivo": "#22c55e",
        "negativo": "#ef4444",
        "fonte": None,
        "linha_divisoria": True,
    },
    "legendas": {
        "ativas": True,
        "estilo": "destaque",  # destaque | caixa | simples
        "palavras_por_bloco": 3,
        "max_caracteres": 20,
        "maiusculas": True,
        "tamanho": 82,
        "posicao_cheio": 0.72,  # altura relativa da legenda com tela cheia
        "posicao_dividido": "divisao",  # 'divisao' ou número 0..1
        "remover_pontuacao": True,
        "substituicoes": {},
    },
    "divisao": {
        "proporcao": 0.5,  # fração da altura ocupada pela animação
        "animacao_em": "cima",  # cima | baixo
        "foco_rosto": 0.36,  # altura (0..1) do rosto no vídeo original
        "zoom_rosto": 1.0,
        "transicao": 0.35,
    },
    "eventos": [],
}

DURACAO_PADRAO = 3.0


@dataclass
class Evento:
    inicio: float
    fim: float
    layout: str
    animacao: dict | None = None
    zoom: dict | None = None
    origem: str = ""
    indice: int = 0
    extras: dict = field(default_factory=dict)


def mesclar(base, novo):
    res = copy.deepcopy(base)
    for k, v in (novo or {}).items():
        if isinstance(v, dict) and isinstance(res.get(k), dict):
            res[k] = mesclar(res[k], v)
        else:
            res[k] = v
    return res


def ler_tempo(valor):
    """Aceita 12, 12.5, '12s', '0:12', '1:02.5', '00:01:02'."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().lower().rstrip("s")
    partes = texto.split(":")
    total = 0.0
    for p in partes:
        total = total * 60 + float(p.replace(",", "."))
    return total


# ---------------------------------------------------------------- gatilhos

def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]+", " ", texto).strip()


class Localizador:
    """Encontra em que momento do vídeo uma frase foi falada."""

    def __init__(self, palavras):
        self.palavras = palavras
        self.tokens = [normalizar(p["palavra"]) for p in palavras]
        # Palavras como "dá-me" viram mais de um token: guardamos o índice da palavra original.
        self.planos, self.indice = [], []
        for i, tok in enumerate(self.tokens):
            for parte in tok.split():
                self.planos.append(parte)
                self.indice.append(i)

    def encontrar(self, frase, ocorrencia=1, depois_de=0.0):
        alvo = normalizar(frase).split()
        if not alvo:
            raise ValueError("Gatilho vazio")
        n = len(alvo)
        exatos, aproximados = [], []
        for i in range(len(self.planos) - n + 1):
            janela = self.planos[i:i + n]
            p_ini = self.palavras[self.indice[i]]
            p_fim = self.palavras[self.indice[i + n - 1]]
            if p_ini["inicio"] < depois_de:
                continue
            if janela == alvo:
                exatos.append((p_ini["inicio"], p_fim["fim"]))
            else:
                r = difflib.SequenceMatcher(None, " ".join(janela), " ".join(alvo)).ratio()
                if r >= 0.82:
                    aproximados.append((p_ini["inicio"], p_fim["fim"], r))
        if len(exatos) >= ocorrencia:
            return exatos[ocorrencia - 1]
        if not exatos and len(aproximados) >= ocorrencia:
            ini, fim, _ = aproximados[ocorrencia - 1]
            return ini, fim
        raise ValueError(self._erro(frase, ocorrencia, len(exatos)))

    def _erro(self, frase, ocorrencia, achados):
        alvo = normalizar(frase)
        n = max(1, len(alvo.split()))
        candidatos = {" ".join(self.planos[i:i + n]) for i in range(len(self.planos) - n + 1)}
        parecidos = difflib.get_close_matches(alvo, candidatos, n=3, cutoff=0.5)
        msg = f'Não encontrei "{frase}" na transcrição'
        if achados:
            msg += f" (apareceu {achados}x, mas você pediu a ocorrência {ocorrencia})"
        if parecidos:
            msg += ". Talvez você quis dizer: " + ", ".join(f'"{p}"' for p in parecidos)
        return msg


# ---------------------------------------------------------------- roteiro

class Roteiro:
    def __init__(self, caminho, exigir_video=True):
        self.caminho = Path(caminho)
        bruto = yaml.safe_load(self.caminho.read_text(encoding="utf-8")) or {}
        self.cfg = mesclar(PADRAO, bruto)
        base = self.caminho.parent
        self.raiz_projeto = Path(__file__).resolve().parent.parent

        self.video = self._resolver_caminho(self.cfg.get("video"), base)
        if exigir_video and (not self.video or not self.video.exists()):
            raise SystemExit(f"Vídeo não encontrado: {self.cfg.get('video')}")
        saida = self.cfg.get("saida") or f"saida/{self.video.stem}_editado.mp4"
        self.saida = self._resolver_caminho(saida, base, deve_existir=False)
        trans = self.cfg.get("transcricao")
        self.arquivo_transcricao = (self._resolver_caminho(trans, base, deve_existir=False) if trans
                                    else transcricao.caminho_transcricao(self.video))
        self.base = base
        self._palavras = None

    def _resolver_caminho(self, valor, base, deve_existir=True):
        if not valor:
            return None
        p = Path(valor).expanduser()
        if p.is_absolute():
            return p
        for raiz in (base, self.raiz_projeto, Path.cwd()):
            if (raiz / p).exists():
                return (raiz / p).resolve()
        return (self.raiz_projeto / p).resolve() if not deve_existir else (base / p).resolve()

    def arquivo(self, valor):
        """Resolve caminhos de imagens/vídeos citados nas animações."""
        caminho = self._resolver_caminho(valor, self.base)
        if not caminho or not caminho.exists():
            raise SystemExit(f"Arquivo não encontrado: {valor}")
        return caminho

    # -------------------------------------------------------------- transcrição
    def precisa_transcricao(self):
        if self.cfg["legendas"].get("ativas"):
            return True
        return any(_tem_gatilho(e) for e in self.cfg["eventos"])

    @property
    def palavras(self):
        if self._palavras is None:
            if not self.arquivo_transcricao.exists():
                if not self.precisa_transcricao():
                    self._palavras = []
                    return self._palavras
                print("Transcrição não encontrada; transcrevendo agora...")
                transcricao.transcrever(self.video, modelo=self.cfg.get("modelo_whisper", "small"),
                                        destino=self.arquivo_transcricao)
            self._palavras = transcricao.carregar(self.arquivo_transcricao)["palavras"]
        return self._palavras

    # -------------------------------------------------------------- eventos
    def eventos(self):
        loc = Localizador(self.palavras) if self.palavras else None
        eventos = []
        for i, bruto in enumerate(self.cfg["eventos"] or [], start=1):
            try:
                eventos.append(self._resolver_evento(bruto, loc, i))
            except ValueError as erro:
                raise SystemExit(f"Evento {i}: {erro}") from erro
        eventos.sort(key=lambda e: e.inicio)
        return eventos

    def _momento(self, bruto, loc, chave_tempo, chave_frase, usar_fim=False, depois_de=0.0):
        if bruto.get(chave_tempo) is not None:
            return ler_tempo(bruto[chave_tempo])
        if bruto.get(chave_frase):
            if loc is None:
                raise ValueError("gatilho por frase precisa de transcrição")
            if bruto.get("depois_de") is not None and chave_frase == "quando":
                depois_de = ler_tempo(bruto["depois_de"])
            ocorrencia = int(bruto.get("ocorrencia", 1)) if chave_frase == "quando" else 1
            ini, fim = loc.encontrar(bruto[chave_frase], ocorrencia, depois_de)
            return fim if usar_fim else ini
        return None

    def _resolver_evento(self, bruto, loc, indice):
        inicio = self._momento(bruto, loc, "em", "quando")
        if inicio is None:
            raise ValueError("defina 'em' (tempo) ou 'quando' (frase falada)")
        inicio = max(0.0, inicio + float(bruto.get("ajuste", 0.0)))

        fim = self._momento(bruto, loc, "ate", "ate_quando", usar_fim=True, depois_de=inicio)
        if fim is None:
            fim = inicio + float(bruto.get("duracao", DURACAO_PADRAO))
        if fim <= inicio:
            raise ValueError(f"o fim ({fim:.2f}s) vem antes do início ({inicio:.2f}s)")

        animacao = copy.deepcopy(bruto.get("animacao"))
        zoom = bruto.get("zoom")
        if bruto.get("tipo") == "zoom":
            zoom = zoom or {}
        if zoom is True:
            zoom = {}
        layout = bruto.get("layout") or ("dividido" if animacao else self.cfg["layout_padrao"])

        if animacao:
            self._resolver_subtempos(animacao, loc, inicio)

        origem = f'"{bruto["quando"]}"' if bruto.get("quando") else f"{inicio:.2f}s"
        return Evento(inicio, fim, layout, animacao, zoom, origem, indice)

    def _resolver_subtempos(self, animacao, loc, inicio_evento):
        """Itens de listas/passos podem ter seu próprio 'quando' ou 'em'."""
        for item in animacao.get("itens", []) or []:
            if isinstance(item, dict) and (item.get("quando") or item.get("em") is not None):
                t = self._momento(item, loc, "em", "quando", depois_de=max(0.0, inicio_evento - 0.5))
                item["_t"] = max(0.0, t - inicio_evento)


def _tem_gatilho(evento):
    if evento.get("quando") or evento.get("ate_quando"):
        return True
    itens = (evento.get("animacao") or {}).get("itens") or []
    return any(isinstance(i, dict) and i.get("quando") for i in itens)
