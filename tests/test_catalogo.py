"""O Python e o Remotion guardam as mesmas listas, cada um por conta própria.

O CLAUDE.md manda um tipo de cena novo entrar em três lugares — a skill, o
`CATALOGO` e um componente. Nada no código obriga isso, e não há como obrigar
sem um dos lados importar o outro. Então o guardião é este arquivo: quem mexer
num lado só descobre aqui, e não num reel já publicado.
"""

import re
from pathlib import Path

from editor import plano

RAIZ = Path(__file__).resolve().parent.parent
MOTION = RAIZ / "motion" / "src"


def _bloco(texto, abre, fecha):
    inicio = texto.index(abre) + len(abre)
    return texto[inicio:texto.index(fecha, inicio)]


def icones_do_remotion():
    fonte = (MOTION / "icones.ts").read_text(encoding="utf-8")
    corpo = _bloco(fonte, "const ICONES = {", "} as const;")
    return {m.group(1) for m in re.finditer(r'^\s+"?([a-z0-9-]+)"?:\s', corpo, re.M)}


def tipos_do_switch():
    fonte = (MOTION / "scenes" / "index.tsx").read_text(encoding="utf-8")
    return set(re.findall(r'case "([a-z_]+)":', fonte))


def tipos_da_skill():
    """Os tipos listados na TABELA do catálogo de `reels-composicao`.

    Lê as linhas da tabela, não qualquer coisa entre crases. A versão
    anterior filtrava por `if t in plano.CATALOGO` e por isso era incapaz,
    por construção, de ver um tipo documentado que ninguém implementou —
    que é metade do erro que este arquivo existe para pegar.
    """
    fonte = (RAIZ / ".claude" / "skills" / "reels-composicao" / "SKILL.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\|\s*`([a-z_]+)`\s*\|", fonte, re.M))


def test_os_icones_sao_os_mesmos_dos_dois_lados():
    do_python = set(plano.ICONES_DISPONIVEIS)
    do_remotion = icones_do_remotion()

    assert do_remotion, "não consegui ler o mapa ICONES de motion/src/icones.ts"
    assert do_python == do_remotion, (
        "ICONES_DISPONIVEIS (editor/plano.py) e ICONES (motion/src/icones.ts) "
        f"discordam. Só no Python: {sorted(do_python - do_remotion)}. "
        f"Só no Remotion: {sorted(do_remotion - do_python)}."
    )


def mundos_do_remotion():
    fonte = (MOTION / "theme.ts").read_text(encoding="utf-8")
    corpo = _bloco(fonte, "export const mundos = {", "\n} as const;")
    return set(re.findall(r"^  ([a-z]+): \{", corpo, re.M))


def test_os_mundos_sao_os_mesmos_dos_dois_lados():
    do_python = set(plano.MUNDOS)
    do_remotion = mundos_do_remotion()

    assert do_remotion, "não consegui ler `mundos` de motion/src/theme.ts"
    assert do_python == do_remotion, (
        "MUNDOS (editor/plano.py) e `mundos` (motion/src/theme.ts) discordam. "
        f"Só no Python: {sorted(do_python - do_remotion)}. "
        f"Só no Remotion: {sorted(do_remotion - do_python)}."
    )


def test_o_mundo_padrao_existe():
    assert plano.MUNDO_PADRAO in plano.MUNDOS


def test_todo_tipo_do_catalogo_tem_componente():
    do_catalogo = set(plano.CATALOGO)
    do_switch = tipos_do_switch()

    assert do_switch, "não consegui ler os `case` de motion/src/scenes/index.tsx"
    assert do_catalogo == do_switch, (
        "O CATALOGO (editor/plano.py) e o switch (motion/src/scenes/index.tsx) "
        f"discordam. Sem componente: {sorted(do_catalogo - do_switch)}. "
        f"Sem entrada no catálogo: {sorted(do_switch - do_catalogo)}."
    )


def test_a_skill_e_o_catalogo_listam_os_mesmos_tipos():
    """Nos dois sentidos.

    Tipo no catálogo e fora da skill: ninguém sabe quando usá-lo. Tipo na
    skill e fora do catálogo é pior — alguém lê a documentação, escreve a
    cena no plano, e o validador rejeita um tipo que a própria skill mandou
    usar. Foi exatamente o que aconteceu com `cena_apoio`.
    """
    do_catalogo = set(plano.CATALOGO)
    da_skill = tipos_da_skill()

    assert da_skill, "não consegui ler a tabela de tipos de reels-composicao"
    assert do_catalogo == da_skill, (
        "O CATALOGO (editor/plano.py) e a tabela de reels-composicao discordam. "
        f"Documentado mas não implementado: {sorted(da_skill - do_catalogo)}. "
        f"Implementado mas não documentado: {sorted(do_catalogo - da_skill)}."
    )


def test_todo_tipo_sabe_quando_usar_e_como_se_verificar():
    for tipo, ficha in plano.CATALOGO.items():
        assert ficha.get("quando"), f"{tipo}: falta o 'quando'"
        assert callable(ficha.get("verificar")), f"{tipo}: falta a função 'verificar'"
