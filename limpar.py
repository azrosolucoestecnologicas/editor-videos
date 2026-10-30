"""Corta duplicações, falas erradas e pausas longas; remapeia a transcrição para o novo tempo."""

import json
import re
import subprocess
import sys

BRUTO = "entrada/Enter x OAB/D6EB16CD-BAC0-4026-B71D-E318BD41CF0E"
VIDEO = f"{BRUTO}.mp4"
TRANSC = f"{BRUTO}.transcricao.json"
SAIDA_VIDEO = "entrada/Enter x OAB/limpo.mp4"
SAIDA_TRANSC = "entrada/Enter x OAB/limpo.transcricao.json"

# Segmentos a descartar (índices da transcrição do bruto). São sempre a 1a tomada,
# em que a frase ficou pela metade; a 2a, logo em seguida, é a que fica.
# Marcar por índice em vez de por tempo evita cortar o fim da frase anterior.
DESCARTAR_SEG = [
    14, 15,              # 1a tomada da ação civil pública
    25, 26, 27, 28,      # 1a tomada do "fase por fase"
    37, 38, 39, 40,      # 1a tomada da fase de postulação
    47, 48, 49, 50,      # 1a tomada da relação econômica
    62,                  # "A cointeligência entre a inteligência..." cortado
    70, 71,              # 1a tomada dos argumentos do outro lado
    74,                  # "A resolvi." — erro de fala
]
# O Whisper colapsou a 1a tomada do "detalhe técnico" e a 2a dentro de uma única
# palavra ("Ordem", 108.4→113.2), então esse corte precisa ser dado na mão.
DESCARTAR_EXTRA = [(102.45, 109.30)]
FOLGA = 0.10  # não encostar na palavra vizinha
# Margem generosa em cada ponta da pausa: a voz costuma começar antes do fim do
# silêncio detectado, e cortar rente come o início/fim das palavras.
RESPIRO = 0.60
PAUSA_MIN = 0.8  # só encurta pausas acima disso


def silencios():
    """Pausas reais do áudio — pega também as que o Whisper esconde dentro de uma palavra."""
    saida = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", VIDEO, "-af", f"silencedetect=noise=-25dB:d={PAUSA_MIN}",
         "-f", "null", "-"],
        capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", saida)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", saida)]
    return list(zip(ini, fim))


def fundir(faixas):
    """Junta faixas que se sobrepõem."""
    juntas = []
    for a, b in sorted(faixas):
        if juntas and a <= juntas[-1][1]:
            juntas[-1][1] = max(juntas[-1][1], b)
        else:
            juntas.append([a, b])
    return juntas


def faixas_descartadas(d):
    """Converte os índices de segmento em faixas de tempo, ancoradas nas palavras
    vizinhas para não comer o fim da frase anterior nem o começo da seguinte."""
    segs, palavras = d["segmentos"], d["palavras"]
    faixas = []
    for i in sorted(DESCARTAR_SEG):
        if faixas and i == faixas[-1][-1] + 1:
            faixas[-1].append(i)
        else:
            faixas.append([i])

    saida = []
    for grupo in faixas:
        antes = [p["fim"] for p in palavras if p["fim"] <= segs[grupo[0]]["inicio"]]
        depois = [p["inicio"] for p in palavras if p["inicio"] >= segs[grupo[-1]]["fim"]]
        a = (max(antes) if antes else segs[grupo[0]]["inicio"]) + FOLGA
        b = (min(depois) if depois else segs[grupo[-1]]["fim"]) - FOLGA
        saida.append([a, b])
    return saida + [list(x) for x in DESCARTAR_EXTRA]


def main():
    d = json.load(open(TRANSC))
    fim_video = d["duracao"]

    # O que sai: as tomadas repetidas inteiras + o miolo de cada pausa (deixando o respiro)
    cortes = faixas_descartadas(d)
    for a, b in silencios():
        if b - a > RESPIRO:
            cortes.append([a + RESPIRO / 2, b - RESPIRO / 2])
    cortes = fundir(cortes)

    # O que fica é o complemento dos cortes
    manter, pos = [], 0.0
    for a, b in cortes:
        if a > pos:
            manter.append((pos, min(a, fim_video)))
        pos = max(pos, b)
    if pos < fim_video:
        manter.append((pos, fim_video))
    manter = [(a, b) for a, b in manter if b - a > 0.08]

    def dentro(t):
        return any(a <= t <= b for a, b in manter)

    segs = [s for s in d["segmentos"] if dentro(s["inicio"]) or dentro(s["fim"])]

    total = sum(b - a for a, b in manter)
    print(f"✂️  {len(manter)} blocos · {total:.1f}s de {fim_video:.1f}s "
          f"(cortou {fim_video - total:.1f}s)")

    # Corta e concatena com ffmpeg
    entradas, filtros, rotulos = [], [], []
    for i, (a, b) in enumerate(manter):
        entradas += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", VIDEO]
        filtros.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}];[{i}:a]asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
        rotulos.append(f"[v{i}][a{i}]")
    filtro = ";".join(filtros) + ";" + "".join(rotulos) + f"concat=n={len(manter)}:v=1:a=1[vo][ao]"

    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", *entradas,
           "-filter_complex", filtro, "-map", "[vo]", "-map", "[ao]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
           "-c:a", "aac", "-b:a", "192k", SAIDA_VIDEO]
    print("🎬 Cortando vídeo...")
    if subprocess.run(cmd).returncode != 0:
        sys.exit("falhou ao cortar")

    # Remapeia os tempos: cada bloco mantido vira um deslocamento na nova linha do tempo
    def remapear(t):
        acum = 0.0
        for a, b in manter:
            if t < a:
                return acum
            if t <= b:
                return acum + (t - a)
            acum += b - a
        return acum

    novo = {"idioma": d["idioma"], "duracao": total, "segmentos": [], "palavras": []}
    for s in segs:
        novo["segmentos"].append({"inicio": remapear(s["inicio"]),
                                  "fim": remapear(s["fim"]), "texto": s["texto"]})
    for p in d["palavras"]:
        if any(a <= p["inicio"] <= b for a, b in manter):
            novo["palavras"].append({"palavra": p["palavra"],
                                     "inicio": remapear(p["inicio"]),
                                     "fim": remapear(p["fim"])})
    json.dump(novo, open(SAIDA_TRANSC, "w"), ensure_ascii=False)
    print(f"✅ {SAIDA_VIDEO}\n✅ {SAIDA_TRANSC} · {len(novo['palavras'])} palavras")


if __name__ == "__main__":
    main()
