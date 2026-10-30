"""Cortes automáticos: remove pausas longas e muletas usando o tempo de cada palavra.

Gera um vídeo cortado e a transcrição com os tempos já ajustados ao novo vídeo,
sem precisar transcrever de novo.
"""

import json
import subprocess
from pathlib import Path

from . import ffmpeg, transcricao
from .texto_util import normalizar

MULETAS_PADRAO = ["hã", "ãh", "ahn", "hum", "hmm", "humm", "éé", "ééé", "eee", "aham"]


def planejar(palavras, duracao, pausa_max=0.35, margem=0.08, fps=30, muletas=None):
    """Devolve (trechos mantidos [(ini, fim)], palavras mantidas)."""
    muletas = {normalizar(m) for m in (MULETAS_PADRAO if muletas is None else muletas)}
    mantidas = [p for p in palavras if normalizar(p["palavra"]) not in muletas]
    trechos = []
    anterior = None
    for p in mantidas:
        ini, fim = max(0.0, p["inicio"] - margem), min(duracao, p["fim"] + margem)
        continua = anterior is not None and p["inicio"] - anterior["fim"] <= pausa_max
        if trechos and (continua or ini <= trechos[-1][1]):
            trechos[-1][1] = max(trechos[-1][1], fim)
        else:
            trechos.append([ini, fim])
        anterior = p
    # Alinha aos quadros para áudio e vídeo cortarem exatamente no mesmo ponto.
    alinhados = []
    for ini, fim in trechos:
        a, b = round(ini * fps) / fps, round(fim * fps) / fps
        if b > a:
            alinhados.append((a, b))
    return alinhados, mantidas


def remapear(t, trechos):
    """Converte um tempo do vídeo original para o tempo do vídeo cortado."""
    deslocamento = 0.0
    for ini, fim in trechos:
        if t < ini:
            return deslocamento
        if t <= fim:
            return deslocamento + (t - ini)
        deslocamento += fim - ini
    return deslocamento


def cortar(video, pausa_max=0.35, margem=0.08, fps=30, muletas=None, destino=None, modelo="small"):
    video = Path(video)
    arq_trans = transcricao.caminho_transcricao(video)
    if not arq_trans.exists():
        transcricao.transcrever(video, modelo=modelo, destino=arq_trans)
    dados = transcricao.carregar(arq_trans)
    duracao = ffmpeg.duracao(video)

    trechos, mantidas = planejar(dados["palavras"], duracao, pausa_max, margem, fps, muletas)
    if not trechos:
        raise SystemExit("Nenhuma fala encontrada na transcrição; nada para cortar.")

    destino = Path(destino) if destino else video.with_name(video.stem + "_cortado.mp4")
    expr = "+".join(f"between(t,{a - 0.0005:.4f},{b - 0.0005:.4f})" for a, b in trechos)
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(video),
           "-vf", f"fps={fps},select='{expr}',setpts=N/{fps}/TB",
           "-af", f"asetnsamples=n=48:p=0,aselect='{expr}',asetpts=N/SR/TB",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(destino)]
    print(f"Cortando {video.name}: {len(trechos)} trecho(s) mantido(s)...")
    subprocess.run(cmd, check=True)

    novas = [{"palavra": p["palavra"], "inicio": round(remapear(p["inicio"], trechos), 3),
              "fim": round(remapear(p["fim"], trechos), 3)} for p in mantidas]
    segmentos = []
    for s in dados["segmentos"]:
        dentro = [p for p, orig in zip(novas, mantidas) if s["inicio"] - 0.01 <= orig["inicio"] <= s["fim"] + 0.01]
        if dentro:
            segmentos.append({"inicio": dentro[0]["inicio"], "fim": dentro[-1]["fim"],
                              "texto": " ".join(p["palavra"] for p in dentro)})
    novo_total = sum(b - a for a, b in trechos)
    transcricao.salvar({"idioma": dados.get("idioma", "pt"), "duracao": round(novo_total, 3),
                        "segmentos": segmentos, "palavras": novas},
                       transcricao.caminho_transcricao(destino))

    relatorio = destino.with_name(destino.stem + ".cortes.json")
    relatorio.write_text(json.dumps({"original": str(video.name), "duracao_original": round(duracao, 3),
                                     "duracao_final": round(novo_total, 3), "pausa_max": pausa_max,
                                     "margem": margem, "trechos_mantidos": [[round(a, 3), round(b, 3)] for a, b in trechos],
                                     "muletas_removidas": len(dados["palavras"]) - len(mantidas)},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDe {duracao:.1f}s para {novo_total:.1f}s ({duracao - novo_total:.1f}s removidos, "
          f"{len(dados['palavras']) - len(mantidas)} muleta(s)).")
    print(f"Vídeo cortado: {destino}")
    print(f"Transcrição ajustada: {transcricao.caminho_transcricao(destino)}")
    return destino

