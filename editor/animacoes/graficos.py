"""Animações com números: contador, barras, progresso e ícone/emoji."""

import math

from ..texto import (colar_centralizado, cor, ease_in_out, ease_out_back, ease_out_cubic, emoji, fonte,
                     limitar, progresso)
from .base import Animacao, animacao


def formatar_numero(valor, casas):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


@animacao("contador")
class Contador(Animacao):
    """Número subindo. Parâmetros: de, ate, prefixo, sufixo, casas, legenda, duracao_contagem."""

    def desenhar(self, img, t, dur):
        de = float(self.p.get("de", 0))
        ate = float(self.p.get("ate", 100))
        tempo = float(self.p.get("duracao_contagem", min(1.6, dur * 0.6)))
        k = ease_out_cubic(progresso(t, 0.1, tempo))
        valor = de + (ate - de) * k
        casas = int(self.p.get("casas", 0))
        texto = f"{self.p.get('prefixo', '')}{formatar_numero(valor, casas)}{self.p.get('sufixo', '')}"
        topo = self.titulo(img, t)
        pulso = 1 + 0.08 * math.sin(math.pi * progresso(t, 0.1 + tempo, 0.25))
        entrada = 0.7 + 0.3 * ease_out_back(progresso(t, 0, 0.35))
        cy = self.h * (0.5 if not topo else 0.55)
        self.desenhar_texto(img, texto, (self.w / 2, cy), float(self.p.get("tamanho", 190)) * pulso * entrada,
                            alt=self.h * 0.4, c=self.c_destaque, alfa=limitar(t / 0.15))
        if self.p.get("legenda"):
            k2 = ease_out_cubic(progresso(t, 0.4, 0.4))
            self.desenhar_texto(img, self.p["legenda"], (self.w / 2, cy + self.h * 0.24), 56,
                                alt=self.h * 0.18, alfa=k2, fonte=self.fonte2)


@animacao("barras")
class Barras(Animacao):
    """Gráfico de barras que crescem. Parâmetros: titulo, barras [{rotulo, valor, cor?}], sufixo."""

    def desenhar(self, img, t, dur):
        barras = self.p.get("barras") or []
        if not barras:
            return
        topo = (self.titulo(img, t) or self.h * 0.06) + self.h * 0.06
        base = self.h * 0.84
        n = len(barras)
        maximo = max(float(b.get("valor", 0)) for b in barras) or 1
        larg_total = self.w * 0.84
        larg = larg_total / n * 0.62
        gap = larg_total / n
        d = self.draw(img)
        sufixo = self.p.get("sufixo", "")
        f_valor = fonte(self.fonte, min(64 * self.s, larg * 0.42))
        f_rotulo = fonte(self.fonte2, min(44 * self.s, larg * 0.32))
        cores_padrao = [self.c_secundaria, self.c_destaque, self.c_positivo, self.c_negativo]
        for i, b in enumerate(barras):
            k = ease_out_cubic(progresso(t, 0.2 + i * 0.25, 0.8))
            valor = float(b.get("valor", 0))
            altura = (base - topo - self.h * 0.08) * (valor / maximo) * k
            x0 = self.w * 0.08 + gap * i + (gap - larg) / 2
            c = cor(b["cor"]) if b.get("cor") else cores_padrao[i % len(cores_padrao)]
            if altura > 1:
                d.rounded_rectangle((x0, base - altura, x0 + larg, base), radius=int(min(18 * self.s, larg / 4)),
                                    fill=c)
            alfa = int(255 * limitar(k * 2))
            casas = int(self.p.get("casas", 0))
            d.text((x0 + larg / 2, base - altura - 12 * self.s), formatar_numero(valor * k, casas) + sufixo,
                   font=f_valor, fill=self.c_texto[:3] + (alfa,), anchor="md")
            d.text((x0 + larg / 2, base + 16 * self.s), str(b.get("rotulo", "")), font=f_rotulo,
                   fill=self.c_texto[:3] + (int(255 * limitar(t / 0.3)),), anchor="ma")
        d.line((self.w * 0.06, base, self.w * 0.94, base), fill=self.c_texto[:3] + (120,), width=max(1, int(3 * self.s)))


