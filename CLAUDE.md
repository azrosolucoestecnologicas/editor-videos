# Pipeline de reels

Antes de criar ou alterar qualquer cena, legenda, corte ou animação dos reels,
consulte as skills reels-estilo, reels-ritmo, reels-legendas, reels-movimento
e reels-composicao (em `.claude/skills/`). Em conflito, reels-composicao decide layout e reels-ritmo decide tempo.

- O Remotion (`motion/`) é o único motor de render. O editor antigo em Pillow
  (`render.py`, `compositor.py`, `roteiro.py`, `animacoes/` e os roteiros YAML) foi
  removido; se precisar dele, está no commit `bed62b4`. Não reintroduza um segundo motor.
- O Python só corta, planeja e chama o Remotion: nada de desenhar quadro a quadro de volta.
- Tokens visuais ficam só em `motion/src/theme.ts` e presets de animação só em `motion/src/motion.ts`.
- Correções de termos da transcrição ficam em `glossario.json` na raiz.
- `motion-trial/` usa outro motor (motion-skills/GSAP, da skill `motion-director`) e é
  para peças curtas avulsas. Não misture com o pipeline de reels.

## Fluxo atual

`python editar.py reel entrada/X.mp4` faz tudo: corta, planeja, valida e renderiza
em `output/`. O conteúdo das cenas do `planos/<nome>.scene_plan.json` é escrito
nesta conversa, não por heurística — a fala de cada cena está no campo `_fala`.

- Tipo de cena novo entra em três lugares, nesta ordem: a skill `reels-composicao`,
  o `CATALOGO` de `editor/plano.py` e um componente em `motion/src/scenes/`.
- Cenas editadas à mão são preservadas pelo `_hash`; campos com prefixo `_` são
  derivados. Para recalcular uma, use `--refazer-cena ID`.
- Antes de qualquer render completo, gere stills (`--stills`) e confira.
- `pytest` roda em menos de um segundo e não precisa de ffmpeg. Rode depois de
  mexer em `mesclar`, no glossário, nos cortes ou em qualquer das duas listas
  que o Python e o Remotion guardam em paralelo (ícones e tipos de cena).
