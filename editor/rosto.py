"""Enquadramento do rosto na metade de baixo da tela dividida.

Amostra alguns quadros do vídeo, detecta o rosto e devolve a altura dele
como fração (0 = topo, 1 = base) — o mesmo formato do `foco_rosto` que o
editor antigo já usava, então o valor é intercambiável entre os dois.

Usa o cascade frontal que vem dentro do `opencv-python`: nada é baixado, o
que mantém o pipeline funcionando offline. É uma detecção simples, feita
para um plano de alguém falando de frente para a câmera; se ela falhar, o
valor padrão continua valendo e você ajusta à mão no `scene_plan.json`.
"""

import statistics
import subprocess
import tempfile
from concurrent import futures
from pathlib import Path

from . import ffmpeg

PADRAO = 0.36
# Quanto o cabelo sobe acima da caixa do rosto, como fracao da altura dela.
# O cascade acha a FACE (testa a queixo); o topo da cabeca fica acima disso.
CABELO = 0.32
AMOSTRAS = 24
# Quantos ffmpeg de cada vez. Oito satura os núcleos sem virar disputa: o
# gargalo de cada um é decodificar um punhado de quadros, não a CPU.
PARALELAS = 8
# Abaixo disso a detecção não é confiável o bastante para mexer no
# enquadramento: melhor manter o valor que já estava.
MINIMO_DETECCOES = 3


def detectar(video, amostras=AMOSTRAS, padrao=PADRAO):
    """Mede o enquadramento.

    Devolve ``(foco_rosto, topo_cabeca, deteccoes, quadros)``, tudo em
    fracao da altura do arquivo. `topo_cabeca` existe porque a dissolucao
    no alto da faixa de video precisa terminar ANTES dela: sem essa medida,
    o degrade come a cabeca de quem tem o rosto alto no quadro.
    """
    try:
        import cv2
    except ImportError:
        return padrao, padrao - 0.15, 0, 0

    duracao = ffmpeg.duracao(video, padrao=0.0)
    if not duracao:
        return padrao, padrao - 0.15, 0, 0

    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    alturas, topos = [], []
    with tempfile.TemporaryDirectory() as tmp:
        quadros = _extrair(video, duracao, amostras, Path(tmp))
        for quadro in quadros:
            imagem = cv2.imread(str(quadro))
            if imagem is None:
                continue
            cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            cinza = cv2.equalizeHist(cinza)
            achados = cascade.detectMultiScale(
                cinza, scaleFactor=1.1, minNeighbors=6,
                minSize=(int(imagem.shape[1] * 0.08),) * 2,
            )
            if len(achados) == 0:
                continue
            # Com mais de um rosto, fica o maior: é quem está falando.
            x, y, w, h = max(achados, key=lambda r: r[2] * r[3])
            alturas.append((y + h / 2) / imagem.shape[0])
            topos.append((y - h * CABELO) / imagem.shape[0])

    if len(alturas) < MINIMO_DETECCOES:
        return padrao, padrao - 0.15, len(alturas), len(quadros)
    # Mediana: um quadro em que ele virou o rosto não desloca o enquadramento.
    return (
        round(statistics.median(alturas), 4),
        round(statistics.median(topos), 4),
        len(alturas),
        len(quadros),
    )



def _um_quadro(video, t, destino):
    """Um quadro no instante `t`. Devolve o caminho, ou None se não saiu."""
    # `-ss` ANTES do `-i`: o ffmpeg salta direto para o keyframe mais próximo
    # em vez de decodificar desde o começo. É o que mantém o custo constante
    # por quadro, qualquer que seja a duração do vídeo.
    resultado = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video),
         "-frames:v", "1", "-vf", "scale=480:-1", "-y", str(destino)],
        capture_output=True,
    )
    return destino if resultado.returncode == 0 and destino.exists() else None


def _extrair(video, duracao, amostras, pasta):
    """Tira `amostras` quadros espalhados pelo vídeo, evitando as pontas.

    Em paralelo, e não em série: eram 24 processos um atrás do outro numa
    etapa que roda em toda primeira geração de plano. Medido num vídeo de
    48 s, 5,7 s em série contra 2,1 s com 8 de cada vez.

    Um passe único de ffmpeg com o filtro `fps` também daria 24 quadros, e
    chega a 2,4 s neste arquivo — mas ele decodifica o vídeo inteiro, então
    piora conforme o reel cresce, enquanto estes seeks não.
    """
    tempos = [(i, duracao * (i + 0.5) / amostras) for i in range(amostras)]
    with futures.ThreadPoolExecutor(max_workers=PARALELAS) as pool:
        saidas = pool.map(
            lambda par: _um_quadro(video, par[1], pasta / f"q{par[0]:03d}.png"),
            tempos,
        )
    return [caminho for caminho in saidas if caminho is not None]
