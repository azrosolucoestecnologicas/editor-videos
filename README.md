# Editor de Reels

Transforma o vídeo que você grava falando para a câmera num reel de tela dividida:

- **Cortes automáticos**: tira pausas longas e muletas (hã, hum) usando o tempo de cada palavra.
- **Legendas dinâmicas**: blocos curtos, com uma palavra-chave em destaque.
- **Tela dividida**: animações em cima, você embaixo, com o rosto enquadrado automaticamente.
- **Animações sincronizadas com a fala**: cada cena entra no momento exato em que a palavra que a chamou é dita.

Há **dois renderizadores** no projeto:

| | Renderizador | Definido em | Comando |
|---|---|---|---|
| **Atual** | Remotion (React) | `planos/*.scene_plan.json` | `python editar.py reel` |
| Antigo | Pillow (Python) | `roteiros/*.yaml` | `python editar.py renderizar` |

O caminho Remotion é o que produz o visual da identidade AR. O editor antigo
continua funcionando igual e está documentado na seção 6.

---

## 1. Instalação (uma vez só)

Você precisa de **Python 3.10+**, **FFmpeg** e **Node.js 20+**.

| Sistema | FFmpeg |
|---|---|
| Windows | `winget install Gyan.FFmpeg` (depois, feche e abra o terminal) |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |

