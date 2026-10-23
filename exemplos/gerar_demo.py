#!/usr/bin/env python3
"""Cria um vídeo de demonstração (entrada/demo.mp4) e sua transcrição, sem precisar gravar nada.

Serve para testar a instalação: depois rode
  python editar.py renderizar roteiros/exemplo.yaml --previa
"""

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "entrada"

FALA = (
    "Hoje eu vou te mostrar três erros que travam o seu negócio. "
    "O primeiro erro é não usar inteligência artificial. "
    "O segundo é ignorar os seus dados. "
    "E o terceiro é nunca testar nada. "
    "Empresas que adotam IA crescem até trezentos por cento mais rápido. "
    "Antes você fazia tudo no braço, depois a IA faz por você. "
    "Comenta IA aqui embaixo que eu te mando o material."
)


def palavras_com_tempo():
    palavras, t = [], 0.4
    for frase in FALA.split(". "):
        for p in frase.split():
            dur = 0.18 + 0.035 * len(p)
            palavras.append({"palavra": p, "inicio": round(t, 3), "fim": round(t + dur, 3)})
            t += dur + 0.06
        palavras[-1]["palavra"] = palavras[-1]["palavra"].rstrip(".") + "."
        t += 0.45
    return palavras, t + 0.5


def pessoa(w=1080, h=1920):
    img = Image.new("RGB", (w, h), (205, 196, 184))
    d = ImageDraw.Draw(img)
    d.rectangle((0, int(h * 0.62), w, h), fill=(170, 160, 150))  # mesa/parede
    d.ellipse((w * 0.18, h * 0.5, w * 0.82, h * 1.05), fill=(40, 70, 120))  # ombros
    d.rounded_rectangle((w * 0.43, h * 0.42, w * 0.57, h * 0.55), radius=30, fill=(224, 172, 140))  # pescoço
    d.ellipse((w * 0.3, h * 0.2, w * 0.7, h * 0.47), fill=(232, 182, 150))  # rosto
    d.ellipse((w * 0.29, h * 0.17, w * 0.71, h * 0.3), fill=(60, 40, 30))  # cabelo
    for x in (0.42, 0.58):
        d.ellipse((w * x - 22, h * 0.32 - 14, w * x + 22, h * 0.32 + 14), fill=(40, 30, 30))
    d.arc((w * 0.42, h * 0.36, w * 0.58, h * 0.42), 20, 160, fill=(150, 60, 60), width=10)
    return img


def main():
    ENTRADA.mkdir(exist_ok=True)
    palavras, duracao = palavras_com_tempo()
    quadro = ENTRADA / "_demo_quadro.png"
    pessoa().save(quadro)
    video = ENTRADA / "demo.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(quadro),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{duracao:.2f}",
                    "-vf", "zoompan=z='1+0.01*sin(on/20)':d=1:s=1080x1920:fps=30", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(video)], check=True)
    quadro.unlink()

    segmentos, atual = [], []
    for p in palavras:
        atual.append(p)
        if p["palavra"].endswith("."):
            segmentos.append({"inicio": atual[0]["inicio"], "fim": atual[-1]["fim"],
                              "texto": " ".join(x["palavra"] for x in atual)})
            atual = []
    dados = {"idioma": "pt", "duracao": duracao, "segmentos": segmentos, "palavras": palavras}
    destino = RAIZ / "entrada" / "demo.transcricao.json"
    destino.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Demo criada: {video} ({duracao:.1f}s) e {destino.name}")


if __name__ == "__main__":
    main()
