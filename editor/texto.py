"""Utilitários de texto, fontes, cores e easing usados pelas legendas e animações."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FONTE_PADRAO = RAIZ / "fontes" / "Inter-Black.otf"
FONTE_SECUNDARIA = RAIZ / "fontes" / "Inter-Bold.otf"
FONTE_EMOJI = RAIZ / "fontes" / "NotoColorEmoji.ttf"


# ---------------------------------------------------------------- cores

def cor(valor, alfa=255):
    """Converte '#rrggbb', '#rgb' ou [r, g, b] em tupla RGBA."""
    if isinstance(valor, (list, tuple)):
        r, g, b = valor[:3]
        return (int(r), int(g), int(b), alfa)
    v = str(valor).lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16), alfa)


def com_alfa(rgba, fator):
    return rgba[:3] + (int(rgba[3] * max(0.0, min(1.0, fator))),)


# ---------------------------------------------------------------- easing

def limitar(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def progresso(t, inicio, duracao):
    if duracao <= 0:
        return 1.0 if t >= inicio else 0.0
    return limitar((t - inicio) / duracao)


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


def ease_out_back(x, s=1.70158):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, k):
    return a + (b - a) * k


# ---------------------------------------------------------------- fontes

@lru_cache(maxsize=512)
def fonte(caminho, tamanho):
    return ImageFont.truetype(str(caminho), max(4, int(round(tamanho))))


def largura(texto, f):
    if not texto:
        return 0
    x0, _, x1, _ = f.getbbox(texto)
    return x1 - x0


def altura_linha(f):
    ascent, descent = f.getmetrics()
    return ascent + descent


def quebrar_linhas(texto, f, largura_max):
    """Quebra o texto em linhas (por palavras) que caibam em largura_max."""
    linhas = []
    for paragrafo in str(texto).split("\n"):
        atual = ""
        for palavra in paragrafo.split():
            teste = f"{atual} {palavra}".strip()
            if not atual or largura(teste, f) <= largura_max:
                atual = teste
            else:
                linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return linhas


def ajustar_texto(texto, caminho, largura_max, altura_max, tamanho_max, tamanho_min=18, entrelinha=1.05):
    """Encontra o maior tamanho de fonte em que o texto cabe na caixa."""
    tamanho = int(tamanho_max)
    while True:
        f = fonte(caminho, tamanho)
        linhas = quebrar_linhas(texto, f, largura_max)
        alt = altura_linha(f) * entrelinha * len(linhas)
        larg = max((largura(l, f) for l in linhas), default=0)
        if (alt <= altura_max and larg <= largura_max) or tamanho <= tamanho_min:
            return f, linhas
        tamanho = max(tamanho_min, int(tamanho * 0.92))


def desenhar_texto(img, texto, centro, caminho, tamanho_max, largura_max, altura_max=None,
                   cor_texto=(255, 255, 255, 255), contorno=0, cor_contorno=(0, 0, 0, 255),
                   sombra=0, entrelinha=1.05, alinhar="centro"):
    """Desenha texto com quebra automática, centralizado em `centro` (x, y)."""
    if not texto:
        return
    altura_max = altura_max or img.height
    f, linhas = ajustar_texto(texto, caminho, largura_max, altura_max, tamanho_max, entrelinha=entrelinha)
    d = ImageDraw.Draw(img)
    lh = altura_linha(f) * entrelinha
    total = lh * len(linhas)
    cx, cy = centro
    y = cy - total / 2
    for linha in linhas:
        w = largura(linha, f)
        x = cx - w / 2 if alinhar == "centro" else cx
        if sombra:
            d.text((x + sombra, y + sombra), linha, font=f, fill=(0, 0, 0, int(cor_texto[3] * 0.5)),
                   stroke_width=contorno, stroke_fill=(0, 0, 0, int(cor_texto[3] * 0.5)))
        d.text((x, y), linha, font=f, fill=cor_texto, stroke_width=contorno, stroke_fill=cor_contorno)
        y += lh


@lru_cache(maxsize=64)
def _emoji_base(caractere):
    f = ImageFont.truetype(str(FONTE_EMOJI), 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((80, 80), caractere, font=f, embedded_color=True, anchor="mm")
    caixa = img.getbbox()
    return img.crop(caixa) if caixa else img


def emoji(caractere, tamanho):
    """Imagem RGBA de um emoji colorido com a altura pedida."""
    base = _emoji_base(caractere)
    escala = tamanho / max(base.height, 1)
    return base.resize((max(1, int(base.width * escala)), max(1, int(tamanho))), Image.LANCZOS)


def colar_centralizado(destino, imagem, centro, alfa=1.0):
    if alfa < 1.0:
        imagem = imagem.copy()
        imagem.putalpha(imagem.getchannel("A").point(lambda v: int(v * alfa)))
    x = int(round(centro[0] - imagem.width / 2))
    y = int(round(centro[1] - imagem.height / 2))
    destino.alpha_composite(imagem, (x, y)) if _dentro(destino, imagem, x, y) else destino.paste(imagem, (x, y), imagem)


def _dentro(destino, imagem, x, y):
    return x >= 0 and y >= 0 and x + imagem.width <= destino.width and y + imagem.height <= destino.height


def gradiente_vertical(tamanho, cor_topo, cor_base):
    w, h = tamanho
    topo = Image.new("RGBA", (w, h), cor(cor_topo))
    base = Image.new("RGBA", (w, h), cor(cor_base))
    mascara = Image.linear_gradient("L").resize((w, h))
    return Image.composite(base, topo, mascara)
