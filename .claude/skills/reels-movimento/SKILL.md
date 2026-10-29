---
name: reels-movimento
description: Padrão de animação dos reels do Thiago (entradas, saídas, transições, curvas de easing, zooms no vídeo gravado). Consultar SEMPRE ao escrever ou ajustar qualquer interpolate, spring ou transição nos componentes Remotion.
---

# Movimento nos reels

Movimento bom é o que o espectador não nota: ele só percebe que a informação apareceu no momento certo. Tudo é curto, amortecido e com direção coerente.

## Presets (fonte única: `motion/src/motion.ts`)

Crie e reutilize estes presets. Nenhum componente define curva própria.

| Preset | Implementação Remotion | Uso |
|---|---|---|
| `entrada` | `spring({ config: { damping: 200, stiffness: 120 }, durationInFrames: 14 })` + translateY 24 px para 0 + opacity 0 para 1 | padrão de qualquer elemento |
| `entradaSuave` | igual, 20 frames, translateY 12 px | textos longos, citações legais |
| `saida` | `interpolate` 8 frames, opacity 1 para 0, translateY 0 para -12 px, easing `Easing.in(Easing.cubic)` | saída de qualquer elemento |
| `destaque` | scale 1 para 1,06 em 6 frames e volta em 10 frames | palavra ou elemento enfatizado |
| `desenho` | `strokeDashoffset` de comprimento total a 0 em 18 a 24 frames | setas, linhas, conectores, sublinhado |
| `contador` | `interpolate` com `Easing.out(Easing.cubic)` terminando no frame em que o número é falado | números |

## Direção

- Elementos entram de baixo para cima ou da esquerda para a direita, na ordem de leitura. Nunca de cima para baixo, nunca girando.
- Itens de lista: atraso de 6 a 8 frames entre um e outro quando entram juntos; quando seguem a fala, use os timestamps (ver `reels-ritmo`).
- Fluxos com setas: caixa, depois seta desenhando, depois a próxima caixa.

## Transição entre cenas

- Padrão: a cena atual sai com `saida` enquanto a próxima entra com `entrada`, sobrepostas 4 a 6 frames.
- Para mudança de assunto: wipe horizontal de 12 frames com `navySoft`.
- Proibido: zoom de transição, giro, flash branco, glitch, slide 3D.

## Vídeo gravado (metade de baixo)

- Zoom leve de ênfase: scale 1,0 para 1,08 em 20 frames, mantido até o fim da frase, volta em 12 frames. No máximo um a cada 8 segundos.
- Use o zoom para disfarçar jump cuts consecutivos (alterne 1,0 e 1,08 entre cortes).
- Enquadramento centrado no rosto, com os olhos no terço superior da metade de baixo.
- Nunca: shake, tremor de câmera falso, efeito de "punch" a cada palavra.

## Limites

- Duração de qualquer entrada: 8 a 24 frames (a 30 fps).
- Nenhum elemento em loop infinito (pulsar, girar, flutuar).
- Movimento contínuo só em indicadores de progresso, e lento.

## Checklist

1. Nenhum componente com curva ou duração fora dos presets.
2. Todas as entradas na direção de leitura.
3. Nenhum loop decorativo.
4. Zooms no vídeo espaçados em no mínimo 8 s.