@animacao("progresso")
class Progresso(Animacao):
    """Barra de progresso enchendo até X%. Parâmetros: valor (0-100), titulo, legenda."""

    def desenhar(self, img, t, dur):
        valor = float(self.p.get("valor", 100))
        k = ease_in_out(progresso(t, 0.2, float(self.p.get("duracao_contagem", min(1.8, dur * 0.6)))))
        topo = self.titulo(img, t, y_rel=0.24)
        d = self.draw(img)
        x0, x1 = self.w * 0.1, self.w * 0.9
        cy = self.h * (0.55 if topo else 0.5)
        alt = 70 * self.s
        r = alt / 2
        d.rounded_rectangle((x0, cy - r, x1, cy + r), radius=int(r), fill=self.c_texto[:3] + (40,),
                            outline=self.c_texto[:3] + (120,), width=max(1, int(3 * self.s)))
        preenchido = (x1 - x0) * valor / 100 * k
        if preenchido > alt * 0.5:
            d.rounded_rectangle((x0, cy - r, x0 + preenchido, cy + r), radius=int(r), fill=self.c_destaque)
        f = fonte(self.fonte, 110 * self.s)
        d.text((self.w / 2, cy - r - 30 * self.s), f"{round(valor * k)}%", font=f, fill=self.c_texto, anchor="md")
        if self.p.get("legenda"):
            self.desenhar_texto(img, self.p["legenda"], (self.w / 2, cy + self.h * 0.16), 54,
                                alt=self.h * 0.15, alfa=ease_out_cubic(progresso(t, 0.5, 0.4)), fonte=self.fonte2)


ICONES = {"check", "x", "seta_cima", "seta_baixo", "alerta", "pergunta", "dinheiro"}


@animacao("icone")
class Icone(Animacao):
    """Ícone grande (ou emoji) com texto. Parâmetros: icone (check, x, seta_cima, seta_baixo, alerta,
    pergunta, dinheiro) ou emoji ('🚀'), texto, cor."""

    def desenhar(self, img, t, dur):
        k = ease_out_back(progresso(t, 0, 0.5))
        tem_texto = bool(self.p.get("texto"))
        cy = self.h * (0.38 if tem_texto else 0.5)
        r = self.h * 0.2 * k
        if self.p.get("emoji"):
            if r > 2:
                flutua = math.sin(t * 3.2) * 6 * self.s
                colar_centralizado(img, emoji(self.p["emoji"], r * 2), (self.w / 2, cy + flutua))
        else:
            self._icone(img, t, cy, r)
        if tem_texto:
            k2 = ease_out_cubic(progresso(t, 0.3, 0.4))
            self.desenhar_texto(img, self.p["texto"], (self.w / 2, self.h * 0.78 + (1 - k2) * 25 * self.s),
                                float(self.p.get("tamanho", 84)), alt=self.h * 0.3, alfa=k2)

    def _icone(self, img, t, cy, r):
        if r <= 2:
            return
        nome = self.p.get("icone", "check")
        padrao = {"check": self.c_positivo, "x": self.c_negativo, "seta_cima": self.c_positivo,
                  "seta_baixo": self.c_negativo, "alerta": self.c_destaque, "dinheiro": self.c_positivo}
        c = cor(self.p["cor"]) if self.p.get("cor") else padrao.get(nome, self.c_destaque)
        d = self.draw(img)
        cx = self.w / 2
        d.ellipse((cx - r * 1.12, cy - r * 1.12, cx + r * 1.12, cy + r * 1.12), fill=c[:3] + (60,))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
        branco = (255, 255, 255, 255)
        traco = max(3, int(r * 0.16))
        tr = ease_out_cubic(progresso(t, 0.25, 0.35))  # "desenho" do traço
        if nome == "check":
            p1, p2, p3 = (cx - r * 0.45, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.36), (cx + r * 0.5, cy - r * 0.34)
            if tr > 0:
                k1 = min(1, tr * 2)
                meio = (p1[0] + (p2[0] - p1[0]) * k1, p1[1] + (p2[1] - p1[1]) * k1)
                d.line([p1, meio], fill=branco, width=traco, joint="curve")
                if tr > 0.5:
                    k2 = (tr - 0.5) * 2
                    fim = (p2[0] + (p3[0] - p2[0]) * k2, p2[1] + (p3[1] - p2[1]) * k2)
                    d.line([p2, fim], fill=branco, width=traco, joint="curve")
        elif nome == "x":
            a = r * 0.4 * tr
            d.line((cx - a, cy - a, cx + a, cy + a), fill=branco, width=traco)
            d.line((cx - a, cy + a, cx + a, cy - a), fill=branco, width=traco)
        elif nome in ("seta_cima", "seta_baixo"):
            sinal = -1 if nome == "seta_cima" else 1
            desloc = (1 - tr) * r * 0.3 * -sinal
            ponta = (cx, cy + sinal * r * 0.55 + desloc)
            d.polygon([ponta, (cx - r * 0.4, cy + sinal * r * 0.05 + desloc), (cx + r * 0.4, cy + sinal * r * 0.05 + desloc)],
                      fill=branco)
            d.line((cx, cy + sinal * r * 0.1 + desloc, cx, cy - sinal * r * 0.5 + desloc), fill=branco, width=traco)
        else:
            simbolo = {"alerta": "!", "pergunta": "?", "dinheiro": "$"}.get(nome, str(nome)[:2])
            f = fonte(self.fonte, r * 1.2)
            d.text((cx, cy), simbolo, font=f, fill=branco, anchor="mm")
