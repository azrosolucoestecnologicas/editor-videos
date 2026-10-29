#!/usr/bin/env python3
"""Fixture visual do catálogo de cenas.

Monta um plano sintético com um exemplo de cada um dos 8 tipos, reaproveitando
o vídeo de um plano que já existe. Serve para conferir o layout de todos eles
de uma vez depois de mexer em `theme.ts`, em `motion.ts` ou num componente —
inclusive dos tipos que um reel específico não usa.

    python exemplos/tipos_de_cena.py planos/MEU_VIDEO_cortado.props.json

Os textos são de preenchimento, escolhidos para bater no limite de palavras de
cada tipo. A citação legal traz um texto neutro de propósito: citação de
verdade só com o dispositivo conferido na fonte.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from editor import remotion as mod_remotion  # noqa: E402

DURACAO_CENA = 5.0

# Um exemplo por tipo, cada um no limite que a skill `reels-composicao` permite.
EXEMPLOS = [
    ("card_conceito", {
        "termo": "Alucinação",
        "definicao": "quando o modelo responde com confiança algo que não existe",
    }),
    ("lista", {
        "titulo": "O método tem três partes",
        "itens": [
            {"texto": "Contexto do caso"},
            {"texto": "Fonte verificável"},
            {"texto": "Conferência humana"},
        ],
    }),
    ("comparacao", {
        "esquerda": {"titulo": "Sem método", "linhas": ["jurisprudência inventada", "risco disciplinar"]},
        "direita": {"titulo": "Com método", "linhas": ["fonte conferida", "peça defensável"]},
    }),
    ("fluxo", {
        "etapas": [
            {"rotulo": "Pergunta"}, {"rotulo": "Busca"},
            {"rotulo": "Minuta"}, {"rotulo": "Conferência"},
        ],
    }),
    ("numero", {"valor": "360", "rotulo": "horas reconhecidas pelo MEC"}),
    ("citacao_legal", {
        "referencia": "Art. 7º, XIII, CF",
        "trecho": (
            "texto neutro de preenchimento com vinte palavras para conferir o "
            "card quando a citação ocupa mais de uma linha inteira do painel"
        ),
    }),
    ("icone_destaque", {"icone": "shield-check", "texto": "Fonte conferida"}),
    ("sintese", {"frase": "Use IA com método"}),
]


def montar(props_existente):
    base = json.loads(Path(props_existente).read_text(encoding="utf-8"))
    cenas = []
    for i, (tipo, conteudo) in enumerate(EXEMPLOS):
        inicio = i * DURACAO_CENA
        cenas.append({
            "id": f"t{i + 1:02d}",
            "inicio": inicio,
            "fim": inicio + DURACAO_CENA,
            "palavra_gatilho": "",
            "ocorrencia": 1,
            "tipo": tipo,
            "conteudo": conteudo,
            "editado": True,
        })

    return {
        "plano": {
            **base["plano"],
            "duracao": len(EXEMPLOS) * DURACAO_CENA,
            "assinatura": "Catálogo de cenas",
            "cenas": cenas,
        },
        # Painel isolado: as legendas já são conferidas no reel de verdade.
        "legendas": [],
        "video": base["video"],
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    props = montar(sys.argv[1])
    destino = RAIZ / "planos" / "catalogo_de_cenas.props.json"
    destino.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")

    fps = props["plano"]["fps"]
    # 70% de cada cena: depois que todos os elementos entraram.
    frames = [round((i * DURACAO_CENA + 0.7 * DURACAO_CENA) * fps) for i in range(len(EXEMPLOS))]
    saida = RAIZ / "output" / "stills" / "catalogo"

    print(f"Plano: {destino}")
    print(f"Renderizando {len(frames)} still(s) em {saida} ...")
    gerados = mod_remotion.stills(destino, frames, saida)
    for tipo, arquivo in zip([t for t, _ in EXEMPLOS], gerados):
        print(f"  {tipo:16} {arquivo.name}")


if __name__ == "__main__":
    main()
