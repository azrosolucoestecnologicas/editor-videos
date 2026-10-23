from . import basicas, graficos, midia  # noqa: F401  (registra as animações)
from .base import REGISTRO, Animacao


def criar(params, tema, escala, roteiro, tamanho):
    tipo = params.get("tipo", "texto")
    if tipo not in REGISTRO:
        raise SystemExit(f"Animação desconhecida: '{tipo}'. Disponíveis: {', '.join(sorted(REGISTRO))}")
    return REGISTRO[tipo](params, tema, escala, roteiro, tamanho)


__all__ = ["REGISTRO", "Animacao", "criar"]
