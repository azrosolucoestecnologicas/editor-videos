"""Planejador de cenas: esqueleto, preservação de edições à mão e validação.

O `scene_plan.json` é a ponte entre a transcrição e a composição Remotion.
Este módulo faz três coisas e só três:

1. `esqueleto()` divide o vídeo cortado em cenas de 3 a 6 segundos, ancoradas
   numa palavra-gatilho que existe literalmente na transcrição, e deixa `tipo`
   e `conteudo` em branco. Decidir o que cada cena mostra é trabalho de quem
   entende o que foi dito, não de uma heurística.
2. `mesclar()` reaplica o esqueleto preservando tudo que foi editado à mão.
   Uma cena é considerada editada quando seu conteúdo não bate mais com o
   `_hash` gravado na última escrita.
3. `validar()` confere o plano contra as regras das skills `reels-ritmo`,
   `reels-composicao` e `reels-legendas`.

As legendas saem num arquivo irmão, derivado da transcrição e do glossário.
Correção de texto de legenda se faz em `glossario.json`, não aqui.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

from . import glossario as mod_glossario
from .texto_util import normalizar

RAIZ = Path(__file__).resolve().parent.parent
PASTA_PLANOS = RAIZ / "planos"
PASTA_PUBLICA = RAIZ / "motion" / "public"
FPS = 30

# ---------------------------------------------------------------- ritmo
# Valores da skill `reels-ritmo`.
CENA_MINIMA = 1.5          # ninguém lê uma cena mais curta
CENA_ALVO_MIN = 3.0        # uma mudança visual a cada 3 a 6 s
CENA_ALVO_MAX = 6.0
LACUNA_MAXIMA = 8.0        # nenhum intervalo sem cena maior que isto
ABERTURA_MAXIMA = 0.5      # a primeira cena precisa estar na tela até aqui
FECHAMENTO_MINIMO = 1.5    # os últimos segundos ficam com a cena-síntese

# ---------------------------------------------------------------- legendas
# Valores da skill `reels-legendas`.
BLOCO_MIN_PALAVRAS = 2
BLOCO_MAX_PALAVRAS = 5
LINHA_MAX_CARACTERES = 28
BLOCO_MAX_LINHAS = 2
BLOCO_DURACAO_MINIMA = 0.6
PAUSA_QUEBRA = 0.45
# Cotas da skill: a quarta pílula tira o peso das outras três, e se todo card
# brilha, nenhum brilha.
MAXIMAS_POR_REEL = 3
CENAS_COM_BRILHO = 2
# Zoom de ênfase no vídeo: no mínimo 8 s entre um e outro.
INTERVALO_ZOOM = 8.0

FIM_DE_FRASE = re.compile(r"[.!?]$")
PONTUACAO_FINAL = re.compile(r"[.,;:!?…]+$")

# "artigo, preposição e número ficam com a palavra seguinte": um bloco nunca
# termina numa destas.
FUNCIONAIS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "em", "no", "na", "nos", "nas", "e", "ou", "que", "com", "por",
    "pelo", "pela", "ao", "aos", "se", "sem", "sob", "sobre", "num", "numa",
    "entre", "ate", "desde", "para", "pra",
}

# Palavras que, estando no bloco, merecem o destaque em cobre.
NEGACOES = {"nao", "nunca", "nenhum", "nenhuma", "jamais", "sem"}

EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002190-\U000021FF\U00002300-\U000023FF"
    "\U00002460-\U000027BF\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F]"
)


# ---------------------------------------------------------------- catálogo
def _palavras(texto):
    return [p for p in re.split(r"\s+", str(texto or "").strip()) if p]


def _limite(conteudo, campo, maximo, rotulo):
    n = len(_palavras(conteudo.get(campo)))
    if n > maximo:
        return [f"{rotulo} tem {n} palavras (máximo {maximo})"]
    if n == 0:
        return [f"{rotulo} está vazio"]
    return []


def _ver_card_conceito(c):
    erros = _limite(c, "termo", 4, "o termo")
    return erros + _limite(c, "definicao", 12, "a definição")


def _ver_lista(c):
    itens = c.get("itens") or []
    erros = []
    if not 2 <= len(itens) <= 4:
        erros.append(f"lista com {len(itens)} itens (a skill pede de 2 a 4)")
    for i, item in enumerate(itens, start=1):
        erros += _limite(item, "texto", 6, f"o item {i}")
    return erros


def _ver_comparacao(c):
    erros = []
    for lado in ("esquerda", "direita"):
        coluna = c.get(lado) or {}
        if not coluna:
            erros.append(f"falta a coluna {lado}")
            continue
        linhas = coluna.get("linhas") or []
        if not 1 <= len(linhas) <= 3:
            erros.append(f"coluna {lado} com {len(linhas)} linhas (máximo 3)")
        erros += _limite(coluna, "titulo", 3, f"o título da coluna {lado}")
    return erros


def _ver_fluxo(c):
    etapas = c.get("etapas") or []
    erros = []
    if not 3 <= len(etapas) <= 5:
        erros.append(f"fluxo com {len(etapas)} etapas (a skill pede de 3 a 5)")
    for i, etapa in enumerate(etapas, start=1):
        erros += _limite(etapa, "rotulo", 3, f"o rótulo da etapa {i}")
    return erros


def _ver_numero(c):
    erros = []
    if not str(c.get("valor") or "").strip():
        erros.append("falta o valor do número")
    return erros + _limite(c, "rotulo", 6, "o rótulo")


def _ver_citacao_legal(c):
    erros = []
    if not str(c.get("referencia") or "").strip():
        erros.append("falta a referência")
    if str(c.get("trecho") or "").strip():
        erros += _limite(c, "trecho", 20, "o trecho")
    return erros


# A mesma lista do mapa `ICONES` em motion/src/icones.ts. Está escrita duas
# vezes porque os dois lados precisam dela sozinhos; `tests/test_catalogo.py`
# compara as duas e falha se alguém mexer só numa.
ICONES_DISPONIVEIS = frozenset({
    "alert-triangle", "book-open", "brain", "calendar-days", "check-circle",
    "clock", "file-search", "file-text", "file-warning", "gavel", "landmark",
    "lightbulb", "lock", "message-circle", "scale", "search", "shield-check",
    "target", "trending-up", "users", "x-circle", "zap",
})


def _ver_icone_destaque(c):
    erros = []
    nome = str(c.get("icone") or "").strip()
    if not nome:
        erros.append("falta o nome do ícone (lucide-react)")
    elif nome not in ICONES_DISPONIVEIS:
        # Pego aqui, no validar, e não no render: um nome errado fazia o
        # Remotion publicar outro ícone sem reclamar.
        erros.append(
            f'o ícone "{nome}" não existe; use um de: '
            f'{", ".join(sorted(ICONES_DISPONIVEIS))}'
        )
    return erros + _limite(c, "texto", 4, "o texto")


def _ver_sintese(c):
    return _limite(c, "frase", 10, "a frase")


CATALOGO = {
    "card_conceito": {"quando": "definir um termo", "verificar": _ver_card_conceito},
    "lista": {"quando": "enumeração falada", "verificar": _ver_lista},
    "comparacao": {"quando": "antes/depois, humano/IA", "verificar": _ver_comparacao},
    "fluxo": {"quando": "processo, pipeline", "verificar": _ver_fluxo},
    "numero": {"quando": "estatística, prazo, valor", "verificar": _ver_numero},
    "citacao_legal": {"quando": "artigo, súmula, tese", "verificar": _ver_citacao_legal},
    "icone_destaque": {"quando": "ideia-chave sem estrutura", "verificar": _ver_icone_destaque},
    "sintese": {"quando": "fechamento", "verificar": _ver_sintese},
}


def textos_da_cena(cena):
    """Todo texto visível de uma cena, para checar repetição com a legenda."""
    c = cena.get("conteudo") or {}
    tipo = cena.get("tipo")
    if tipo == "card_conceito":
        return [c.get("termo"), c.get("definicao")]
    if tipo == "lista":
        return [c.get("titulo")] + [i.get("texto") for i in c.get("itens") or []]
    if tipo == "comparacao":
        saida = []
        for lado in ("esquerda", "direita"):
            coluna = c.get(lado) or {}
            saida.append(coluna.get("titulo"))
            saida += coluna.get("linhas") or []
        return saida
    if tipo == "fluxo":
        return [e.get("rotulo") for e in c.get("etapas") or []]
    if tipo == "numero":
        return [str(c.get("valor") or ""), c.get("rotulo")]
    if tipo == "citacao_legal":
        return [c.get("referencia"), c.get("trecho")]
    if tipo == "icone_destaque":
        return [c.get("texto")]
    if tipo == "sintese":
        return [c.get("frase")]
    return []


# ---------------------------------------------------------------- legendas
def _visuais(bloco):
    """Quantas palavras o bloco ocupa na linha.

    Uma entrada fundida pelo glossário ("MBA de IA no Direito") conta como
    cinco, senão o bloco estoura a largura da faixa.
    """
    return sum(len(w["palavra"].split()) for w in bloco)


def _fechavel(bloco, fim_na_tela):
    """Um bloco só fecha com 2 palavras e 0,6 s de tela; senão vira um flash."""
    if not bloco:
        return False
    return (
        _visuais(bloco) >= BLOCO_MIN_PALAVRAS
        and fim_na_tela - bloco[0]["inicio"] >= BLOCO_DURACAO_MINIMA
    )


def blocos_legenda(palavras):
    """Agrupa as palavras já corrigidas em blocos de legenda.

    Mesma lógica de agrupamento de `editor/legendas.py` (pausa, pontuação,
    limite de palavras e de caracteres), com os limites da skill
    `reels-legendas` e uma palavra destacada por bloco.
    """
    blocos, atual = [], []

    def fechar():
        if atual:
            blocos.append(list(atual))
            atual.clear()

    anterior = None
    for p in palavras:
        texto = p["palavra"].strip()
        if not texto:
            continue
        pausa = anterior is not None and p["inicio"] - anterior["fim"] > PAUSA_QUEBRA
        caracteres = sum(len(w["palavra"]) + 1 for w in atual) + len(texto)
        # Uma entrada fundida pelo glossário ("MBA de IA no Direito") ocupa a
        # linha como cinco palavras, não como uma.
        visuais = sum(len(w["palavra"].split()) for w in atual) + len(texto.split())
        cheio = (
            visuais > BLOCO_MAX_PALAVRAS
            or caracteres > LINHA_MAX_CARACTERES * BLOCO_MAX_LINHAS
        )
        if atual and (cheio or pausa):
            # "artigo, preposição e número ficam com a palavra seguinte":
            # o órfão migra para o bloco novo em vez de segurar o atual.
            orfao = len(atual) > 1 and normalizar(atual[-1]["palavra"]) in FUNCIONAIS
            if orfao and _fechavel(atual[:-1], atual[-1]["inicio"]):
                preso = atual.pop()
                fechar()
                atual.append(preso)
            elif _fechavel(atual, p["inicio"]):
                fechar()
        atual.append(p)
        if FIM_DE_FRASE.search(texto) and _visuais(atual) >= BLOCO_MIN_PALAVRAS:
            fechar()
        anterior = p
    fechar()

    saida = []
    for i, bloco in enumerate(blocos):
        inicio = bloco[0]["inicio"]
        fim = bloco[-1]["fim"]
        # O bloco fica na tela até o próximo começar, respeitando o mínimo.
        proximo = blocos[i + 1][0]["inicio"] if i + 1 < len(blocos) else None
        if proximo is not None and proximo - inicio >= BLOCO_DURACAO_MINIMA:
            fim = proximo
        else:
            fim = max(fim, inicio + BLOCO_DURACAO_MINIMA)
            if proximo is not None:
                fim = min(fim, proximo)
        saida.append({
            "inicio": round(inicio, 3),
            "fim": round(fim, 3),
            "destaque": _indice_destaque(bloco),
            "maxima": None,
            "palavras": [
                {
                    "texto": p["palavra"],
                    "inicio": round(p["inicio"], 3),
                    "fim": round(p["fim"], 3),
                }
                for p in bloco
            ],
        })
    return _marcar_maximas(saida)


def _marcar_maximas(blocos):
    """Promove até 3 destaques ao nível "máxima" (pílula cobre).

    Heurística conservadora: ganha quem tem dígito (número que decide), depois
    sigla em caixa alta. É palpite — a cota de 3 da skill `reels-legendas`
    existe justamente porque a quarta pílula tira o peso das outras três.
    """
    candidatos = []
    for i, bloco in enumerate(blocos):
        j = bloco["destaque"]
        if j is None:
            continue
        texto = PONTUACAO_FINAL.sub("", bloco["palavras"][j]["texto"].strip())
        if any(c.isdigit() for c in texto):
            peso = 2
        elif len(texto) >= 3 and texto.isupper():
            peso = 1
        else:
            continue
        candidatos.append((peso, -i, i))

    for _, _, i in sorted(candidatos, reverse=True)[:MAXIMAS_POR_REEL]:
        # Um nível por bloco: quem vira pílula deixa de ser "chave".
        blocos[i]["maxima"] = blocos[i]["destaque"]
        blocos[i]["destaque"] = None
    return blocos


def _indice_destaque(bloco):
    """Uma palavra destacada por bloco, no máximo: número, sigla ou negação."""
    melhor, pontos_melhor = None, 0
    for i, p in enumerate(bloco):
        limpo = PONTUACAO_FINAL.sub("", p["palavra"].strip())
        sem_acento = normalizar(limpo)
        pontos = 0
        if any(c.isdigit() for c in limpo):
            pontos = 3
        elif len(limpo) >= 2 and limpo.isupper():
            pontos = 2
        elif sem_acento in NEGACOES:
            pontos = 1
        if pontos > pontos_melhor:
            melhor, pontos_melhor = i, pontos
    return melhor


# ---------------------------------------------------------------- esqueleto
def _melhor_corte(trecho):
    """Onde quebrar um trecho que passou dos 6 s.

    Procura a última vírgula ou ponto que ainda deixe uma cena de pelo menos
    3 s. Sem isso, a quebra cai no meio de uma oração — foi o que separava
    "Black | Friday Vitalícia" na primeira versão.
    """
    inicio = trecho[0]["inicio"]
    for k in range(len(trecho) - 1, 0, -1):
        anterior = trecho[k - 1]
        if (
            PONTUACAO_FINAL.search(anterior["palavra"].strip())
            and anterior["fim"] - inicio >= CENA_ALVO_MIN
        ):
            return k
    # Sem vírgula utilizável, quebra ANTES da palavra que estourou os 6 s em
    # vez de depois dela: deixa a cena dentro do alvo e dá à cena seguinte uma
    # palavra-gatilho com peso, não a sobra da anterior.
    if len(trecho) > 1 and trecho[-2]["fim"] - inicio >= CENA_ALVO_MIN:
        return len(trecho) - 1
    return len(trecho)


def _dividir_em_cenas(palavras, duracao):
    """Quebra a fala em trechos de 3 a 6 s, preferindo o fim de uma frase."""
    trechos, atual = [], []
    for p in palavras:
        atual.append(p)
        dur = atual[-1]["fim"] - atual[0]["inicio"]
        fim_frase = bool(FIM_DE_FRASE.search(p["palavra"].strip()))
        if dur >= CENA_ALVO_MIN and fim_frase:
            trechos.append(atual)
            atual = []
        elif dur >= CENA_ALVO_MAX:
            corte = _melhor_corte(atual)
            trechos.append(atual[:corte])
            atual = atual[corte:]
    if atual:
        trechos.append(atual)

    # Trechos curtos demais se juntam ao vizinho: nenhuma cena abaixo de 1,5 s.
    juntados = []
    for trecho in trechos:
        dur = trecho[-1]["fim"] - trecho[0]["inicio"]
        if juntados and dur < CENA_MINIMA:
            juntados[-1] += trecho
        else:
            juntados.append(trecho)
    if len(juntados) > 1:
        ultimo = juntados[-1]
        if ultimo[-1]["fim"] - ultimo[0]["inicio"] < CENA_MINIMA:
            juntados[-2] += juntados.pop()

    cenas = []
    for i, trecho in enumerate(juntados):
        # Sem trechos mortos: cada cena vai até o início da seguinte.
        inicio = 0.0 if i == 0 else trecho[0]["inicio"]
        fim = juntados[i + 1][0]["inicio"] if i + 1 < len(juntados) else duracao
        cenas.append((inicio, fim, trecho))
    return cenas


def _espacar_zooms(cenas):
    """Marca em quais cenas o vídeo recebe o zoom de ênfase.

    Sem isso o vídeo fica parado o reel inteiro. A skill `reels-movimento`
    pede no mínimo 8 s entre um zoom e outro; aqui o primeiro só entra depois
    da abertura, para o gancho não começar já se mexendo.
    """
    ultimo = -INTERVALO_ZOOM
    for cena in cenas[1:]:
        if cena["inicio"] - ultimo >= INTERVALO_ZOOM:
            cena["zoom"] = True
            ultimo = cena["inicio"]
    return cenas


def esqueleto(transcricao, video, duracao=None, assinatura="", gloss=None):
    """Monta o plano estrutural. `tipo` e `conteudo` ficam em branco de propósito."""
    gloss = gloss or mod_glossario.carregar()
    duracao = float(duracao if duracao is not None else transcricao["duracao"])

    # Tudo daqui para baixo trabalha sobre a transcrição JÁ CORRIGIDA pelo
    # glossário: é o texto que aparece na legenda, e é ele que mantém
    # "Black Friday Vitalícia" como uma unidade que a quebra não pode partir.
    # Os tempos são os mesmos — o glossário nunca os altera.
    corrigidas = gloss.aplicar(transcricao["palavras"])

    loc = LocalizadorSimples(corrigidas)
    indice_por_inicio = {round(p["inicio"], 3): i for i, p in enumerate(corrigidas)}

    cenas = []
    for n, (inicio, fim, trecho) in enumerate(_dividir_em_cenas(corrigidas, duracao), start=1):
        primeira = trecho[0]
        i = indice_por_inicio.get(round(primeira["inicio"], 3), 0)
        gatilho = PONTUACAO_FINAL.sub("", primeira["palavra"].strip())
        fala = " ".join(p["palavra"] for p in trecho)
        cena = {
            "id": f"c{n:02d}",
            "inicio": round(inicio, 3),
            "fim": round(fim, 3),
            "palavra_gatilho": gatilho,
            "ocorrencia": loc.ocorrencia_em(gatilho, i),
            "tipo": None,
            "conteudo": None,
            "editado": False,
            "_fala": fala,
        }
        cena["_hash"] = _hash(cena)
        cenas.append(cena)

    _espacar_zooms(cenas)
    for cena in cenas:
        cena["_hash"] = _hash(cena)

    return {
        "versao": 1,
        "video": _relativo(video),
        "duracao": round(duracao, 3),
        "fps": FPS,
        "fonte": dimensoes(video),
        "assinatura": assinatura,
        "enquadramento": {"foco_rosto": 0.36, "zoom": 1.0, "origem": "padrao"},
        "cenas": cenas,
    }


def legendas_do_plano(transcricao, gloss=None):
    gloss = gloss or mod_glossario.carregar()
    return blocos_legenda(gloss.aplicar(transcricao["palavras"]))


# Tudo que você pode escrever à mão no plano e esperar que sobreviva ao próximo
# `editar.py plano`. `zoom` e `brilho` entram aqui porque o Remotion os consome
# (scenes/base.tsx) e `validar` cobra cota deles como se fossem autorais — sem
# isso, ligar um brilho à mão era desfeito na rodada seguinte, sem aviso.
# O hash é recalculado depois de `_espacar_zooms`, então o zoom que o planejador
# distribui sozinho é a linha de base, não uma edição sua.
CAMPOS_DO_HASH = ("tipo", "conteudo", "inicio", "fim", "palavra_gatilho", "ocorrencia",
                  "zoom", "brilho")


def _sem_derivados(valor):
    """Remove os campos com prefixo `_`: eles são recalculados, não autorais."""
    if isinstance(valor, dict):
        return {k: _sem_derivados(v) for k, v in valor.items() if not k.startswith("_")}
    if isinstance(valor, list):
        return [_sem_derivados(v) for v in valor]
    return valor


def _chave(cena):
    """O que identifica uma cena entre duas rodadas do planejador.

    É a fala que a cena comenta — a palavra-gatilho e qual ocorrência dela —,
    não o id, que é apenas a posição na lista.
    """
    return (cena.get("palavra_gatilho"), cena.get("ocorrencia"))


def _hash(cena):
    bruto = json.dumps(
        _sem_derivados({k: cena.get(k) for k in CAMPOS_DO_HASH}),
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha1(bruto.encode("utf-8")).hexdigest()[:12]


def resolver_gatilhos(plano, transcricao, gloss=None):
    """Converte cada `palavra_gatilho` no segundo em que ela é falada.

    Grava o resultado em `_em` (campo derivado, recalculado a cada rodada e
    ignorado pelo hash). Vale para a cena e para qualquer elemento interno com
    palavra-gatilho própria: item de lista, etapa de fluxo, número.
    """
    gloss = gloss or mod_glossario.carregar()
    loc = LocalizadorSimples(gloss.aplicar(transcricao["palavras"]))

    def resolver(no):
        if isinstance(no, dict):
            if "palavra_gatilho" in no:
                no["_em"] = loc.momento(
                    no.get("palavra_gatilho"), int(no.get("ocorrencia", 1) or 1)
                )
            for valor in no.values():
                resolver(valor)
        elif isinstance(no, list):
            for valor in no:
                resolver(valor)

    for cena in plano.get("cenas") or []:
        resolver(cena)
    return plano


def mesclar(antigo, novo, refazer=()):
    """Reaplica o esqueleto preservando as cenas editadas à mão.

    Uma cena conta como editada quando seu conteúdo não bate mais com o
    `_hash` da última escrita, ou quando `editado` já estava marcado. Para
    devolver uma cena ao planejador, passe o id dela em `refazer`
    (`python editar.py plano ... --refazer-cena c01`): editar o JSON não
    serve, porque qualquer mudança no arquivo é justamente o que marca a
    cena como editada.
    """
    if not antigo:
        return novo

    refazer = set(refazer)
    antigas = antigo.get("cenas") or []
    # Casa pela fala, não pela posição. O id (`c05`) é só uma contagem: corrigir
    # uma palavra no glossário desloca todas as fronteiras, e casar por id faria
    # o texto escrito para uma fala reaparecer colado a outra, sem aviso.
    por_chave = {}
    for c in antigas:
        por_chave.setdefault(_chave(c), c)
    por_id = {c["id"]: c for c in antigas}

    usadas = set()
    cenas = []
    for proposta in novo["cenas"]:
        atual = por_chave.get(_chave(proposta))
        gatilho_mudou = False
        if atual is None or atual["id"] in usadas:
            # A fala sumiu ou já foi reaproveitada: cai no id, como antes, mas
            # marca a cena para o `validar` pedir uma conferida.
            atual = por_id.get(proposta["id"])
            gatilho_mudou = atual is not None

        if atual is None or refazer & {proposta["id"], atual["id"]}:
            cenas.append(proposta)
            continue

        usadas.add(atual["id"])
        tocada = atual.get("editado") or atual.get("_hash") != _hash(atual)
        if tocada:
            mantida = dict(atual)
            mantida["id"] = proposta["id"]       # o id segue a posição nova
            mantida["editado"] = True
            mantida["_fala"] = proposta["_fala"]
            if gatilho_mudou:
                mantida["_gatilho_mudou"] = True
            else:
                mantida.pop("_gatilho_mudou", None)
            mantida["_hash"] = _hash(mantida)
            cenas.append(mantida)
        else:
            cenas.append(proposta)

    plano = dict(novo)
    plano["cenas"] = cenas
    # Campos de topo editáveis à mão sobrevivem ao recálculo.
    for campo in ("assinatura", "enquadramento"):
        if campo in antigo:
            plano[campo] = antigo[campo]
    return plano


# ---------------------------------------------------------------- validação
def validar(plano, transcricao, legendas=None, gloss=None):
    """Devolve uma lista de ``(nivel, mensagem)``; nível é "erro" ou "aviso"."""
    achados = []
    cenas = plano.get("cenas") or []
    duracao = float(plano.get("duracao") or 0)

    if not cenas:
        return [("erro", "o plano não tem nenhuma cena")]

    # A palavra-gatilho é conferida contra a transcrição corrigida pelo
    # glossário, que é o texto que de fato aparece na tela.
    gloss = gloss or mod_glossario.carregar()
    loc = LocalizadorSimples(gloss.aplicar(transcricao["palavras"]))

    # --- abertura e fechamento (skill reels-ritmo) ---
    if cenas[0]["inicio"] > ABERTURA_MAXIMA:
        achados.append((
            "erro",
            f'abertura: a primeira cena só entra em {cenas[0]["inicio"]:.2f}s '
            f"(a skill pede até {ABERTURA_MAXIMA}s; é o gancho)",
        ))
    ultima = cenas[-1]
    if ultima.get("tipo") != "sintese":
        achados.append((
            "erro",
            f'fechamento: a última cena ({ultima["id"]}) é "{ultima.get("tipo")}", '
            "deveria ser sintese",
        ))
    if duracao - ultima["inicio"] < FECHAMENTO_MINIMO:
        achados.append((
            "aviso",
            f'fechamento: a cena-síntese dura {duracao - ultima["inicio"]:.2f}s '
            f"(a skill pede pelo menos {FECHAMENTO_MINIMO}s)",
        ))

    # --- cena a cena ---
    vistos = set()
    anterior_fim = 0.0
    for cena in cenas:
        ident = cena.get("id", "?")
        if ident in vistos:
            achados.append(("erro", f"id repetido: {ident}"))
        vistos.add(ident)

        inicio, fim = float(cena.get("inicio", 0)), float(cena.get("fim", 0))
        dur = fim - inicio

        if fim <= inicio:
            achados.append(("erro", f"{ident}: fim ({fim:.2f}s) não é depois do início ({inicio:.2f}s)"))
        elif dur < CENA_MINIMA:
            achados.append(("erro", f"{ident}: dura {dur:.2f}s (mínimo {CENA_MINIMA}s; ninguém lê)"))
        elif dur > LACUNA_MAXIMA:
            achados.append(("erro", f"{ident}: dura {dur:.2f}s sem mudança visual (máximo {LACUNA_MAXIMA}s)"))
        elif dur > CENA_ALVO_MAX:
            achados.append(("aviso", f"{ident}: dura {dur:.2f}s (a skill pede de {CENA_ALVO_MIN} a {CENA_ALVO_MAX}s)"))

        lacuna = inicio - anterior_fim
        if lacuna > 0.04:
            nivel = "erro" if lacuna > LACUNA_MAXIMA else "aviso"
            achados.append((nivel, f"{ident}: {lacuna:.2f}s de tela sem cena antes dele"))
        anterior_fim = max(anterior_fim, fim)

        # A cena foi escrita para uma fala que não está mais lá: o `mesclar` a
        # reaproveitou pela posição para não jogar fora o seu texto, mas quem
        # escreveu precisa conferir se ele ainda comenta o que está sendo dito.
        if cena.get("_gatilho_mudou"):
            achados.append((
                "aviso",
                f'{ident}: a fala-gatilho "{cena.get("palavra_gatilho")}" mudou desde que '
                "você escreveu esta cena; confira se o conteúdo ainda casa com `_fala`",
            ))

        # --- tipo e conteúdo ---
        tipo = cena.get("tipo")
        if tipo is None:
            achados.append(("erro", f"{ident}: sem tipo (cena ainda não planejada)"))
            continue
        if tipo not in CATALOGO:
            achados.append((
                "erro",
                f'{ident}: tipo "{tipo}" fora do catálogo '
                f'({", ".join(sorted(CATALOGO))})',
            ))
            continue
        conteudo = cena.get("conteudo")
        if not isinstance(conteudo, dict):
            achados.append(("erro", f"{ident}: sem conteúdo"))
            continue
        for erro in CATALOGO[tipo]["verificar"](conteudo):
            achados.append(("erro", f"{ident} ({tipo}): {erro}"))

        # --- texto: emoji, caixa alta, acentuação ---
        for texto in textos_da_cena(cena):
            if not texto:
                continue
            if EMOJI.search(str(texto)):
                achados.append(("erro", f'{ident}: emoji em "{texto}" (a skill proíbe)'))
            letras = [c for c in str(texto) if c.isalpha()]
            if len(letras) > 6 and all(c.isupper() for c in letras):
                achados.append(("aviso", f'{ident}: "{texto}" está todo em caixa alta'))

        # --- palavra-gatilho ---
        gatilho = cena.get("palavra_gatilho")
        if not gatilho:
            achados.append(("erro", f"{ident}: sem palavra_gatilho"))
        else:
            momento = loc.momento(gatilho, int(cena.get("ocorrencia", 1) or 1))
            if momento is None:
                achados.append((
                    "erro",
                    f'{ident}: a palavra-gatilho "{gatilho}" não existe na transcrição',
                ))
            elif abs(momento - inicio) > 0.4:
                achados.append((
                    "aviso",
                    f'{ident}: "{gatilho}" é falada em {momento:.2f}s mas a cena '
                    f"começa em {inicio:.2f}s",
                ))

    # --- cotas da v2 ---
    zooms = [c for c in cenas if c.get("zoom")]
    for anterior, seguinte in zip(zooms, zooms[1:]):
        intervalo = seguinte["inicio"] - anterior["inicio"]
        if intervalo < INTERVALO_ZOOM:
            achados.append((
                "aviso",
                f'zoom em {seguinte.get("id")} só {intervalo:.1f}s depois do de '
                f'{anterior.get("id")} (a skill pede {INTERVALO_ZOOM:.0f}s)',
            ))

    com_brilho = [c.get("id") for c in cenas if c.get("brilho")]
    if len(com_brilho) > CENAS_COM_BRILHO:
        achados.append((
            "erro",
            f"{len(com_brilho)} cenas com brilho metálico "
            f'({", ".join(com_brilho)}); a skill permite {CENAS_COM_BRILHO}. '
            "Se todo card brilha, nenhum brilha.",
        ))

    if legendas:
        pilulas = sum(1 for b in legendas if b.get("maxima") is not None)
        if pilulas > MAXIMAS_POR_REEL:
            achados.append((
                "erro",
                f"{pilulas} legendas em nível máxima; a skill permite "
                f"{MAXIMAS_POR_REEL}.",
            ))
        achados += _checar_repeticao(cenas, legendas)

    return achados


def _checar_repeticao(cenas, legendas):
    achados = []
    for cena in cenas:
        inicio, fim = float(cena.get("inicio", 0)), float(cena.get("fim", 0))
        faladas = set()
        for bloco in legendas:
            if bloco["fim"] > inicio and bloco["inicio"] < fim:
                # `.split()` porque uma entrada fundida pelo glossário
                # ("Black Friday Vitalícia") normaliza para três tokens.
                for p in bloco["palavras"]:
                    faladas |= set(normalizar(p["texto"]).split())
        faladas.discard("")
        for texto in textos_da_cena(cena):
            alvo = [t for t in normalizar(texto or "").split() if len(t) > 3]
            if len(alvo) >= 3 and all(t in faladas for t in alvo):
                achados.append((
                    "aviso",
                    f'{cena.get("id")}: "{texto}" repete a legenda do mesmo momento '
                    "(a skill pede escolher um dos dois)",
                ))
    return achados


class LocalizadorSimples:
    """Momento em que uma palavra foi falada, sem levantar exceção.

    Os tokens são achatados como em `roteiro.Localizador`: uma entrada que o
    glossário fundiu ("Black Friday Vitalícia") vale por três posições, senão
    nenhuma busca por ela acharia nada.
    """

    def __init__(self, palavras):
        self.palavras = palavras
        self.planos, self.indice = [], []
        for i, p in enumerate(palavras):
            for parte in normalizar(p["palavra"]).split():
                self.planos.append(parte)
                self.indice.append(i)

    def _posicoes(self, palavra):
        partes = normalizar(palavra or "").split()
        if not partes:
            return []
        n = len(partes)
        return [
            i for i in range(len(self.planos) - n + 1)
            if self.planos[i:i + n] == partes
        ]

    def momento(self, palavra, ocorrencia=1):
        posicoes = self._posicoes(palavra)
        if len(posicoes) < ocorrencia:
            return None
        return self.palavras[self.indice[posicoes[ocorrencia - 1]]]["inicio"]

    def ocorrencia_em(self, palavra, indice_palavra):
        """Qual ocorrência da palavra começa na palavra de índice dado."""
        for n, i in enumerate(self._posicoes(palavra), start=1):
            if self.indice[i] >= indice_palavra:
                return n
        return 1


# ---------------------------------------------------------------- arquivos
def dimensoes(video):
    """Largura e altura do arquivo, que a composição usa no recorte em cover."""
    try:
        saida = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(video)],
            capture_output=True, text=True, check=True,
        ).stdout.strip().split("x")
        return {"largura": int(saida[0]), "altura": int(saida[1])}
    except (subprocess.CalledProcessError, ValueError, IndexError):
        return {"largura": 1080, "altura": 1920}


def gerar_fundo(video, destino):
    """Versão pequena e já desfocada do vídeo, para o fundo vivo.

    O fundo vivo precisa do mesmo material do vídeo principal, mas borrado.
    Reaproveitar o arquivo original significava decodificá-lo duas vezes por
    frame — medido, isso era 70% do tempo de render. Aqui o ffmpeg desfoca uma
    vez só, e o arquivo resultante tem 270 px de largura: decodifica num
    piscar de olhos.
    """
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video),
         "-vf", "scale=270:-2,gblur=sigma=6", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
         "-pix_fmt", "yuv420p", str(destino)],
        check=True,
    )
    return destino


def _slug(nome):
    """Nome de arquivo seguro para URL: sem acento, sem espaço."""
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", nome)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^A-Za-z0-9._-]+", "-", sem_acento).strip("-")


def exportar_props(plano, legendas, video, destino, pasta_publica=PASTA_PUBLICA):
    """Escreve o arquivo de props do Remotion e publica o vídeo em `public/`.

    O Remotion só serve arquivos de dentro de `motion/public/`, e ao empacotar
    ele copia a pasta sem seguir link simbólico. Por isso o vídeo entra como
    link físico (custo zero no mesmo sistema de arquivos), caindo para cópia
    quando as duas pastas estão em discos diferentes. O nome é normalizado
    porque vira uma URL.
    """
    pasta_publica.mkdir(parents=True, exist_ok=True)
    nome_publico = _slug(Path(video).name)
    publicado = pasta_publica / nome_publico
    alvo = Path(video).resolve()

    ja_publicado = (
        publicado.exists()
        and not publicado.is_symlink()
        and publicado.stat().st_ino == alvo.stat().st_ino
    )
    if not ja_publicado:
        if publicado.exists() or publicado.is_symlink():
            publicado.unlink()
        try:
            os.link(alvo, publicado)
        except OSError:
            shutil.copy2(alvo, publicado)

    # Um caminho de saída só: quando havia dois, o atalho de "já publicado"
    # escrevia as props sem o vídeo de fundo e a composição renderizava sem
    # fundo nenhum.
    return _com_fundo(plano, legendas, nome_publico, pasta_publica, destino)


def _com_fundo(plano, legendas, nome_publico, pasta_publica, destino):
    """Garante o vídeo de fundo e escreve as props."""
    nome_fundo = f"{Path(nome_publico).stem}_fundo.mp4"
    fundo = pasta_publica / nome_fundo
    origem = pasta_publica / nome_publico
    if not fundo.exists() or fundo.stat().st_mtime < origem.stat().st_mtime:
        print(f"Gerando o fundo desfocado: {fundo.name}")
        gerar_fundo(origem, fundo)

    return salvar(
        {
            "plano": plano,
            "legendas": legendas,
            "video": nome_publico,
            "videoFundo": nome_fundo,
        },
        destino,
    )


def _relativo(caminho):
    p = Path(caminho).resolve()
    try:
        return p.relative_to(RAIZ).as_posix()
    except ValueError:
        return p.as_posix()


def caminhos(video):
    """Onde ficam o plano, as legendas e as props de um vídeo."""
    nome = Path(video).stem
    return (
        PASTA_PLANOS / f"{nome}.scene_plan.json",
        PASTA_PLANOS / f"{nome}.legendas.json",
        PASTA_PLANOS / f"{nome}.props.json",
    )


def carregar(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def salvar(dados, caminho):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return caminho
