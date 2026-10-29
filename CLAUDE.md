# Pipeline de reels

Antes de criar ou alterar qualquer cena, legenda, corte ou animação dos reels,
consulte as skills reels-estilo, reels-ritmo, reels-legendas, reels-movimento
e reels-composicao (em `.claude/skills/`). Em conflito, reels-composicao decide layout e reels-ritmo decide tempo.

- O editor em Python (`editar.py`, pasta `editor/`) deve continuar funcionando: não mude o comportamento dos comandos existentes.
- Tokens visuais ficam só em `motion/src/theme.ts` e presets de animação só em `motion/src/motion.ts`.
- Correções de termos da transcrição ficam em `glossario.json` na raiz.

## Fluxo atual

`python editar.py reel entrada/X.mp4` faz tudo: corta, planeja, valida e renderiza
em `output/`. O conteúdo das cenas do `planos/<nome>.scene_plan.json` é escrito
nesta conversa, não por heurística — a fala de cada cena está no campo `_fala`.

- Tipo de cena novo entra em três lugares, nesta ordem: a skill `reels-composicao`,
  o `CATALOGO` de `editor/plano.py` e um componente em `motion/src/scenes/`.
- Cenas editadas à mão são preservadas pelo `_hash`; campos com prefixo `_` são
  derivados. Para recalcular uma, use `--refazer-cena ID`.
- Antes de qualquer render completo, gere stills (`--stills`) e confira.