Depois, dentro da pasta do projeto:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cd motion && npm install && npx remotion skills add && cd ..
```

O `npx remotion skills add` reinstala as Agent Skills oficiais do Remotion em
`motion/.agents/skills` (ficam fora do git; as versões estão fixadas em
`motion/skills-lock.json`).

---

## 2. O comando único

```bash
python editar.py reel "entrada/Black Friday/ROTEIRO 4.mp4" --assinatura "Thiago Azeredo"
```

Ele faz, em ordem:

1. **Transcreve e corta** — gera `entrada/<nome>_cortado.mp4` e a transcrição com os tempos já remapeados. Se o vídeo cortado já existir, essa etapa é pulada.
2. **Planeja as cenas** — escreve `planos/<nome>.scene_plan.json`, detecta o enquadramento do rosto e exporta as legendas e as props do Remotion.
3. **Valida** contra as skills (`reels-ritmo`, `reels-composicao`, `reels-legendas`). Erro aqui interrompe o processo; aviso só aparece no relatório.
4. **Renderiza** em `output/<nome>_final.mp4`.

Na primeira rodada de um vídeo novo, a etapa 3 vai parar com *"cena sem tipo"*:
o esqueleto marca **onde** cada cena entra, mas **o que** ela mostra é escrito
por quem entende o que foi dito. Abra o plano e preencha, ou peça ao Claude
(a fala de cada cena está no campo `_fala`). Depois rode o mesmo comando de novo.

Opções úteis:

```bash
--stills          # em vez do vídeo, um PNG por cena para conferir antes de renderizar
--previa          # metade da resolução, bem mais rápido
--detectar-rosto  # redetecta o enquadramento, descartando o ajuste manual
--refazer-cena c04  # devolve só a cena c04 ao planejador (pode repetir)
--refazer         # descarta TODAS as suas edições do plano e recalcula
--muletas ""      # não remove nenhuma muleta no corte
```

Para abrir a prévia interativa e mexer na composição:

```bash
cd motion && npx remotion studio
```

---

## 3. Como reeditar uma cena

O `planos/<nome>.scene_plan.json` é feito para ser editado à mão. Mude o que
quiser e rode `python editar.py reel ...` de novo: **o que você editou é
preservado e só o resto é recalculado.**

Funciona assim: cada cena guarda um `_hash` do conteúdo que o planejador
escreveu. Se o conteúdo não bate mais com esse hash, a cena foi editada e
passa a ser intocável (`"editado": true`).

### Mudar o texto de uma cena

```jsonc
{
  "id": "c06",
  "inicio": 24.553,
  "fim": 29.613,
  "palavra_gatilho": "Ela",
  "tipo": "card_conceito",
  "conteudo": {
    "termo": "Black Friday Vitalícia",      // <- mude aqui
    "definicao": "uma condição que não se repete"
  },
  "editado": true,
  "_fala": "Ela vai ter uma condição que não se repete...",  // referência, não aparece
  "_hash": "a1b2c3d4e5f6"
}
```

### Mudar o tempo

Edite `inicio` e `fim` (segundos no vídeo **já cortado**). Para manter a cena
grudada na fala, mude a `palavra_gatilho` em vez do tempo — o planejador
resolve a palavra para o segundo em que ela é dita e grava em `_em`.

Campos que começam com `_` são **derivados**: recalculados a cada rodada e
ignorados pelo hash. Não adianta editá-los.

### Trocar o tipo de cena

Troque `tipo` e reescreva `conteudo` no formato do novo tipo (tabela na seção 4).
O validador avisa se o formato não bater ou se o texto passar do limite.

### Voltar atrás numa cena

Editar o JSON **não** desfaz a marca de editado — qualquer mudança no arquivo é
justamente o que marca a cena. Para devolver uma cena ao planejador:

```bash
python editar.py reel entrada/X.mp4 --refazer-cena c04
```

### Corrigir o texto de uma legenda

Legenda não se edita no plano: ela é derivada da transcrição. Erro de
transcrição se corrige em **`glossario.json`** na raiz, que vale para todos os
vídeos (seção 5).

### Conferir sem renderizar

```bash
python editar.py validar-plano entrada/X_cortado.mp4   # só as regras
python editar.py reel entrada/X.mp4 --stills           # um PNG por cena
```

---

## 4. Os tipos de cena

Catálogo fechado, espelhando a skill `reels-composicao`. Tipo novo precisa
entrar na skill, em `editor/plano.py` (`CATALOGO`) e em `motion/src/scenes/`.

| `tipo` | `conteudo` | Limite |
|---|---|---|
| `card_conceito` | `termo`, `definicao` | definição até 12 palavras |
| `lista` | `titulo`, `itens: [{texto, palavra_gatilho}]` | 2 a 4 itens, 6 palavras cada |
| `comparacao` | `esquerda`/`direita`: `{titulo, linhas}` | até 3 linhas por coluna |
| `fluxo` | `etapas: [{rotulo, palavra_gatilho}]` | 3 a 5 etapas, rótulo até 3 palavras |
| `numero` | `valor`, `rotulo`, `palavra_gatilho` | rótulo até 6 palavras |
| `citacao_legal` | `referencia`, `trecho` | trecho até 20 palavras |
| `icone_destaque` | `icone`, `texto` | texto até 4 palavras |
| `sintese` | `frase` | até 10 palavras |

O `palavra_gatilho` dentro de um item ou etapa faz **aquele elemento** entrar
quando a palavra é dita — é assim que os itens de uma lista aparecem um a um.

Os nomes de ícone disponíveis estão em `motion/src/icones.ts`.

---

## 5. O glossário

`glossario.json` na raiz corrige o que a transcrição automática erra, em três
camadas:

```jsonc
{
  "palavras":   { "rague": "RAG", "prompet": "prompt" },        // uma palavra
  "expressoes": [{ "de": "ano direito", "para": "IA no Direito" }],  // várias palavras
  "muletas":    [{ "palavra": "tipo", "nao_remover_antes_de": ["de", "da"] }]
}
```

A comparação ignora acento, maiúscula e pontuação. `nao_remover_antes_de`
evita apagar o uso legítimo da palavra: em *"tipo de contrato"*, `tipo` fica.

Isso corrige a **grafia**, nunca o conteúdo. Se você errar um número na fala,
o glossário não conserta — é para ser sinalizado e regravado.

---

## 6. O editor antigo (Pillow)

Continua funcionando sem nenhuma mudança de comportamento. Use quando quiser
b-roll, zoom de ênfase ou um tipo de animação que o catálogo do Remotion ainda
não tem.

```bash
# 1) Coloque o vídeo na pasta entrada/
# 2) Cortes automáticos: tira pausas longas e muletas (hã, hum)
#    Gera entrada/meu_reels_cortado.mp4 + a transcrição já com os tempos ajustados
python editar.py cortar entrada/meu_reels.mp4

