---
name: reels-estilo
description: Identidade visual dos reels do Thiago (cores, tipografia, ícones, tom visual). Consultar SEMPRE antes de criar ou alterar qualquer cena Remotion, card, legenda ou elemento gráfico dos reels.
---

# Estilo visual dos reels

Conteúdo: IA aplicada ao Direito e aos negócios, falado por um especialista. O visual precisa transmitir rigor técnico e autoridade, não "criativo de anúncio". Referência mental: editorial de revista jurídica com animação limpa. Anti-referência: TikTok de marketing com glitch e neon.

## Tokens (fonte única: `motion/src/theme.ts`)

Nunca escreva cor, fonte ou tamanho direto num componente. Importe de `theme.ts`. Se o token não existir, crie-o lá antes de usar.

Paleta padrão (identidade AR). Se o vídeo for de outra marca, troque os valores em `theme.ts`, nunca nos componentes.

| Token | Valor | Uso |
|---|---|---|
| `navy` | `#0F2540` | fundo do painel de animação, texto principal sobre claro |
| `cobre` | `#B87333` | destaque: palavra-chave, seta ativa, número |
| `creme` | `#F5EFE4` | fundo de cards, texto sobre navy |
| `navySoft` | `#1C3A5E` | cards secundários, grades, conectores inativos |
| `creme60` | `rgba(245,239,228,0.6)` | texto de apoio, rótulos |

Proporção por cena: cerca de 70% navy, 25% creme, no máximo 5% cobre. Cobre é sinal, não decoração: no máximo um elemento cobre por cena.

## Tipografia

| Papel | Fonte | Peso | Tamanho base (1080 px de largura) |
|---|---|---|---|
| Título de cena, termo | Fraunces | 600 | 72 a 96 px |
| Corpo, itens de lista | Hanken Grotesk | 500 | 44 a 52 px |
| Rótulos de diagrama | Hanken Grotesk | 600, caixa alta, tracking 0.08em | 28 a 32 px |
| Números, artigos de lei, código | JetBrains Mono | 600 | 56 a 120 px |

Carregue as fontes com `@remotion/google-fonts` e aguarde o carregamento antes do primeiro frame. Nunca deixe fonte do sistema aparecer.

Escrita: português com acentuação completa. Maiúscula só no início da frase e em siglas (LGPD, CLT, STF, RAG, LLM). Sem emojis. Sem ponto final em títulos e itens curtos.

## Ícones e figuras

- Ícones de linha de `lucide-react`, `strokeWidth` 2, cor `creme` ou `cobre`. Um único estilo de ícone no vídeo inteiro.
- Preferir figuras próprias: diagramas de caixas e setas, linhas do tempo, tabelas de duas colunas, documentos estilizados.
- Documento jurídico estilizado: card creme, cabeçalho em JetBrains Mono ("Art. 7º, XIII"), corpo em linhas cinza, um trecho sublinhado em cobre.
- Proibido: imagem de banco (martelo de juiz, balança dourada, aperto de mão, robô azul), clip-art, emoji, ilustração 3D de plástico, logo de terceiros sem autorização.

## O que nunca fazer

- Glitch, neon, gradiente arco-íris, brilho pulsante, partículas, lens flare.
- Foto ou textura atrás de texto.
- Mais de duas famílias tipográficas visíveis na mesma cena.
- Sombra pesada. Máximo: `0 8px 24px rgba(0,0,0,0.25)` em cards.
- Raios misturados. Padrão: 20 px em cards, 999 px em pílulas.

## Checklist antes de renderizar

1. Todas as cores e fontes vêm de `theme.ts`.
2. No máximo um elemento cobre por cena.
3. Nenhum emoji, nenhuma imagem de banco.
4. Textos com acentuação correta e conferidos contra a transcrição.
