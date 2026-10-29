---
name: reels-legendas
description: Padrão das legendas dos reels do Thiago (quebra, tamanho, posição, destaque de palavra, revisão de termos jurídicos e técnicos). Consultar SEMPRE ao gerar, estilizar, posicionar ou revisar legendas.
---

# Legendas dos reels

A legenda carrega a fala para quem assiste sem som. Ela não compete com a animação: a animação mostra o conceito, a legenda mostra a frase.

## Posição e tamanho (1080x1920)

- Na faixa da divisória entre animação e vídeo, centralizada, em zona segura: nunca a menos de 180 px da borda inferior nem sob os botões da interface do Instagram (lateral direita, 140 px).
- Fonte: Hanken Grotesk 700, 54 a 60 px, cor `creme`, contorno de 6 px em `navy` ou caixa `navy` com 85% de opacidade e raio 14 px.
- No máximo 2 linhas e 28 caracteres por linha.

## Quebra

- Quebre por unidade de sentido, nunca no meio de expressão: "Súmula 331" e "Art. 7º" ficam juntos; artigo, preposição e número ficam com a palavra seguinte.
- Bloco de 2 a 5 palavras por vez, sincronizado palavra a palavra com os timestamps.
- Duração mínima de um bloco na tela: 0,6 s.

## Destaque

- Uma palavra destacada por bloco, no máximo: a palavra-chave da frase (termo técnico, número, negação decisiva como "não").
- Destaque = cor `cobre` + escala 1,06. Nada de emoji, fundo colorido por palavra ou balanço.
- Se a palavra destacada for o gatilho de uma cena, o destaque e a entrada da cena acontecem no mesmo frame.

## Revisão obrigatória de termos

A transcrição automática erra justamente o vocabulário que dá autoridade ao vídeo. Antes de renderizar, confira e corrija:

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
- Mantenha um arquivo `glossario.json` no projeto com as correções; aplique-o automaticamente e acrescente os erros novos que aparecerem.
- Nunca "corrija" o conteúdo do que foi dito. Se o Thiago errou um número na fala, sinalize para ele em vez de mudar a legenda em silêncio.

## O que nunca fazer

- Legenda repetindo palavra por palavra o texto que está no card animado ao mesmo tempo (escolha um dos dois).
- Legenda em caixa alta inteira.
- Emojis inseridos automaticamente.
- Palavras de preenchimento ("né", "tipo", "assim") na legenda: remova da legenda mesmo que fiquem no áudio.
