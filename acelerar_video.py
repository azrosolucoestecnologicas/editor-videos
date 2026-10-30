#!/usr/bin/env python3
"""Acelera um vídeo mantendo a qualidade do áudio e sincronização."""

import subprocess
import sys
from pathlib import Path

def acelerar_video(entrada, saida, velocidade=1.4):
    """Acelera um vídeo usando FFmpeg com filtro de velocidade suave."""
    entrada = Path(entrada)
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)

    if not entrada.exists():
        raise SystemExit(f"Arquivo não encontrado: {entrada}")

    # Filtro para acelerar sem ficar robótico
    # setpts reduz o tempo de cada frame, atempo acelera o áudio proporcionalmente
    filtro_video = f"setpts=PTS/{velocidade}"
    filtro_audio = f"atempo={velocidade}"

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(entrada),
        "-vf", filtro_video,
        "-af", filtro_audio,
        "-c:v", "libx264", "-preset", "fast",
        "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(saida)
    ]

    print(f"Acelerando {entrada.name} → {saida.name} ({velocidade}x)...")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"✓ Pronto! Vídeo acelerado: {saida}")
        return saida
    else:
        raise SystemExit("FFmpeg falhou ao acelerar o vídeo.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <entrada.mp4> [saida.mp4] [velocidade]")
        print(f"Ex.: {sys.argv[0]} saida/meu_video.mp4 saida/meu_video_rapido.mp4 1.4")
        sys.exit(1)

    entrada = sys.argv[1]
    velocidade = float(sys.argv[3]) if len(sys.argv) > 3 else 1.4
    saida = sys.argv[2] if len(sys.argv) > 2 else str(Path(entrada).stem) + "_acelado.mp4"

    acelerar_video(entrada, saida, velocidade)
