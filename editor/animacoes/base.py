"""Classe base das animações que aparecem na área de cima (tela dividida)."""

from PIL import ImageDraw

from ..texto import FONTE_PADRAO, FONTE_SECUNDARIA, cor, desenhar_texto, ease_out_cubic, progresso

REGISTRO = {}


def animacao(nome):
    def registrar(cls):
        REGISTRO[nome] = cls
        cls.nome = nome
        return cls
    return registrar


class Animacao:
    """Cada animação recebe os parâmetros do roteiro e desenha num painel RGBA transparente.

    t é o tempo (s) desde o início do evento e dur a duração total do evento.
    """

    nome = "base"

    def __init__(self, params, tema, escala, roteiro, tamanho):
        self.p = params
        self.tema = tema
        self.s = escala
        self.roteiro = roteiro
        self.w, self.h = tamanho
        self.fonte = tema.get("_fonte") or FONTE_PADRAO
        self.fonte2 = FONTE_SECUNDARIA
        self.c_texto = cor(params.get("cor") or tema["texto"])
        self.c_destaque = cor(params.get("cor_destaque") or tema["destaque"])
        self.c_secundaria = cor(tema["secundaria"])
        self.c_positivo = cor(tema["positivo"])
        self.c_negativo = cor(tema["negativo"])

    # helpers ----------------------------------------------------------
    def titulo(self, img, t, texto=None, y_rel=0.14, tamanho=80, atraso=0.0):
        texto = texto if texto is not None else self.p.get("titulo")
        if not texto:
            return 0
        k = ease_out_cubic(progresso(t, atraso, 0.35))
        desenhar_texto(img, texto, (self.w / 2, self.h * y_rel - (1 - k) * 30 * self.s), self.fonte,
                       tamanho * self.s, self.w * 0.86, self.h * 0.2,
                       cor_texto=self.c_destaque[:3] + (int(255 * k),))
        return self.h * (y_rel + 0.1)

    def desenhar_texto(self, img, texto, centro, tamanho, larg=None, alt=None, c=None, alfa=1.0, fonte=None):
        c = c or self.c_texto
        desenhar_texto(img, texto, centro, fonte or self.fonte, tamanho * self.s, larg or self.w * 0.86,
                       alt or self.h * 0.3, cor_texto=c[:3] + (int(c[3] * alfa),))

    def draw(self, img):
        return ImageDraw.Draw(img)

    def desenhar(self, img, t, dur):
        raise NotImplementedError

    def fechar(self):
        pass
