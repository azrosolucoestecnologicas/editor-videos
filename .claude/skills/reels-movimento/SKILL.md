---
name: reels-movimento
description: Padrão de animação dos reels do Thiago (entradas com profundidade, brilho metálico, saídas, transições, curvas, zooms no vídeo gravado). Consultar SEMPRE ao escrever ou ajustar qualquer interpolate, spring ou transição nos componentes Remotion.
---

# Movimento nos reels

Movimento bom é o que o espectador não nota: ele só percebe que a informação
apareceu no momento certo. Tudo é curto, amortecido e com direção coerente.

## O que mudou da v1

Três presets novos, todos a serviço da profundidade da `reels-composicao`:
`flutuar` (entrada com perspectiva), `brilhoMetal` (varredura especular) e
`profundidade` (a sombra cresce junto com a entrada). Nada foi removido.

## Presets (fonte única: `motion/src/motion.ts`)

Crie e reutilize estes presets. Nenhum componente define curva própria.

| Preset | Implementação Remotion | Uso |
|---|---|---|
| `entrada` | `spring({ config: { damping: 200, stiffness: 120 }, durationInFrames: 14 })` + translateY 24 px para 0 + opacity 0 para 1 | padrão de qualquer elemento |
| `entradaSuave` | igual, 20 frames, translateY 12 px | textos longos, citações legais |
| `flutuar` | **novo**: igual `entrada`, 18 frames, mais `rotateY` -6° para 0° e `scale` 0,96 para 1 | card que flutua sobre o vídeo |
| `profundidade` | **novo**: sombra de `0 8px 20px rgba(0,0,0,0.2)` para `0 24px 60px rgba(0,0,0,0.45)` nos mesmos 18 frames do `flutuar` | acompanha sempre o `flutuar` |
| `brilhoMetal` | **novo**: `metal.brilho` atravessando o card da esquerda para a direita em 22 frames, `Easing.inOut(Easing.cubic)`, **uma vez só** | card com borda metálica, na entrada |
| `saida` | `interpolate` 8 frames, opacity 1 para 0, translateY 0 para -12 px, easing `Easing.in(Easing.cubic)` | saída de qualquer elemento |
| `destaque` | scale 1 para 1,06 em 6 frames e volta em 10 frames | palavra ou elemento enfatizado |
| `desenho` | `strokeDashoffset` de comprimento total a 0 em 18 a 24 frames | setas, linhas, conectores, sublinhado |
| `contador` | `interpolate` com `Easing.out(Easing.cubic)` terminando no frame em que o número é falado | números |

### Sobre o `brilhoMetal`

É o preset mais fácil de estragar o vídeo. Duas regras:

- **Uma passada por card, na entrada.** Nunca em laço, nunca repetindo.
- No máximo **duas cenas por reel** usam brilho. Se todo card brilha, nenhum
  brilha — e o reel vira anúncio de aposta.

## Direção

- Elementos entram de baixo para cima ou da esquerda para a direita, na ordem
  de leitura. Nunca de cima para baixo, nunca girando.
- A rotação do `flutuar` é de eixo Y e some: é perspectiva, não giro. Nenhum
  elemento termina a entrada fora do plano.
- Itens de lista: atraso de 6 a 8 frames entre um e outro quando entram juntos;
  quando seguem a fala, use os timestamps (ver `reels-ritmo`).
- Fluxos com setas: caixa, depois seta desenhando, depois a próxima caixa.

## Transição entre cenas

- Padrão: a cena atual sai com `saida` enquanto a próxima entra com `flutuar`,
  sobrepostas 4 a 6 frames.
- Para mudança de assunto: wipe horizontal de 12 frames com `reforco`.
- Para entrar e sair de uma `cena_apoio`: as mesmas `flutuar` e `saida`. **Nunca
  corte seco para o b-roll** — é o que faz parecer vídeo de banco colado.
- Proibido: zoom de transição, giro, flash branco, glitch, slide 3D.

## Vídeo gravado

- Zoom leve de ênfase: scale 1,0 para 1,08 em 20 frames, mantido até o fim da
  frase, volta em 12 frames. No máximo um a cada 8 segundos.
- Use o zoom para disfarçar jump cuts consecutivos (alterne 1,0 e 1,08 entre
  cortes).
- O fundo vivo **não** acompanha o zoom do vídeo nítido: ele fica parado. Se os
  dois se mexerem juntos, o efeito de profundidade some.
- Nunca: shake, tremor de câmera falso, efeito de "punch" a cada palavra.

## Limites

- Duração de qualquer entrada: 8 a 24 frames (a 30 fps).
- Nenhum elemento em laço infinito (pulsar, girar, flutuar, brilhar).
- Movimento contínuo só em indicadores de progresso, e lento.

## Checklist

1. Nenhum componente com curva ou duração fora dos presets.
2. Todas as entradas na direção de leitura.
3. Nenhum laço decorativo; nenhum brilho repetindo.
4. No máximo duas cenas com `brilhoMetal`.
5. Zooms no vídeo espaçados em no mínimo 8 s, e o fundo vivo parado.