# 3) Crie o roteiro a partir do vídeo cortado (a transcrição entra como referência)
python editar.py novo entrada/meu_reels_cortado.mp4

# 3b) Edite roteiros/meu_reels_cortado.yaml com os eventos (ou peça ao Claude para fazer isso)

# 4) Confira em que segundo cada gatilho caiu
python editar.py eventos roteiros/meu_reels.yaml

# 5) Veja um quadro específico (PNG), rápido
python editar.py quadro roteiros/meu_reels.yaml 0:12.5

# 6) Prévia rápida (metade da resolução)
python editar.py renderizar roteiros/meu_reels.yaml --previa

# 7) Vídeo final em 1080x1920
python editar.py renderizar roteiros/meu_reels.yaml
```

Opções úteis:

- `cortar --pausa-max 0.5` deixa pausas de até 0,5 s (padrão: 0,35 s). `--margem 0.12` dá mais respiro antes e depois de cada fala. `--muletas "hã,hum,tipo"` troca a lista de muletas; `--muletas ""` não remove nenhuma. Os trechos mantidos ficam registrados em `entrada/<video>_cortado.cortes.json`.

- `--inicio 0:10 --fim 0:20` renderiza só um trecho.
- `python editar.py transcrever video.mp4 --modelo medium` usa um modelo mais preciso (o `small` é o padrão; `medium` e `large-v3` acertam mais, mas são mais lentos). Na primeira vez o modelo é baixado da internet para a pasta `modelos/` do projeto; depois disso funciona offline (inclusive no Cowork).
- Se a transcrição errar uma palavra, corrija direto no arquivo `entrada/<video>.transcricao.json` ou use `legendas.substituicoes` no roteiro.

---

## 7. O roteiro de edição (editor antigo)

```yaml
video: entrada/meu_reels.mp4
saida: saida/meu_reels_editado.mp4

legendas:
  estilo: destaque      # destaque | caixa | simples
  palavras_por_bloco: 3

divisao:
  proporcao: 0.5        # quanto da tela fica para a animação
  animacao_em: cima     # cima | baixo
  foco_rosto: 0.36      # onde está seu rosto no vídeo original (0 = topo, 1 = base)

eventos:
  - quando: "três erros"          # começa quando eu falar isso
    ate_quando: "seu negócio"     # e termina quando eu falar isso
    animacao:
      tipo: texto
      texto: "3 ERROS"
      emoji: "🚨"
