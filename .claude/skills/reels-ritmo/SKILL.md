---
name: reels-ritmo
description: Regras de ritmo e sincronia dos reels do Thiago (quando entra cada cena, densidade visual, cortes, respiros). Consultar SEMPRE ao gerar ou revisar o scene_plan.json, ao cortar o vídeo bruto ou ao decidir o tempo de qualquer elemento animado.
---

# Ritmo dos reels

O ritmo é dado pela fala, não pela música. Cada elemento visual existe porque uma palavra o chamou. Se a animação entra antes ou depois da fala, o espectador sente o desencontro mesmo sem saber dizer o quê.

## Fonte de verdade do tempo

- Use a transcrição com timestamps por palavra (Whisper com `word_timestamps=True` ou equivalente). Sem timestamps por palavra, pare e gere-os antes de planejar cenas.
- Todo tempo no `scene_plan.json` é em segundos, relativo ao vídeo já cortado, nunca ao bruto.
- Converter para frames só dentro da composição: `Math.round(seg * fps)`.

## Sincronia

| Evento | Regra |
|---|---|
| Entrada de um elemento | 2 a 4 frames ANTES do início da palavra-gatilho (o olho chega antes do ouvido) |
| Item de lista | cada item entra na palavra que o nomeia, nunca todos juntos |
| Número animado | o contador termina exatamente quando o número é falado |
| Saída da cena | começa 6 a 10 frames antes da próxima cena entrar; nunca corte seco entre cenas animadas |

## Densidade

- Uma mudança visual a cada 3 a 6 segundos. Mais rápido que 2 s cansa; mais lento que 8 s parece parado.
- Dentro de uma cena, no máximo 3 elementos entrando em sequência.
- Abertura (0 a 3 s): a primeira cena precisa estar na tela até 0,5 s. É o gancho; nada de tela vazia.
- Fechamento: os últimos 1,5 s ficam com uma cena-síntese estática (a ideia central em uma frase), sem animação nova.

## Respiro

- Pausa de fala acima de 0,6 s no vídeo cortado é erro de corte: reduza para 0,15 a 0,25 s.
- Não remova toda pausa. Mantenha 0,3 a 0,5 s depois de uma afirmação importante ou de uma pergunta retórica: é aí que a ideia assenta.
- Respiração audível no início de frase: corte. Riso ou ênfase intencional: mantenha.

## O que nunca fazer

- Animação que entra sem palavra-gatilho na transcrição.
- Duas cenas animadas mudando ao mesmo tempo nas duas metades da tela.
- Cena que dura menos de 1,5 s (ninguém lê).
- Jump cut no rosto a cada frase. Se houver muitos cortes seguidos, alterne com um zoom leve (ver `reels-movimento`) para disfarçar.

## Checklist do scene_plan.json

1. Cada cena tem `palavra_gatilho` que existe literalmente na transcrição.
2. Nenhum intervalo sem cena maior que 8 s.
3. Nenhuma cena menor que 1,5 s.
4. Abertura com cena até 0,5 s; fechamento com cena-síntese.
