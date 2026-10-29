"""Correções de termos da transcrição (skill `reels-legendas`).

O arquivo `glossario.json` na raiz do projeto é a fonte única das correções.
Elas valem para a GRAFIA das legendas, nunca para o conteúdo do que foi dito:
se o Thiago errou um número na fala, o glossário não conserta — isso é
sinalizado para ele.

Este módulo é usado na exportação das legendas para o Remotion. O caminho
antigo em Pillow (`editor/legendas.py`) continua intocado, para não mudar o
comportamento dos comandos já existentes de `editar.py`.
"""

import json
import re
from pathlib import Path

from .roteiro import normalizar

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_PADRAO = RAIZ / "glossario.json"

# Pontuação que fica grudada na palavra e precisa sobreviver à substituição.
PONTUACAO_FINAL = re.compile(r"[.,;:!?…]+$")


class Glossario:
    def __init__(self, dados=None):
        dados = dados or {}
        self.palavras = {
            normalizar(de): para for de, para in (dados.get("palavras") or {}).items()
        }
        # As expressões mais longas são testadas primeiro, senão "sumula 331"
        # nunca venceria uma entrada de uma palavra só.
        expressoes = []
        for item in dados.get("expressoes") or []:
            tokens = normalizar(item["de"]).split()
            if tokens:
                expressoes.append((tokens, item["para"]))
        self.expressoes = sorted(expressoes, key=lambda e: -len(e[0]))
        self.muletas = {}
        for item in dados.get("muletas") or []:
            chave = normalizar(item["palavra"])
            if chave:
                self.muletas[chave] = [
                    normalizar(p) for p in item.get("nao_remover_antes_de") or []
                ]

    @property
    def vazio(self):
        return not (self.palavras or self.expressoes or self.muletas)

    # ------------------------------------------------------------ aplicação
    def aplicar(self, palavras):
        """Corrige uma lista de ``{"palavra", "inicio", "fim"}``.

        Devolve uma nova lista: expressões viram uma entrada só (do início da
        primeira palavra ao fim da última) e muletas somem. Os tempos das
        palavras que sobram não mudam.
        """
        tokens = [normalizar(p["palavra"]) for p in palavras]
        saida = []
        i = 0
        while i < len(palavras):
            consumidas, texto = self._expressao(tokens, i)
            if consumidas:
                saida.append({
                    "palavra": texto,
                    "inicio": palavras[i]["inicio"],
                    "fim": palavras[i + consumidas - 1]["fim"],
                })
                i += consumidas
                continue

            if self._e_muleta(tokens, i):
                i += 1
                continue

            saida.append({**palavras[i], "palavra": self._palavra(palavras[i], tokens[i])})
            i += 1
        return saida

    def _expressao(self, tokens, i):
        for alvo, para in self.expressoes:
            n = len(alvo)
            if tokens[i:i + n] == alvo:
                return n, para
        return 0, None

    def _e_muleta(self, tokens, i):
        bloqueios = self.muletas.get(tokens[i])
        if bloqueios is None:
            return False
        if bloqueios and i + 1 < len(tokens) and tokens[i + 1] in bloqueios:
            return False
        return True

    def _palavra(self, original, token):
        correta = self.palavras.get(token)
        if correta is None:
            return original["palavra"]
        # "rag." precisa virar "RAG.", não "RAG".
        sufixo = PONTUACAO_FINAL.search(original["palavra"].strip())
        return correta + (sufixo.group(0) if sufixo else "")


def carregar(caminho=None):
    """Lê o glossário. Se o arquivo não existir, devolve um glossário vazio."""
    arquivo = Path(caminho) if caminho else CAMINHO_PADRAO
    if not arquivo.exists():
        return Glossario()
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    return Glossario(dados)
