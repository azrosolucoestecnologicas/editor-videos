# Skills de edição dos reels

Cinco skills para o Claude Code consultar antes de editar os reels:

| Skill | Governa |
|---|---|
| `reels-estilo` | cores, tipografia, ícones, o que nunca usar |
| `reels-ritmo` | sincronia com a fala, densidade de cenas, cortes e respiros |
| `reels-legendas` | posição, quebra, destaque, glossário de termos jurídicos e técnicos |
| `reels-movimento` | presets de entrada, saída, transição e zoom |
| `reels-composicao` | tela dividida, zonas seguras, camadas e catálogo de cenas |

## Instalação

1. Copie a pasta `.claude/skills/` para a raiz do projeto do pipeline de reels (mesclando com uma `.claude/` existente, se houver).
2. Abra o Claude Code no projeto e confirme que as skills foram reconhecidas pedindo: "liste as skills disponíveis neste projeto".
3. Acrescente ao `CLAUDE.md` do projeto:

```
Antes de criar ou alterar qualquer cena, legenda, corte ou animação dos reels,
consulte as skills reels-estilo, reels-ritmo, reels-legendas, reels-movimento
e reels-composicao. Em conflito, reels-composicao decide layout e reels-ritmo decide tempo.
```

## Dependências que as skills pressupõem

- Projeto Remotion em `motion/` com `src/theme.ts` (tokens de estilo) e `src/motion.ts` (presets de animação). Se ainda não existirem, peça ao Claude Code para criá-los a partir das skills.
- Transcrição com timestamps por palavra.
- `glossario.json` na raiz para as correções de legenda.

## Ajustes pessoais

A paleta padrão é a da AR. Para outra marca, altere apenas os valores em `theme.ts`; as skills continuam valendo.
