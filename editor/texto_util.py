"""Normalização de texto, para casar o que foi falado com o que foi escrito.

Vivia em ``roteiro.py``, que era o leitor de YAML do editor antigo. Com ele
fora, `plano`, `cortes` e `glossario` passam a depender só disto — nenhum
deles precisava de YAML nem do Pillow que vinham junto no import.
"""

import re
import unicodedata


def normalizar(texto):
    """Minúsculas, sem acento, só letras, dígitos e ``%``.

    É o que faz "Ação!" casar com "acao" na hora de achar um gatilho na
    transcrição, e o que mantém "30%" inteiro em vez de virar "30".
    """
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]+", " ", texto).strip()
