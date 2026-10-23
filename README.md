# Editor de Reels

Edita automaticamente os Reels que você grava no celular:

- **Legendas dinâmicas**: blocos curtos com a palavra falada em destaque, gerados a partir da transcrição.
- **Tela dividida**: a tela se divide com uma transição suave. As animações ficam em cima e você aparece embaixo, com o rosto enquadrado.
- **Animações sincronizadas com a fala**: você diz *"quando eu falar X, mostra Y"* e a animação entra no momento exato em que a frase foi dita.
- **Zoom de ênfase** no rosto, imagens, prints e vídeos de apoio (b-roll).

Tudo é definido num **roteiro de edição** (arquivo `.yaml`) bem simples de ler e de editar.

---

## 1. Instalação (uma vez só)

Você precisa de **Python 3.10+** e do **FFmpeg**.

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
```

Para testar a instalação sem gravar nada:

```bash
python exemplos/gerar_demo.py
python editar.py renderizar roteiros/exemplo.yaml --previa
```

O resultado fica em `saida/demo_editado_previa.mp4`.

---

## 2. Fluxo de trabalho

```bash
# 1) Coloque o vídeo na pasta entrada/
# 2) Crie o roteiro (já transcreve o vídeo e coloca a transcrição como referência)
python editar.py novo entrada/meu_reels.mp4

# 3) Edite roteiros/meu_reels.yaml com os eventos (ou peça ao Claude para fazer isso)

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

- `--inicio 0:10 --fim 0:20` renderiza só um trecho.
- `python editar.py transcrever video.mp4 --modelo medium` usa um modelo mais preciso (o `small` é o padrão; `medium` e `large-v3` acertam mais, mas são mais lentos). Na primeira vez o modelo é baixado da internet.
- Se a transcrição errar uma palavra, corrija direto no arquivo `entrada/<video>.transcricao.json` ou use `legendas.substituicoes` no roteiro.

---

## 3. O roteiro de edição

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

## 4. Trabalhando junto com o Claude

1. Envie o vídeo para a pasta `entrada/` (ou me diga onde ele está).
2. Eu rodo `python editar.py novo entrada/seu_video.mp4` e te mostro a transcrição com os tempos.
3. Você me guia: *"quando eu falar 'três erros', mostra uma lista com os 3 erros"*, *"no 0:15 faz um zoom"*, *"quando eu falar trezentos por cento, faz um contador"*.
4. Eu escrevo o roteiro, confiro os quadros e gero o vídeo final.

## Estrutura

```
editar.py              linha de comando
editor/
  roteiro.py           leitura do YAML e gatilhos por frase
  transcricao.py       transcrição com faster-whisper (tempo por palavra)
  legendas.py          legendas dinâmicas
  compositor.py        tela dividida, zoom e montagem de cada quadro
  render.py            leitura e gravação do vídeo com FFmpeg
  animacoes/           cada tipo de animação
roteiros/              roteiros de edição (.yaml)
entrada/  saida/       seus vídeos (fora do git)
fontes/                fontes Inter e Noto Color Emoji (licença OFL)
```
