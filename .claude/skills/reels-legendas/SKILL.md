---
name: reels-legendas
description: Padrão das legendas dos reels do Thiago (quebra, tamanho, posição, níveis de ênfase, revisão de termos jurídicos e técnicos). Consultar SEMPRE ao gerar, estilizar, posicionar ou revisar legendas.
---

# Legendas dos reels

A legenda carrega a fala para quem assiste sem som. Ela não compete com a
animação: a animação mostra o conceito, a legenda mostra a frase.

## O que mudou da v1

A v1 tinha a legenda numa faixa de divisória e **uma** palavra destacada em
acento por bloco. Com o layout novo não existe mais divisória, e um único nível
de ênfase deixa a legenda monótona num reel de 50 segundos. A v2 move a legenda
para a zona segura inferior e cria **três níveis** de ênfase, com cota.

## Posição e tamanho (1080x1920)

- Sobre o vídeo, centralizada, com o centro em **1620 px**: acima dos 1740 px
  da zona segura inferior e longe dos botões do Instagram (lateral direita,
  140 px).
- Fonte: Hanken Grotesk 700, 54 a 60 px.
- Contorno de 6 px em `contorno`, sempre: agora a legenda fica sobre a imagem, não
  sobre fundo chapado.
- No máximo 2 linhas e 28 caracteres por linha.

## Quebra

- Quebre por unidade de sentido, nunca no meio de expressão: "Súmula 331" e
  "Art. 7º" ficam juntos; artigo, preposição e número ficam com a palavra
  seguinte.
- Bloco de 2 a 5 palavras por vez, sincronizado palavra a palavra com os
  timestamps.
- Duração mínima de um bloco na tela: 0,6 s.

## Níveis de ênfase

| Nível | Aparência | Cota |
|---|---|---|
| Normal | creme fixo | o resto do bloco |
| Chave | `acento` | no máximo 1 por bloco |
| Máxima | creme sobre pílula `acento`, raio 999 px, padding 8/20 px | no máximo **3 por reel inteiro** |

O que merece cada nível:

- **Chave**: número, sigla técnica (RAG, LGPD, LLM), negação decisiva ("não",
  "nunca", "sem").
- **Máxima**: a palavra que você quer que apareça no print que alguém manda
  para um colega. Normalmente o nome da oferta, o prazo ou o número que decide.
  Três por reel é cota rígida: a quarta tira o peso das outras três.

Cada palavra também dá um pop ao ser falada: `scale` 1,00 para 1,04 em 4 frames
e volta. É pop, não balanço — nada de rotação, nada de salto vertical.

## Revisão obrigatória de termos

A transcrição automática erra justamente o vocabulário que dá autoridade ao
vídeo. Antes de renderizar, confira e corrija:

| Erro comum | Forma correta |
|---|---|
| "rag", "rague" | RAG |
| "cloud", "clode" | Claude |
| "LGPD" soletrado ou "lei geral" truncado | LGPD |
| "TST", "TRT" em minúscula | TST, TRT-3 |
| "artigo sétimo, inciso treze" | Art. 7º, XIII |
| "súmula trezentos e trinta e um" | Súmula 331 |
| "prompt", "prompti" | prompt |
| "LLM", "elemente" | LLM |

- Números de lei, súmula, processo e valores sempre em algarismos.
- Mantenha um arquivo `glossario.json` no projeto com as correções; aplique-o
  automaticamente e acrescente os erros novos que aparecerem.
- Nunca "corrija" o conteúdo do que foi dito. Se o Thiago errou um número na
  fala, sinalize para ele em vez de mudar a legenda em silêncio.

## O que nunca fazer

- Legenda repetindo palavra por palavra o texto que está no card animado ao
  mesmo tempo (escolha um dos dois).
- Legenda em caixa alta inteira.
- Mais de um nível "máxima" no mesmo bloco.
- Cor fora da paleta: a ênfase é `acento` e creme, não verde, vermelho ou amarelo.
- Emojis inseridos automaticamente.
- Palavras de preenchimento ("né", "tipo", "assim") na legenda: remova da
  legenda mesmo que fiquem no áudio.
