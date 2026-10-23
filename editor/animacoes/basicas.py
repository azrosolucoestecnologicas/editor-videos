"""Animações de texto: frase de impacto, digitação, lista, passos e comparação."""

import math

from PIL import Image

from ..texto import (altura_linha, colar_centralizado, desenhar_texto, ease_out_back, ease_out_cubic, emoji,
                     fonte, largura, limitar, progresso, quebrar_linhas)
from .base import Animacao, animacao


@animacao("texto")
class TextoImpacto(Animacao):
    """Frase grande que entra com 'pop'. Parâmetros: texto, subtitulo, emoji, tamanho."""

    def desenhar(self, img, t, dur):
        texto = self.p.get("texto", "")
        sub = self.p.get("subtitulo")
        ic = self.p.get("emoji")
        k = ease_out_back(progresso(t, 0, 0.45))
        escala = 0.6 + 0.4 * k
        cy = self.h * (0.42 if sub else 0.5)
        if ic:
            tam = self.h * 0.2 * ease_out_back(progresso(t, 0.1, 0.5))
            if tam > 2:
                balanço = math.sin(t * 3) * 4 * self.s
                colar_centralizado(img, emoji(ic, tam), (self.w / 2, self.h * 0.2 + balanço))
            cy = self.h * 0.55
        tamanho = float(self.p.get("tamanho", 130)) * escala
        self.desenhar_texto(img, texto, (self.w / 2, cy), tamanho, alt=self.h * 0.45,
                            c=self.c_destaque if self.p.get("destacar", True) else self.c_texto,
                            alfa=limitar(t / 0.15))
        if sub:
            k2 = ease_out_cubic(progresso(t, 0.35, 0.4))
            self.desenhar_texto(img, sub, (self.w / 2, cy + self.h * 0.26 + (1 - k2) * 20 * self.s), 60,
                                alt=self.h * 0.2, alfa=k2, fonte=self.fonte2)


@animacao("digitando")
class Digitando(Animacao):
    """Texto que aparece letra por letra. Parâmetros: texto, velocidade (letras/s), titulo."""

    def desenhar(self, img, t, dur):
        texto = self.p.get("texto", "")
        vel = float(self.p.get("velocidade", 0) or max(12.0, len(texto) / max(0.5, dur * 0.6)))
        n = int(t * vel)
        topo = self.titulo(img, t) or 0
        parcial = texto[:n]
        cursor = "|" if (n < len(texto) or int(t * 2) % 2 == 0) else ""
        f = fonte(self.fonte, float(self.p.get("tamanho", 80)) * self.s)
        linhas = quebrar_linhas(texto, f, self.w * 0.84)
        # Quebra fixa pelo texto completo para as linhas não "pularem" enquanto digita.
        lh = altura_linha(f) * 1.1
        y = max(topo, (self.h - lh * len(linhas)) / 2)
        d = self.draw(img)
        restante = parcial
        for linha in linhas:
            pedaco = restante[:len(linha)]
            restante = restante[len(linha):].lstrip(" ")
            x = (self.w - largura(linha, f)) / 2
            d.text((x, y), pedaco, font=f, fill=self.c_texto)
            if cursor and (len(pedaco) < len(linha) or not restante):
                d.text((x + largura(pedaco, f), y), cursor, font=f, fill=self.c_destaque)
                cursor = ""
            y += lh


def _normalizar_itens(itens):
    res = []
    for it in itens or []:
        if isinstance(it, dict):
            res.append({"texto": str(it.get("texto", "")), "emoji": it.get("emoji"), "_t": it.get("_t")})
        else:
            res.append({"texto": str(it), "emoji": None, "_t": None})
    return res


