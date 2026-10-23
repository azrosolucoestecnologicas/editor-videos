"""Leitura do vídeo, composição quadro a quadro e gravação do resultado com FFmpeg."""

import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image

from .compositor import Compositor


def verificar_ffmpeg():
    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            raise SystemExit(f"'{prog}' não encontrado. Instale o FFmpeg (veja o README) e tente de novo.")


def duracao_video(video):
    saida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True, check=True).stdout.strip()
    return float(saida)


def tem_audio(video):
    saida = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip()
    return bool(saida)


def _dimensoes(roteiro, previa):
    w, h = (int(v) for v in roteiro.cfg["resolucao"])
    if previa:
        w, h = w // 2, h // 2
    return w // 2 * 2, h // 2 * 2


def _filtro(w, h, fps):
    return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps}"


def renderizar(roteiro, previa=False, inicio=None, fim=None, saida=None):
    verificar_ffmpeg()
    video = roteiro.video
    w, h = _dimensoes(roteiro, previa)
    fps = int(roteiro.cfg["fps"])
    total = duracao_video(video)
    t0 = max(0.0, inicio or 0.0)
    t1 = min(total, fim) if fim else total
    duracao = t1 - t0
    if duracao <= 0:
        raise SystemExit("Intervalo de tempo vazio.")

    saida = saida or roteiro.saida
    if previa and saida == roteiro.saida:
        saida = saida.with_name(saida.stem + "_previa.mp4")
    saida.parent.mkdir(parents=True, exist_ok=True)

    compositor = Compositor(roteiro, w, h, fps)
    _resumo(compositor)

    leitor = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{duracao:.3f}", "-i", str(video),
         "-vf", _filtro(w, h, fps), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)

    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-"]
    if tem_audio(video):
        cmd += ["-ss", f"{t0:.3f}", "-t", f"{duracao:.3f}", "-i", str(video), "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast" if previa else "medium",
            "-crf", str(23 if previa else roteiro.cfg["qualidade"]), "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-shortest", str(saida)]
    gravador = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    tamanho = w * h * 3
    n_total = int(duracao * fps)
    n = 0
    comeco = time.time()
    try:
        while True:
            dados = leitor.stdout.read(tamanho)
            if len(dados) < tamanho:
                break
            t = t0 + n / fps
            frame = Image.fromarray(np.frombuffer(dados, np.uint8).reshape(h, w, 3))
            gravador.stdin.write(compositor.quadro(frame, t).tobytes())
            n += 1
            if n % fps == 0:
                pct = min(100, 100 * n / max(1, n_total))
                vel = n / max(1e-6, time.time() - comeco)
                sys.stdout.write(f"\r  Renderizando: {pct:5.1f}%  ({t - t0:5.1f}s de {duracao:.1f}s, {vel:4.1f} quadros/s)")
                sys.stdout.flush()
    finally:
        compositor.fechar()
        leitor.stdout.close()
        leitor.wait()
        gravador.stdin.close()
        gravador.wait()
    print()
    if gravador.returncode != 0:
        raise SystemExit("O FFmpeg falhou ao gravar o vídeo.")
    print(f"Pronto! Vídeo salvo em: {saida}")
    return saida


def exportar_quadro(roteiro, tempo, destino, previa=False):
    """Gera um PNG de um instante do vídeo (para conferir o visual rapidamente)."""
    verificar_ffmpeg()
    w, h = _dimensoes(roteiro, previa)
    fps = int(roteiro.cfg["fps"])
    dados = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{tempo:.3f}", "-i", str(roteiro.video), "-frames:v", "1",
         "-vf", _filtro(w, h, fps), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    frame = Image.fromarray(np.frombuffer(dados[:w * h * 3], np.uint8).reshape(h, w, 3))
    compositor = Compositor(roteiro, w, h, fps)
    try:
        compositor.quadro(frame, tempo).save(destino)
    finally:
        compositor.fechar()
    print(f"Quadro de {tempo:.2f}s salvo em {destino}")


def _resumo(compositor):
    eventos = compositor.eventos
    if not eventos:
        print("Nenhum evento no roteiro: só as legendas serão aplicadas.")
        return
    print(f"{len(eventos)} evento(s):")
    for e in eventos:
        print("  " + descrever(e))


def descrever(e):
    oque = []
    if e.animacao:
        oque.append(f"animação '{e.animacao.get('tipo', 'texto')}'")
    if e.zoom is not None:
        oque.append("zoom")
    return f"[{e.inicio:6.2f}s → {e.fim:6.2f}s] {e.layout:<9} {', '.join(oque) or '-':<24} (gatilho: {e.origem})"
