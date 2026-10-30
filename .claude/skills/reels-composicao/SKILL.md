---
name: reels-composicao
description: Layout e camadas dos reels do Thiago (sobreposição com profundidade, grid, margens, zonas seguras, catálogo de tipos de cena). Consultar SEMPRE ao montar a composição Remotion, criar um novo tipo de cena ou posicionar qualquer elemento na tela.
---

# Composição dos reels

Formato fixo: 1080x1920, 30 fps. Uma composição principal com camadas fixas; as
cenas só preenchem a zona de cenas.

## O que mudou da v1 e por quê

A v1 dividia a tela em duas caixas coladas: painel navy chapado em cima, vídeo
embaixo, emenda reta em 900 px. Três problemas:

- A emenda reta é a marca visual de "duas coisas coladas". É ela, não a cor,
  que faz o reel parecer amador.
- O navy chapado não tem profundidade nenhuma.
- Os gráficos ignoravam a luz do cenário, que muda de cor ao longo da gravação.

A v2 resolve os três com um recurso só: **o fundo da zona de cenas é o próprio
vídeo**, ampliado, desfocado e escurecido. A luz do palco vaza para o fundo
sozinha, a emenda vira um degradê e os cards passam a flutuar dentro do
ambiente em vez de morar numa caixa separada.

## Camadas (de baixo para cima)

| # | Camada | Faixa (px) | O que é |
|---|---|---|---|
| 1 | Fundo vivo | 0 a 1920 | o próprio vídeo, escala 2,2x, desfocado, escurecido a 0,45 |
| 2 | Véu | 0 a 1010 | `veu`, para o texto ter contraste |
| 3 | Grade | 0 a 1010 | linhas `reforco` a 20%, espaçamento 72 px |
| 4 | Vídeo nítido | 1010 a 1920 | você, reenquadrado no rosto, com degradê de 150 px no topo |
| 5 | Cenas | 150 a 860 | os cards do `scene_plan.json` |
| 6 | Legenda | centro em 1620 | sobre o vídeo, na zona segura inferior |
| 7 | Assinatura | 120 | nome em `tintaFraca`, 28 px, canto superior esquerdo |
| 8 | Aviso | 120 | pílula fixa, centralizada, acima de tudo (ver abaixo) |

O degradê no topo da camada 4 é o que substitui a emenda: o vídeo nítido
dissolve no desfocado em 150 px. **Nunca existe uma linha reta separando as
duas metades.**

## O aviso fixo

O campo `aviso` do plano põe uma pílula no topo pelo **reel inteiro** — não é
cena, não entra nem sai. Um aviso que aparece só num trecho não avisa quem
assistiu o resto.

Para conteúdo jurídico ele não é enfeite: é o que separa informar de parecer
dar consultoria. Texto curto, numa linha: *"Conteúdo informativo · não é
consultoria jurídica"*. Quando há aviso, a assinatura desce sozinha.

## Enquadramento do rosto

O centro do rosto fica em **1240 px** (um terço do alto da faixa nítida). No
material atual o rosto está a 28% da altura do arquivo, então o vídeo desce
cerca de 600 px — o que sobra em cima é justamente onde o fundo vivo trabalha.

Nunca deixe o rosto acima de 1100 px: a partir daí ele disputa espaço com os
cards.

## Zonas seguras

- Margem lateral: 72 px.
- Topo: nada importante acima de 120 px (barra do Instagram).
- Base: nada importante abaixo de 1740 px.
- Lateral direita inferior: 140 px livres (curtir, comentar, compartilhar).

## Profundidade

Card não é um retângulo colado na tela: é um objeto no ambiente.

- Entra com perspectiva leve: `rotateY` de -6° a 0° e `scale` de 0,96 a 1.
- Sombra projetada de verdade, com o limite ampliado da `reels-estilo`.
- `perspective: 1400px` no contêiner da zona de cenas, nunca no card.
- Cards de uma mesma cena ficam no mesmo plano. Nada de um na frente do outro.

## Catálogo de cenas (fechado)

Cada tipo é um componente em `motion/src/scenes/`. Não invente tipo novo sem
acrescentá-lo aqui primeiro.