@animacao("lista")
class Lista(Animacao):
    """Título + itens que aparecem um a um.

    Parâmetros: titulo, itens (texto ou {texto, quando/em, emoji}), numerada (bool), marcador ('check'|'ponto').
    """

    def tempos(self, itens, dur):
        n = len(itens)
        passo = (dur * 0.7) / max(1, n)
        inicio = 0.35 if self.p.get("titulo") else 0.1
        return [it["_t"] if it["_t"] is not None else inicio + i * passo for i, it in enumerate(itens)]

    def desenhar(self, img, t, dur):
        itens = _normalizar_itens(self.p.get("itens"))
        if not itens:
            return
        topo = self.titulo(img, t) or self.h * 0.08
        tempos = self.tempos(itens, dur)
        area = self.h - topo - self.h * 0.06
        altura_item = min(area / len(itens), self.h * 0.2)
        y0 = topo + (area - altura_item * len(itens)) / 2
        x_texto = self.w * 0.22
        numerada = self.p.get("numerada", False)
        marcador = self.p.get("marcador", "check")
        d = self.draw(img)
        tam = float(self.p.get("tamanho", 66))
        for i, (it, ti) in enumerate(zip(itens, tempos)):
            k = ease_out_cubic(progresso(t, ti, 0.35))
            if k <= 0:
                continue
            cy = y0 + altura_item * (i + 0.5)
            dx = (1 - k) * 80 * self.s
            r = min(altura_item * 0.32, 46 * self.s) * ease_out_back(progresso(t, ti, 0.4))
            cx = self.w * 0.12 + dx
            if it["emoji"]:
                if r > 1:
                    colar_centralizado(img, emoji(it["emoji"], r * 2.2), (cx, cy))
            elif r > 1:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=self.c_destaque)
                if numerada:
                    f = fonte(self.fonte, r * 1.2)
                    d.text((cx, cy), str(i + 1), font=f, fill=(15, 15, 15, 255), anchor="mm")
                elif marcador == "check":
                    pts = [(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.35), (cx + r * 0.5, cy - r * 0.35)]
                    d.line(pts, fill=(15, 15, 15, 255), width=max(2, int(r * 0.22)), joint="curve")
            caixa = Image.new("RGBA", (int(self.w * 0.74), int(altura_item)), (0, 0, 0, 0))
            desenhar_texto(caixa, it["texto"], (0, caixa.height / 2), self.fonte, tam * self.s,
                           caixa.width, caixa.height * 0.9, cor_texto=self.c_texto[:3] + (int(255 * k),),
                           alinhar="esquerda")
            img.alpha_composite(caixa, (int(x_texto + dx), int(cy - caixa.height / 2)))


@animacao("passos")
class Passos(Lista):
    """Igual à lista, mas numerada (1, 2, 3...)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.p.setdefault("numerada", True)


@animacao("comparacao")
class Comparacao(Animacao):
    """Duas colunas lado a lado. Parâmetros: esquerda {titulo, itens}, direita {titulo, itens}, titulo."""

    def desenhar(self, img, t, dur):
        topo = self.titulo(img, t) or self.h * 0.06
        d = self.draw(img)
        lados = [("esquerda", self.c_negativo, "x"), ("direita", self.c_positivo, "check")]
        larg_col = self.w * 0.43
        for idx, (lado, c, simbolo) in enumerate(lados):
            dados = self.p.get(lado) or {}
            atraso = 0.2 + idx * 0.5
            k = ease_out_cubic(progresso(t, atraso, 0.4))
            if k <= 0:
                continue
            itens = _normalizar_itens(dados.get("itens"))
            x0 = self.w * 0.05 + idx * (larg_col + self.w * 0.04)
            alt_item = self.h * 0.15
            cabecalho = self.h * 0.17
            alt_coluna = min(self.h * 0.95 - topo, cabecalho + alt_item * len(itens) + self.h * 0.04)
            y0 = topo + (self.h * 0.95 - topo - alt_coluna) / 2 + (1 - k) * 40 * self.s
            y1 = y0 + alt_coluna
            fundo = c[:3] + (int(45 * k),)
            d.rounded_rectangle((x0, y0, x0 + larg_col, y1), radius=int(28 * self.s), fill=fundo,
                                outline=c[:3] + (int(255 * k),), width=max(2, int(4 * self.s)))
            self.desenhar_texto(img, dados.get("titulo", ""), (x0 + larg_col / 2, y0 + cabecalho / 2), 70,
                                larg=larg_col * 0.85, alt=cabecalho * 0.8, c=c, alfa=k)
            area_y = y0 + cabecalho
            alt_item = min(alt_item, (y1 - area_y - self.h * 0.02) / max(1, len(itens)))
            for j, it in enumerate(itens):
                kj = ease_out_cubic(progresso(t, atraso + 0.3 + j * 0.25, 0.3))
                if kj <= 0:
                    continue
                cy = area_y + alt_item * (j + 0.5)
                r = 20 * self.s
                cx = x0 + larg_col * 0.12
                cc = c[:3] + (int(255 * kj),)
                largura_traco = max(3, int(8 * self.s))
                if simbolo == "x":
                    d.line((cx - r, cy - r, cx + r, cy + r), fill=cc, width=largura_traco)
                    d.line((cx - r, cy + r, cx + r, cy - r), fill=cc, width=largura_traco)
                else:
                    d.line([(cx - r, cy), (cx - r * 0.2, cy + r * 0.8), (cx + r, cy - r * 0.8)], fill=cc,
                           width=largura_traco, joint="curve")
                caixa = Image.new("RGBA", (int(larg_col * 0.72), int(alt_item)), (0, 0, 0, 0))
                desenhar_texto(caixa, it["texto"], (0, caixa.height / 2), self.fonte2, 52 * self.s,
                               caixa.width, caixa.height * 0.92, cor_texto=self.c_texto[:3] + (int(255 * kj),),
                               alinhar="esquerda")
                img.alpha_composite(caixa, (int(x0 + larg_col * 0.22), int(cy - caixa.height / 2)))