```

### Quando um evento começa e termina

| Campo | Exemplo | Significado |
|---|---|---|
| `quando` | `"inteligência artificial"` | começa quando essa frase é falada (ignora acentos e maiúsculas e tolera pequenas diferenças) |
| `em` | `"0:12.5"` ou `12.5` | começa num tempo exato |
| `ocorrencia` | `2` | usa a 2ª vez que a frase aparece |
| `ajuste` | `-0.3` | adianta (negativo) ou atrasa o início, em segundos |
| `duracao` | `4` | dura 4 segundos (padrão: 3) |
| `ate` / `ate_quando` | `"0:20"` / `"frase"` | termina num tempo ou ao fim de uma frase |
| `layout` | `dividido` ou `cheio` | eventos com animação dividem a tela por padrão; `cheio` põe a animação sobre o vídeo |
| `zoom` | `{fator: 1.2}` | zoom de ênfase no rosto |

### Animações disponíveis

| `tipo` | Parâmetros | Uso |
|---|---|---|
| `texto` | `texto`, `subtitulo`, `emoji`, `tamanho` | frase de impacto com "pop" |
| `digitando` | `texto`, `titulo`, `velocidade` | efeito máquina de escrever (ótimo para prompts) |
| `lista` | `titulo`, `itens`, `numerada`, `marcador` | itens aparecem um a um. Cada item pode ter seu próprio `quando` |
| `passos` | igual à lista | lista numerada 1, 2, 3 |
| `comparacao` | `esquerda: {titulo, itens}`, `direita: {...}` | antes × depois, errado × certo |
| `contador` | `de`, `ate`, `prefixo`, `sufixo`, `casas`, `legenda` | número subindo (+300%, R$ 10.000) |
| `barras` | `titulo`, `barras: [{rotulo, valor}]`, `sufixo` | gráfico de barras crescendo |
| `progresso` | `valor` (0–100), `titulo`, `legenda` | barra de progresso |
| `icone` | `icone` (check, x, seta_cima, seta_baixo, alerta, pergunta, dinheiro) ou `emoji`, `texto` | ícone animado |
| `imagem` | `arquivo`, `titulo`, `zoom`, `preencher` | foto/print com zoom lento |
| `video` | `arquivo`, `inicio_arquivo`, `titulo`, `preencher` | vídeo de apoio (b-roll, gravação de tela) |

Veja `roteiros/exemplo.yaml` para um exemplo completo usando quase todas.

### Cores e fonte

```yaml
tema:
  fundo: ["#0b1020", "#1c2541"]  # gradiente do painel
  destaque: "#facc15"            # cor de destaque (legendas e títulos)
  secundaria: "#38bdf8"
  texto: "#ffffff"
  fonte: fontes/MinhaFonte.ttf   # opcional
```

---

## 8. Trabalhando junto com o Claude

1. Envie o vídeo para a pasta `entrada/` (ou me diga onde ele está).
2. Eu rodo `python editar.py novo entrada/seu_video.mp4` e te mostro a transcrição com os tempos.
3. Você me guia: *"quando eu falar 'três erros', mostra uma lista com os 3 erros"*, *"no 0:15 faz um zoom"*, *"quando eu falar trezentos por cento, faz um contador"*.
4. Eu escrevo o roteiro, confiro os quadros e gero o vídeo final.

## 9. Estrutura

```
editar.py              linha de comando
glossario.json         correções de termos da transcrição
editor/
  transcricao.py       transcrição com faster-whisper (tempo por palavra)
  cortes.py            cortes automáticos de pausas e muletas
  glossario.py         aplica o glossario.json às legendas
  plano.py             esqueleto do scene_plan, merge e validador das skills
  rosto.py             detecção do enquadramento (opencv)
  remotion.py          chamada do Remotion para stills e render
  roteiro.py           (editor antigo) leitura do YAML e gatilhos por frase
  legendas.py          (editor antigo) legendas em Pillow
  compositor.py        (editor antigo) tela dividida e montagem de cada quadro
  render.py            (editor antigo) leitura e gravação com FFmpeg
  animacoes/           (editor antigo) cada tipo de animação
motion/                projeto Remotion
  src/theme.ts         ÚNICA fonte de cores, fontes e medidas
  src/motion.ts        ÚNICA fonte das curvas de animação
  src/scenes/          um componente por tipo de cena
  src/Reel.tsx         as três faixas montadas
  public/              vídeos publicados para o Remotion (fora do git)
planos/                scene_plan.json, legendas e props de cada vídeo
roteiros/              roteiros do editor antigo (.yaml)
entrada/  saida/       seus vídeos (fora do git)
output/                render final e stills (fora do git)
fontes/                fontes do editor antigo (licença OFL)
```

As regras de estilo, ritmo, legenda, movimento e layout ficam nas skills em
`.claude/skills/`. Elas valem sobre qualquer coisa escrita aqui.