| Tipo | Quando usar | Limite |
|---|---|---|
| `card_conceito` | definir um termo | termo + até 12 palavras de definição |
| `lista` | enumeração falada | 2 a 4 itens, até 6 palavras cada |
| `comparacao` | antes/depois, humano/IA, certo/errado | 2 colunas, até 3 linhas cada |
| `fluxo` | processo, pipeline, arquitetura de agente | 3 a 5 caixas, rótulos de até 3 palavras |
| `numero` | estatística, prazo, valor | 1 número + rótulo de até 6 palavras |
| `citacao_legal` | artigo, súmula, tese | referência + trecho de até 20 palavras |
| `icone_destaque` | ideia-chave sem estrutura | 1 ícone + até 4 palavras |
| `documento` | cláusulas de um instrumento | título + 2 a 4 cláusulas de até 5 palavras |
| `objeto` | metáfora concreta | 1 imagem + título de até 8 palavras |
| `cena_apoio` | b-roll ilustrando a fala | 1 clipe + rótulo de até 5 palavras |
| `sintese` | fechamento | 1 frase de até 10 palavras, com `chave` opcional |

`objeto` mostra **a coisa** de que a fala trata — a casa, o selo, a balança —
em vez de descrevê-la num card. A imagem não vem de código: é um arquivo que o
Thiago gera e deixa na pasta do job, em `entrada/<job>/`, e que o
`exportar_props` publica sozinho. Escreva no plano o nome do arquivo como ele
está na pasta.

O guia de prompt para gerar essas imagens está em
[reels-ilustracao](../reels-ilustracao/SKILL.md). Imagem fora daquela gramática
estraga mais do que ajuda: um render 3D genérico tira autoridade igual a foto
de banco de imagem.

`documento` não é uma `lista` com outro nome. A lista **enumera ideias**; o
documento mostra **um papel que existe** e o que está escrito nele — escritura,
contrato, procuração. Por isso ele tem selo, título em mono caixa-alta e card
preenchido. Se a fala não se refere a um instrumento concreto, é `lista`.

A cláusula que acabou de entrar fica no acento e as anteriores recuam para
checada — um acento preenchido por instante, como manda `reels-estilo`.

Em `sintese`, o campo `chave` sublinha **uma** palavra da frase no acento. Ela
precisa aparecer na frase (o validador cobra): é justamente quando alguém
reescreve a frase e esquece a chave que o sublinhado sumiria calado.

### `cena_apoio`

O clipe ocupa a zona de cenas inteira, com os mesmos cantos e a mesma sombra de
um card — é um card cujo conteúdo é vídeo, não um corte para tela cheia.

- Duração de 2 a 4 s — janela própria, diferente dos 3 a 6 s das outras.
  Mais que isso e o reel vira vídeo de banco. O validador avisa.
- No máximo **2 por reel**, nunca seguidas. As duas regras são erro no
  validador, não aviso: b-roll demais deixa de ser reel dele.
- Entra e sai com os mesmos presets das outras cenas, sem corte seco.
- Mudo, sempre: o áudio é a sua fala. O componente força isso.
- O clipe fica em `entrada/<job>/` e o `exportar_props` publica sozinho,
  igual às imagens do `objeto`.
- Vale a regra de fidelidade da `reels-estilo`: filmagem real, nada de robô,
  martelo ou juiz genérico.

## Hierarquia dentro da cena

- Um ponto focal por cena. Se houver dois, a cena está errada: divida em duas.
- Alinhamento à esquerda para listas e textos; centralizado só em `numero`,
  `icone_destaque` e `sintese`.
- Espaçamento vertical: 32 px (relacionados) ou 64 px (blocos distintos).
- Ocupe no máximo 70% da zona de cenas; o vazio faz parte do desenho.

## Fidelidade

- Todo texto de cena sai do que foi dito. Não invente dado, número, artigo de
  lei ou citação. Se a fala for vaga, a cena é `icone_destaque`, não `numero`.
- `citacao_legal` só com texto conferido na fonte; na dúvida, mostre só a
  referência ("Art. 7º, XIII, CF") sem transcrever o dispositivo.

## Checklist antes do render final

1. Gerar stills de 4 a 6 frames-chave e conferir.
2. Nenhuma linha reta separando o vídeo do fundo.
3. Nada fora das zonas seguras; rosto abaixo de 1100 px.
4. Um ponto focal por cena.
5. No máximo 2 `cena_apoio`, nunca seguidas.
6. Todos os tipos de cena pertencem ao catálogo.
