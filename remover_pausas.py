#!/usr/bin/env python3
"""Remove automaticamente as pausas longas do vídeo."""

import subprocess
import json
from pathlib import Path

def remover_pausas(video_entrada, video_saida, trans_json):
    """Remove pausas >2.5s usando o arquivo de transcrição."""

    # Carregar transcrição
    with open(trans_json) as f:
        data = json.load(f)

    segmentos = data["segmentos"]

    # Encontrar pausas longas
    clips = []
    tempo_inicio = 0

    for i in range(len(segmentos)-1):
        fim_atual = segmentos[i]["fim"]
        inicio_proximo = segmentos[i+1]["inicio"]
        pausa = inicio_proximo - fim_atual

        if pausa > 2.5:  # Pausa longa - cortar
            if tempo_inicio < fim_atual:
                clips.append((tempo_inicio, fim_atual))
            tempo_inicio = inicio_proximo

    # Adicionar o final
    duracao_total = data["duracao"]
    if tempo_inicio < duracao_total:
        clips.append((tempo_inicio, duracao_total))

    print(f"✂️  Removendo {len(segmentos) - len(clips)} pausas longas...")
    print(f"   Mantendo {len(clips)} clipes contínuos")

    # Criar arquivo de concatagem
    temp_dir = Path("saida/temp_clips")
    temp_dir.mkdir(exist_ok=True)

    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for i, (start, end) in enumerate(clips):
            clip_file = temp_dir / f"clip_{i:03d}.mp4"
            duracao = end - start

            # Extrair clip
            cmd = [
                "ffmpeg", "-y", "-v", "error",
                "-ss", str(start),
                "-i", video_entrada,
                "-t", str(duracao),
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k",
                str(clip_file)
            ]
            print(f"   Clip {i+1}: {start:.1f}s → {end:.1f}s")
            subprocess.run(cmd, check=True, capture_output=True)
            f.write(f"file '{clip_file.name}'\n")

    # Concatenar
    print("\n🔗 Concatenando clipes...")
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "copy", "-c:a", "aac",
        "-b:a", "192k", str(video_saida)
    ]
    subprocess.run(cmd, cwd=str(temp_dir), check=True, capture_output=True)

    print(f"✓ Vídeo sem pausas: {video_saida}")
    return video_saida

if __name__ == "__main__":
    import sys
    entrada = sys.argv[1] if len(sys.argv) > 1 else "saida/Enter_x_OAB_v2_profissional.mp4"
    saida = sys.argv[2] if len(sys.argv) > 2 else "saida/Enter_x_OAB_v2_sem_pausas.mp4"
    trans = "entrada/Enter x OAB/D6EB16CD-BAC0-4026-B71D-E318BD41CF0E.transcricao.json"

    remover_pausas(entrada, saida, trans)
