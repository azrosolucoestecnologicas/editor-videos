"""As chamadas ao FFmpeg que mais de um módulo precisa.

`duracao` existia copiada em três arquivos (cortes, render e rosto), cada
cópia com um tratamento de erro diferente: uma deixava a exceção subir, outra
devolvia 0.0 calado. Agora quem chama escolhe, e a escolha fica explícita.
"""

import shutil
import subprocess


def verificar():
    """Para cedo, com uma mensagem útil, se o FFmpeg não estiver instalado."""
    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            raise SystemExit(
                f"'{prog}' não encontrado. Instale o FFmpeg (veja o README) e tente de novo."
            )


def duracao(video, padrao=None):
    """Duração do arquivo em segundos, medida no próprio vídeo.

    Sem ``padrao``, um arquivo ilegível levanta a exceção — quem pergunta o
    tamanho de algo normalmente precisa que esse algo exista. Com ``padrao``,
    devolve esse valor: é o caso da detecção de rosto, que prefere desistir do
    enquadramento automático a derrubar a geração do plano inteiro.
    """
    try:
        saida = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(video)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return float(saida)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        if padrao is None:
            raise
        return padrao
