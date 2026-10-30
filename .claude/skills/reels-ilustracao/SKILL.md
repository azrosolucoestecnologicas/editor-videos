---
name: reels-ilustracao
description: Como gerar as ilustrações das cenas `objeto` dos reels do Thiago — a gramática visual, o prompt base, o que pedir e o que nunca pedir, e como salvar o arquivo. Consultar SEMPRE que for escrever um prompt de imagem para um reel, ou quando uma cena `objeto` precisar de arte.
---

# Ilustrações das cenas `objeto`

A cena `objeto` mostra a coisa de que a fala trata. É o que faz o reel parecer
caro — e é também o jeito mais rápido de fazê-lo parecer barato, porque um
render 3D genérico tira autoridade exatamente como uma foto de banco de imagem.

Estas imagens não são geradas pelo pipeline. O Thiago gera onde preferir e
salva em `entrada/<job>/`; o `exportar_props` publica sozinho.

## A gramática

Uma coisa só, ou duas que se relacionam. Objetos reais, não ícones inflados:
uma casa, uma escritura enrolada com fita, uma aliança, um carimbo, uma pasta,
uma chave. Pousados numa superfície, com sombra de luz difusa vindo de cima.

| | |
|---|---|
| **Fundo** | liso, da cor do `chao` do mundo do reel — e **nada mais** |
| **Material** | madeira fosca, papel, cera, metal escovado. Nada de plástico brilhante |
| **Paleta** | navy, creme e cobre. No máximo uma peça em cobre, e é a que carrega o ponto |
| **Luz** | uma fonte, de cima, difusa. Sombra macia e curta |
| **Ângulo** | levemente de cima, três quartos. Nunca em perspectiva dramática |
| **Formato** | quadrado, fundo transparente quando a ferramenta deixar (PNG) |

## O prompt base

Comece por este e troque só o objeto:

> A single `<objeto>` resting on a flat surface, 3D render, soft matte
> materials — wood, paper, wax. Muted palette: deep navy `#0F2540`, warm cream
> `#F5EFE4`, one copper accent `#B87333`. Single soft light from above, short
> diffuse shadow. Slight three-quarter top angle. Plain `<cor do chao>`
> background, nothing else in frame. Centered, generous empty margin.
> No text, no logos, no people, no hands.

Para duas peças que se relacionam, diga a relação em vez de listar as peças:
*"a wooden pawn and a house, connected by a thin copper ring"* funciona; *"a
pawn, a house and a ring"* devolve três objetos soltos.

## O que nunca pedir

- **Martelo de juiz, balança dourada, deusa da justiça.** São o clichê que a
  skill `reels-estilo` já proíbe em b-roll, e em 3D ficam piores.
- Robô, cérebro de circuito, holograma, rede neural flutuando.
- Texto dentro da imagem. Ele sai errado, sai em inglês, e o texto da cena é
  responsabilidade do componente — que sabe a fonte e o idioma certos.
- Pessoas, mãos, rostos. Quem aparece no reel é o Thiago.
- Mais de três objetos. A cena tem 300 px de altura: quatro peças viram sopa.

## Antes de usar

1. **Olhe em 300 px de altura**, que é o tamanho real na tela. Detalhe que só
   se lê a 100% não existe.
2. **Confira a paleta.** Se apareceu um azul-turquesa ou um dourado-amarelo,
   peça de novo — a imagem vai brigar com o resto do reel.
3. **Conte os elementos em cobre.** Mais de um e o acento deixa de significar.
4. Salve em `entrada/<job>/` com nome descritivo: `casa_doacao.png`, não
   `gen_0047.png`. O nome vai para o plano e alguém vai lê-lo daqui a um mês.

A regra que decide: **a imagem mostra alguma coisa, ou só ocupa espaço?** Vale
a mesma pergunta que a `reels-estilo` faz sobre b-roll. Na dúvida, a cena é
`card_conceito` e o reel não perde nada.
