"""Legendas dinâmicas: blocos curtos de palavras com a palavra falada em destaque."""

import re
from dataclasses import dataclass

from PIL import Image, ImageDraw

from .texto import altura_linha, cor, ease_out_back, fonte, largura, limitar

PONTUACAO_FINAL = re.compile(r"[.!?;:,…]$")


@dataclass
class Bloco:
    palavras: list  # [{'texto', 'inicio', 'fim'}]
    inicio: float
    fim: float


class Legendas:
    def __init__(self, palavras, cfg, tema, escala, largura_tela, caminho_fonte):
        self.cfg = cfg
        self.escala = escala
        self.largura_max = largura_tela * 0.86
        self.caminho_fonte = caminho_fonte
        self.cor_texto = cor(tema["texto"])
        self.cor_destaque = cor(tema["destaque"])
        self.tamanho = cfg["tamanho"] * escala
        self.contorno = max(2, int(round(7 * escala)))
        self.blocos = self._montar_blocos(palavras)
        self._cache = {}
        self._ultimo = 0

    # ------------------------------------------------------------ blocos
    def _texto(self, palavra):
        bruto = palavra["palavra"].strip()
        subs = self.cfg.get("substituicoes") or {}
        limpo = re.sub(r"^[\"'“”(]+|[\"'“”)]+$", "", bruto)
        for de, para in subs.items():
            if limpo.lower().strip(".,!?;:") == str(de).lower():
                limpo = str(para)
        if self.cfg.get("remover_pontuacao", True):
            limpo = re.sub(r"[.,;:…]+$", "", limpo)
        return limpo.upper() if self.cfg.get("maiusculas", True) else limpo

    def _montar_blocos(self, palavras):
        max_pal = int(self.cfg.get("palavras_por_bloco", 3))
        max_car = int(self.cfg.get("max_caracteres", 20))
        blocos, atual = [], []

        def fechar():
            if atual:
                blocos.append(Bloco(list(atual), atual[0]["inicio"], atual[-1]["fim"]))
                atual.clear()

        anterior = None
        for p in palavras:
            texto = self._texto(p)
            if not texto:
                continue
            pausa = anterior is not None and p["inicio"] - anterior["fim"] > 0.45
            chars = sum(len(w["texto"]) + 1 for w in atual) + len(texto)
            if atual and (len(atual) >= max_pal or chars > max_car or pausa):
                fechar()
            atual.append({"texto": texto, "inicio": p["inicio"], "fim": p["fim"]})
            if PONTUACAO_FINAL.search(p["palavra"].strip()):
                fechar()
            anterior = p
        fechar()

        # Cada bloco fica na tela até o próximo começar (se a pausa for curta).
        for i, b in enumerate(blocos):
            prox = blocos[i + 1].inicio if i + 1 < len(blocos) else None
            fim = b.fim + 0.35
            if prox is not None:
                fim = prox if prox - b.fim < 0.6 else min(fim, prox)
            b.fim = fim
        return blocos

    def bloco_em(self, t):
        # Busca incremental (os quadros chegam em ordem), com recuo se necessário.
        if self._ultimo >= len(self.blocos) or (self.blocos and self.blocos[self._ultimo].inicio > t):
            self._ultimo = 0
        for i in range(self._ultimo, len(self.blocos)):
            b = self.blocos[i]
            if b.inicio > t:
                break
            if b.inicio <= t < b.fim:
                self._ultimo = i
                return i, b
        return None, None

    # ------------------------------------------------------------ desenho
    def imagem(self, t):
        """Retorna (imagem RGBA, alfa) da legenda no tempo t, ou (None, 0)."""
        i, b = self.bloco_em(t)
        if b is None:
            return None, 0
        ativa = 0
        for j, p in enumerate(b.palavras):
            if p["inicio"] <= t + 0.02:
                ativa = j
        pop = ease_out_back(limitar((t - b.inicio) / 0.14))
        escala_pop = round(0.82 + 0.18 * pop, 2)
        chave = (i, ativa, escala_pop)
        if chave not in self._cache:
            if len(self._cache) > 300:
                self._cache.clear()
            self._cache[chave] = self._desenhar(b, ativa, escala_pop)
        return self._cache[chave], limitar((t - b.inicio) / 0.06)

    def _linhas(self, palavras, f):
        espaco = largura(" ", f) or f.size * 0.28
        linhas, atual, w_atual = [], [], 0
        for j, p in enumerate(palavras):
            w = largura(p["texto"], f)
            extra = w if not atual else w_atual + espaco + w
            if atual and extra > self.largura_max:
                linhas.append((atual, w_atual))
                atual, w_atual = [], 0
                extra = w
            atual.append((j, p["texto"], w))
            w_atual = extra
        if atual:
            linhas.append((atual, w_atual))
        return linhas, espaco

    def _desenhar(self, bloco, ativa, escala_pop):
        estilo = self.cfg.get("estilo", "destaque")
        f = fonte(self.caminho_fonte, self.tamanho * escala_pop)
        linhas, espaco = self._linhas(bloco.palavras, f)
        lh = altura_linha(f) * 1.02
        pad = self.contorno * 3 + int(18 * self.escala)
        w = int(max(l[1] for l in linhas) + pad * 2)
        h = int(lh * len(linhas) + pad * 2)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        y = pad
        for itens, w_linha in linhas:
            x = (w - w_linha) / 2
            for j, texto, wp in itens:
                destaque = j == ativa
                cor_txt = self.cor_texto
                if estilo == "destaque" and destaque:
                    cor_txt = self.cor_destaque
                if estilo == "caixa" and destaque:
                    m = int(10 * self.escala)
                    x0, y0, x1, y1 = d.textbbox((x, y), texto, font=f)
                    d.rounded_rectangle((x0 - m, y0 - m, x1 + m, y1 + m), radius=int(14 * self.escala),
                                        fill=self.cor_destaque)
                    cor_txt = (15, 15, 15, 255)
                em_caixa = estilo == "caixa" and destaque
                if not em_caixa:
                    sombra = int(5 * self.escala)
                    d.text((x + sombra, y + sombra), texto, font=f, fill=(0, 0, 0, 110),
                           stroke_width=self.contorno, stroke_fill=(0, 0, 0, 110))
                contorno = 0 if em_caixa else self.contorno
                d.text((x, y), texto, font=f, fill=cor_txt, stroke_width=contorno, stroke_fill=(0, 0, 0, 255))
                x += wp + espaco
            y += lh
        return img
