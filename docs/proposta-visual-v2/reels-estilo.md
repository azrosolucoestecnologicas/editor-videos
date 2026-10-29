---
name: reels-estilo
description: Identidade visual dos reels do Thiago (cores, metal, tipografia, ícones, tom visual). Consultar SEMPRE antes de criar ou alterar qualquer cena Remotion, card, legenda ou elemento gráfico dos reels.
---

# Estilo visual dos reels

Conteúdo: IA aplicada ao Direito e aos negócios, falado por um especialista. O
visual precisa transmitir rigor técnico e autoridade, não "criativo de anúncio".
Referência mental: editorial de revista jurídica **com acabamento de produto**
— metal escovado, vidro fosco, luz que vem do ambiente. Anti-referência, sem
mudança: TikTok de marketing com glitch e neon.

## O que mudou da v1

A v1 proibia todo gradiente e limitava a sombra a `0 8px 24px`. Isso garantia
sobriedade, mas também garantia que nada tivesse volume: tudo ficava chapado.
A v2 libera **gradiente monocromático** e **sombra de objeto flutuante**, que
são o que dá acabamento. Continua proibido tudo que é barulho: neon, arco-íris,
glitch, partícula, brilho pulsante.

## Tokens (fonte única: `motion/src/theme.ts`)

Nunca escreva cor, fonte ou tamanho direto num componente. Importe de
`theme.ts`. Se o token não existir, crie-o lá antes de usar.

| Token | Valor | Uso |
|---|---|---|
| `navy` | `#0F2540` | base escura, véu sobre o fundo vivo |
| `cobre` | `#B87333` | destaque: palavra-chave, seta ativa, número |
| `creme` | `#F5EFE4` | texto sobre escuro, fundo de card de citação |
| `navySoft` | `#1C3A5E` | corpo dos cards, grades, conectores inativos |
| `creme60` | `rgba(245,239,228,0.6)` | texto de apoio, rótulos |
| `veu` | `rgba(15,37,64,0.72)` | **novo**: véu sobre o fundo vivo |
| `vidro` | `rgba(28,58,94,0.55)` | **novo**: corpo de card translúcido |

### Metal

| Token | Valor |
|---|---|
| `metal.borda` | `linear-gradient(135deg, #B87333, #E8D5BC, #B87333)` |
| `metal.face` | `linear-gradient(180deg, rgba(255,255,255,0.06), rgba(0,0,0,0.10))` |
| `metal.brilho` | `linear-gradient(105deg, transparent 40%, rgba(245,239,228,0.22) 50%, transparent 60%)` |

A borda metálica é um fio de **1,5 px**. Acima disso vira moldura de convite de
casamento.

## A regra do cobre

Esta é a regra que mais se quebra sozinha quando se libera metal, então ela
muda de forma:

- **Cobre como preenchimento** (número, ícone, pílula, texto): no máximo **um
  por cena**. Continua valendo igual à v1.
- **Cobre como fio** (borda metálica de 1,5 px): pode estar em todos os cards
  da cena. Lê como material, não como sinal.

Se você não consegue dizer qual é o único elemento cobre preenchido da cena, a
cena tem cobre demais.

Proporção por cena: cerca de 70% escuro, 25% creme, no máximo 5% cobre.

## Sombra e profundidade

| Situação | Sombra |
|---|---|
| Card flutuando sobre o vídeo | `0 24px 60px rgba(0,0,0,0.45)` |
| Elemento dentro de um card | `0 4px 12px rgba(0,0,0,0.20)` |
| Texto solto sobre o fundo vivo | nenhuma; use contorno |

A sombra do card flutuante é maior que na v1 **de propósito**: é ela que faz o
card parecer estar no ambiente em vez de colado na tela. Sem ela, o resto da
profundidade não convence.

## Tipografia

| Papel | Fonte | Peso | Tamanho base (1080 px de largura) |
|---|---|---|---|
| Título de cena, termo | Fraunces | 600 | 72 a 96 px |
| Corpo, itens de lista | Hanken Grotesk | 500 | 44 a 52 px |
| Rótulos de diagrama | Hanken Grotesk | 600, caixa alta, tracking 0.08em | 28 a 32 px |
| Números, artigos de lei, código | JetBrains Mono | 600 | 56 a 120 px |

Carregue as fontes com `@remotion/google-fonts` e aguarde o carregamento antes
do primeiro frame. Nunca deixe fonte do sistema aparecer.

Escrita: português com acentuação completa. Maiúscula só no início da frase e
em siglas (LGPD, CLT, STF, RAG, LLM). Sem emojis. Sem ponto final em títulos e
itens curtos.

## Ícones e figuras

- Ícones de linha de `lucide-react`, `strokeWidth` 2, cor `creme` ou `cobre`.
  Um único estilo de ícone no vídeo inteiro.
- Preferir figuras próprias: diagramas de caixas e setas, linhas do tempo,
  tabelas de duas colunas, documentos estilizados.
- Documento jurídico estilizado: card creme, cabeçalho em JetBrains Mono
  ("Art. 7º, XIII"), corpo em linhas cinza, um trecho sublinhado em cobre.

## B-roll

Liberado como `cena_apoio`, com limites (ver `reels-composicao`). O que entra e
o que não entra:

| Serve | Não serve |
|---|---|
| filmagem sua, do escritório, das mãos, da tela | robô, androide, cérebro de circuito |
| documento real sendo folheado | martelo de juiz, balança dourada |
| gravação de tela do seu fluxo de trabalho | aperto de mão corporativo genérico |
| fachada de tribunal, filmagem real | "juiz" ou "advogado" de banco de imagem posando |

O critério: **a imagem mostra alguma coisa, ou só ocupa espaço?** Se um
espectador advogado reconhece a cena como clichê de banco de imagem, ela tira
autoridade em vez de dar.

Material gerado por IA segue o mesmo critério e precisa ser bom o bastante para
não ser identificado como gerado. Na dúvida, não use.

## O que nunca fazer

- Glitch, neon, gradiente arco-íris, brilho pulsante, partículas, lens flare.
- Gradiente entre matizes diferentes. Os permitidos são monocromáticos:
  cobre-creme-cobre e claro-escuro da mesma cor.
- Foto ou textura atrás de texto que não seja o fundo vivo desfocado.
- Mais de duas famílias tipográficas visíveis na mesma cena.
- Raios misturados. Padrão: 20 px em cards, 999 px em pílulas.
- **Logo de terceiros sem autorização.** Inclui o símbolo do Claude, da
  Anthropic, da OpenAI e de qualquer ferramenta. São marcas registradas e o
  vídeo é promocional.

## Checklist antes de renderizar

1. Todas as cores e fontes vêm de `theme.ts`.
2. Dá para apontar o único elemento cobre preenchido da cena.
3. Fio metálico com no máximo 1,5 px.
4. Nenhum emoji, nenhuma imagem de banco, nenhum logo de terceiro.
5. Textos com acentuação correta e conferidos contra a transcrição.
