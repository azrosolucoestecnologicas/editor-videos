# Pipeline de reels

Antes de criar ou alterar qualquer cena, legenda, corte ou animação dos reels,
consulte as skills reels-estilo, reels-ritmo, reels-legendas, reels-movimento
e reels-composicao (em `.claude/skills/`). Em conflito, reels-composicao decide layout e reels-ritmo decide tempo.

- O editor em Python (`editar.py`, pasta `editor/`) deve continuar funcionando: não mude o comportamento dos comandos existentes.
- Tokens visuais ficam só em `motion/src/theme.ts` e presets de animação só em `motion/src/motion.ts`.
- Correções de termos da transcrição ficam em `glossario.json` na raiz.
