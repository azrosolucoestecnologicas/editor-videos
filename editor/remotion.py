"""Chamada do Remotion para gerar stills e o vídeo final.

O projeto Remotion vive em `motion/` e é rodado pelo `npx` de lá. Este
módulo só monta a linha de comando: toda a aparência está nos componentes.
"""

import shutil
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_MOTION = RAIZ / "motion"
COMPOSICAO = "Reel"

# Mesma qualidade do renderizador antigo em `editor/render.py`.
CRF = 18


def verificar():
    """Confere que dá para chamar o Remotion antes de perder tempo cortando."""
    if shutil.which("npx") is None:
        raise SystemExit(
            "npx não encontrado. Instale o Node.js 20+ para renderizar com o Remotion."
        )
    if not (PASTA_MOTION / "node_modules").exists():
        raise SystemExit(
            f"Dependências do Remotion ausentes. Rode:\n  cd {PASTA_MOTION} && npm install"
        )


def _rodar(comando):
    print("  " + " ".join(comando))
    subprocess.run(comando, cwd=PASTA_MOTION, check=True)


def renderizar(props, destino, previa=False, concorrencia=None, log="info"):
    """Gera o vídeo final. `previa` renderiza em metade da resolução."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    comando = [
        "npx", "remotion", "render", COMPOSICAO, str(destino.resolve()),
        f"--props={Path(props).resolve()}",
        "--codec=h264",
        f"--crf={CRF}",
        f"--log={log}",
    ]
    if previa:
        comando.append("--scale=0.5")
    if concorrencia:
        comando.append(f"--concurrency={concorrencia}")

    _rodar(comando)
    return destino


def stills(props, frames, pasta, log="error"):
    """Renderiza frames avulsos como PNG, num empacotamento só.

    A pasta é esvaziada antes: o Remotion varia o zero à esquerda do nome
    conforme a quantidade de frames (`element-405.png` num render de um,
    `element-0405.png` num de oito), então sobras de uma rodada anterior
    ficariam lado a lado com as novas e seriam lidas como se fossem atuais.
    """
    pasta = Path(pasta)
    if pasta.exists():
        for antigo in pasta.glob("*.png"):
            antigo.unlink()
    pasta.mkdir(parents=True, exist_ok=True)

    _rodar([
        "npx", "remotion", "render", COMPOSICAO, str(pasta.resolve()),
        f"--props={Path(props).resolve()}",
        f"--frames={','.join(str(f) for f in frames)}",
        "--image-format=png",
        f"--log={log}",
    ])
    return sorted(pasta.glob("*.png"))


def frames_chave(plano, maximo=6):
    """Um frame por cena, a 70% dela — depois que todos os elementos entraram.

    Com mais cenas que `maximo`, escolhe cenas espalhadas pelo reel em vez
    das primeiras, para a conferência cobrir começo, meio e fim.
    """
    cenas = plano.get("cenas") or []
    fps = plano.get("fps", 30)
    if not cenas:
        return []

    if len(cenas) <= maximo:
        escolhidas = cenas
    else:
        passo = (len(cenas) - 1) / (maximo - 1)
        escolhidas = [cenas[round(i * passo)] for i in range(maximo)]

    duracao_total = float(plano.get("duracao") or 0)
    frames = []
    for cena in escolhidas:
        instante = cena["inicio"] + 0.7 * (cena["fim"] - cena["inicio"])
        frame = round(min(instante, duracao_total - 1 / fps) * fps)
        frames.append(max(0, frame))
    return sorted(set(frames))
