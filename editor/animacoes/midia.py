"""Animações com arquivos: imagem (com zoom suave) e vídeo de apoio (b-roll)."""

import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from ..texto import ease_out_cubic, progresso
from .base import Animacao, animacao


def _cantos_arredondados(img, raio):
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=raio, fill=255)
    img.putalpha(mascara)
    return img


class _Midia(Animacao):
    def area(self):
        """Retângulo onde a mídia fica (com margem, ou ocupando tudo se 'tela_cheia: true')."""
        if self.p.get("preencher", False):
            return 0, 0, self.w, self.h
        margem = int(self.w * 0.05)
        topo = int(self.h * 0.2) if self.p.get("titulo") else margem
        return margem, topo, self.w - margem, self.h - margem

    def compor(self, img, t, quadro):
        x0, y0, x1, y1 = self.area()
        k = ease_out_cubic(progresso(t, 0, 0.35))
        if not self.p.get("preencher", False):
            quadro = _cantos_arredondados(quadro.convert("RGBA"), int(28 * self.s))
        else:
            quadro = quadro.convert("RGBA")
        if k < 1:
            quadro.putalpha(quadro.getchannel("A").point(lambda v: int(v * k)))
        img.alpha_composite(quadro, (x0, int(y0 + (1 - k) * 30 * self.s)))
        self.titulo(img, t, y_rel=0.1)


@animacao("imagem")
class Imagem(_Midia):
    """Mostra uma imagem com zoom lento. Parâmetros: arquivo, titulo, zoom (padrão 1.08), preencher."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        x0, y0, x1, y1 = self.area()
        self.tamanho = (x1 - x0, y1 - y0)
        original = Image.open(self.roteiro.arquivo(self.p["arquivo"]))
        original = ImageOps.exif_transpose(original).convert("RGBA")
        zoom = float(self.p.get("zoom", 1.08))
        alvo = (int(self.tamanho[0] * zoom) + 2, int(self.tamanho[1] * zoom) + 2)
        self.grande = ImageOps.fit(original, alvo, Image.LANCZOS)
        self.zoom = zoom

    def desenhar(self, img, t, dur):
        k = progresso(t, 0, dur)
        z = 1 + (self.zoom - 1) * k  # Ken Burns: aproxima devagar
        w, h = self.tamanho
        cw, ch = self.grande.width / z, self.grande.height / z
        cx, cy = self.grande.width / 2, self.grande.height / 2
        quadro = self.grande.resize((w, h), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
        self.compor(img, t, quadro)


@animacao("video")
class VideoApoio(_Midia):
    """Toca outro vídeo (b-roll, gravação de tela) no painel. Parâmetros: arquivo, inicio_arquivo, titulo."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        x0, y0, x1, y1 = self.area()
        self.tamanho = ((x1 - x0) // 2 * 2, (y1 - y0) // 2 * 2)
        self.arquivo = self.roteiro.arquivo(self.p["arquivo"])
        self.fps = self.p.get("_fps", 30)
        self.proc = None
        self.proximo = None
        self.ultimo = Image.new("RGB", self.tamanho, (0, 0, 0))

    def _abrir(self, t):
        self.fechar()
        w, h = self.tamanho
        inicio = float(self.p.get("inicio_arquivo", 0)) + t
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{inicio:.3f}", "-i", str(self.arquivo), "-an",
               "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={self.fps}",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.proximo = round(t * self.fps)

    def desenhar(self, img, t, dur):
        indice = round(t * self.fps)
        if self.proc is None or indice != self.proximo:
            self._abrir(t)
        w, h = self.tamanho
        dados = self.proc.stdout.read(w * h * 3)
        if len(dados) == w * h * 3:
            self.ultimo = Image.fromarray(np.frombuffer(dados, np.uint8).reshape(h, w, 3))
        self.proximo = indice + 1
        self.compor(img, t, self.ultimo.copy())

    def fechar(self):
        if self.proc:
            self.proc.kill()
            self.proc.wait()
            self.proc = None
