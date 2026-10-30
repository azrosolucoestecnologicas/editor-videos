---
name: reels-briefing
description: Como começar um reel a partir de um vídeo na pasta entrada/ — o que perguntar ao Thiago antes de editar, em que ordem rodar o pipeline e quando parar para mostrar. Consultar SEMPRE que ele disser que pôs um vídeo na entrada, pedir para editar um vídeo, ou mandar começar um reel novo.
---

# Começar um reel

O Thiago põe uma pasta em `entrada/` com o vídeo e as imagens que quer usar. A
partir daí a edição é uma conversa: o pipeline corta e planeja, mas **o conteúdo
de cada cena é escrito por quem entendeu o que foi dito** — nunca por heurística.

## 1. Olhe antes de perguntar

```bash
python editar.py entrada
```

Mostra cada job, a duração, as imagens que estão na pasta e qual é o próximo
passo. Rode isto **antes** de perguntar qualquer coisa: metade do briefing já
está no disco, e perguntar o que dá para ver é desperdício do tempo dele.

## 2. Pergunte uma vez só, com os padrões escritos

Uma mensagem, não um interrogatório. Pergunte **apenas o que muda o vídeo**, e
diga o que você vai assumir se ele não responder:

- **A ideia única.** O que a pessoa tem que levar embora se lembrar de uma coisa
  só. Sem isso não há como escolher quais falas viram cena e quais são passagem.
  É a única pergunta sem padrão: não invente a tese dele.
- **As imagens.** Liste as que achou na pasta, pelo nome, e pergunte onde cada
  uma entra — ou se são só referência. *Padrão: não uso nenhuma.*
- **Duração.** *Padrão: o que a fala der depois de cortadas as pausas.* Se ele
  pedir um alvo, é corte de conteúdo, não aceleração: escolha as falas que saem.
- **Assinatura** no canto. *Padrão: vazio.*
- **O que não pode aparecer** — um número que ele errou na fala, um nome de
  cliente, um dado que não pode ir ao ar. *Padrão: nada.*

Não pergunte formato (é sempre 1080x1920, 30 fps), nem paleta, nem tipografia,
nem estilo de legenda: isso está nas skills e é a identidade dele, não uma
escolha por vídeo.

## 3. Rode o pipeline

```bash
python editar.py reel "entrada/<pasta>/<video>.mp4"
```

Corta as pausas e as muletas, planeja as cenas, valida contra as skills. Ele vai
parar com erro listando as cenas sem tipo — **isso é o esperado**, é o seu
trabalho que começa aí.

## 4. Escreva as cenas

Abra `planos/<nome>_cortado.scene_plan.json`. Cada cena tem a fala dela em
`_fala`. Preencha `tipo` e `conteudo` conforme o catálogo de
[reels-composicao](../reels-composicao/SKILL.md), com o ritmo de
[reels-ritmo](../reels-ritmo/SKILL.md).

- Nem toda fala vira cena. Fala de passagem é passagem; cena demais vira ruído.
- Campos com prefixo `_` são derivados: não os edite, são recalculados.
- Para devolver uma cena ao planejador: `--refazer-cena c05`.
- Se o `validar` avisar que a fala-gatilho mudou, confira se o texto que você
  escreveu ainda comenta o que está sendo dito naquele ponto.

## 5. Confira antes de renderizar

```bash
python editar.py reel "entrada/<pasta>/<video>.mp4" --stills
```

Um PNG por cena, em segundos em vez de minutos. **Olhe cada um** e só depois
renderize. Render completo para conferir layout é desperdício de minutos dele.

Mostre os stills ao Thiago antes do render final. Ele corrige em português —
*"a cena 3 está cedo demais"*, *"troca essa lista por um número"* — e você refaz
só aquela cena.

## 6. Renderize

```bash
python editar.py reel "entrada/<pasta>/<video>.mp4"
```

Sai em `output/<nome>_final.mp4`. Diga onde ficou, quanto tempo tem, e o que
mudou em relação ao que ele pediu — se mudou.

## O que nunca fazer

- **Inventar número, nome, data ou citação.** Tudo que aparece na tela saiu da
  fala dele ou de uma imagem que ele deu. Se a fala errou um número, sinalize e
  peça para regravar: o glossário corrige grafia, nunca conteúdo.
- **Encher as cenas sozinho para o validador passar.** Um plano que valida e diz
  a coisa errada é pior que um plano incompleto.
- **Renderizar sem olhar os stills.**
