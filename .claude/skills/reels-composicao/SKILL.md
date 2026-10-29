---
name: reels-composicao
description: Layout e camadas dos reels do Thiago (tela dividida, grid, margens, zonas seguras, catálogo de tipos de cena). Consultar SEMPRE ao montar a composição Remotion, criar um novo tipo de cena ou posicionar qualquer elemento na tela.
---

# Composição dos reels

Formato fixo: 1080x1920, 30 fps. Uma composição principal com camadas fixas; as cenas só preenchem o painel de animação.

## Layout de tela dividida

| Faixa | Altura (px) | Conteúdo |
|---|---|---|
| Painel de animação | 0 a 900 | cenas do `scene_plan.json`, fundo `navy` |
| Divisória | 900 a 1040 | legenda (ver `reels-legendas`) sobre faixa `navy` |
| Vídeo | 1040 a 1920 | o Thiago, recortado em cover, rosto centralizado |

- A proporção pode virar 50/50 (960/960) se o conteúdo da cena for denso, mas fica igual no vídeo inteiro.
- Momentos sem cena relevante (introdução pessoal, chamada final): o vídeo ocupa a tela inteira, com transição de 12 frames e a legenda descendo para a zona segura inferior. No máximo 2 desses momentos por reel.

## Zonas seguras

- Margem lateral do painel: 72 px.
- Topo: nada importante acima de 120 px (barra do Instagram).
- Lateral direita inferior: 140 px livres (botões de curtir, comentar, compartilhar).

## Camadas (de baixo para cima)

1. Fundo `navy` do painel.
2. Grade sutil opcional: linhas `navySoft` com 30% de opacidade, espaçamento 72 px.
3. Cena atual.
4. Vídeo do Thiago.
5. Legenda.
6. Assinatura discreta: nome ou logo em `creme60`, 28 px, canto superior esquerdo do painel, fixa o vídeo todo.

## Catálogo de cenas (fechado)

Cada tipo é um componente em `motion/src/scenes/`. Não invente tipo novo sem acrescentá-lo aqui primeiro.

| Tipo | Quando usar | Limite |
|---|---|---|
| `card_conceito` | definir um termo | termo + até 12 palavras de definição |
| `lista` | enumeração falada | 2 a 4 itens, até 6 palavras cada |
| `comparacao` | antes/depois, humano/IA, certo/errado | 2 colunas, até 3 linhas cada |
| `fluxo` | processo, pipeline, arquitetura de agente | 3 a 5 caixas, rótulos de até 3 palavras |
| `numero` | estatística, prazo, valor | 1 número + rótulo de até 6 palavras |
| `citacao_legal` | artigo, súmula, tese | referência + trecho de até 20 palavras |
| `icone_destaque` | ideia-chave sem estrutura | 1 ícone + até 4 palavras |
| `sintese` | fechamento | 1 frase de até 10 palavras |

## Hierarquia dentro da cena

- Um ponto focal por cena. Se houver dois, a cena está errada: divida em duas.
- Alinhamento à esquerda para listas e textos; centralizado só em `numero`, `icone_destaque` e `sintese`.
- Espaçamento vertical entre elementos: 32 px (relacionados) ou 64 px (blocos distintos).
- Ocupe no máximo 70% da área do painel; o vazio faz parte do desenho.

## Fidelidade

- Todo texto de cena sai do que foi dito. Não invente dado, número, artigo de lei ou citação. Se a fala for vaga, a cena é `icone_destaque`, não `numero`.
- `citacao_legal` só com texto conferido na fonte; na dúvida, mostre só a referência ("Art. 7º, XIII, CF") sem transcrever o dispositivo.

## Checklist antes do render final

1. Gerar stills (`npx remotion still`) de 4 a 6 frames-chave e conferir.
2. Nada fora das zonas seguras.
3. Um ponto focal por cena.
4. Todos os tipos de cena pertencem ao catálogo.
