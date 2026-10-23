"""Transcrição do áudio com marcação de tempo por palavra (faster-whisper)."""

import json
from pathlib import Path

# Modelos ficam dentro do projeto: baixados uma vez, funcionam offline em qualquer ambiente.
PASTA_MODELOS = Path(__file__).resolve().parent.parent / "modelos"


def caminho_transcricao(video):
    video = Path(video)
    return video.with_name(video.stem + ".transcricao.json")


def formatar_tempo(segundos):
    m, s = divmod(max(0.0, segundos), 60)
    return f"{int(m):02d}:{s:04.1f}"


def transcrever(video, modelo="small", idioma="pt", destino=None):
    try:
        from faster_whisper import WhisperModel
    except ImportError as erro:
        raise SystemExit(
            "faster-whisper não está instalado. Rode: pip install -r requirements.txt"
        ) from erro

    destino = Path(destino) if destino else caminho_transcricao(video)
    print(f"Carregando modelo Whisper '{modelo}' (a primeira vez faz o download)...")
    # Se o modelo já foi baixado, não tenta acessar a internet (permite rodar offline).
    ja_baixado = any(PASTA_MODELOS.glob(f"models--*--faster-whisper-{modelo}/snapshots/*/model.bin"))
    whisper = WhisperModel(modelo, device="auto", compute_type="int8", download_root=str(PASTA_MODELOS),
                           local_files_only=ja_baixado)
    print(f"Transcrevendo {video} ...")
    segmentos_iter, info = whisper.transcribe(
        str(video), language=idioma, word_timestamps=True, vad_filter=True, beam_size=5
    )

    segmentos, palavras = [], []
    for seg in segmentos_iter:
        segmentos.append({"inicio": round(seg.start, 3), "fim": round(seg.end, 3), "texto": seg.text.strip()})
        for p in seg.words or []:
            texto = p.word.strip()
            if texto:
                palavras.append({"palavra": texto, "inicio": round(p.start, 3), "fim": round(p.end, 3)})
        print(f"  [{formatar_tempo(seg.start)}] {seg.text.strip()}")

    dados = {"idioma": info.language, "duracao": round(info.duration, 3),
             "segmentos": segmentos, "palavras": palavras}
    salvar(dados, destino)
    print(f"\nTranscrição salva em {destino}")
    print(f"Versão legível em {destino.with_suffix('.txt')}")
    return dados


def salvar(dados, destino):
    destino = Path(destino)
    destino.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    linhas = [f"[{formatar_tempo(s['inicio'])} - {formatar_tempo(s['fim'])}] {s['texto']}" for s in dados["segmentos"]]
    destino.with_suffix(".txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def carregar(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    dados["palavras"] = sorted(dados.get("palavras", []), key=lambda p: p["inicio"])
    return dados
