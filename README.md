# Editor de Reels

Transforma o vídeo que você grava falando para a câmera num reel de tela dividida:

- **Cortes automáticos**: tira pausas longas e muletas (hã, hum) usando o tempo de cada palavra.
- **Legendas dinâmicas**: blocos curtos, com uma palavra-chave em destaque.
- **Tela dividida**: animações em cima, você embaixo, com o rosto enquadrado automaticamente.
- **Animações sincronizadas com a fala**: cada cena entra no momento exato em que a palavra que a chamou é dita.

O render é **só do Remotion** (React), a partir de `planos/*.scene_plan.json`,
pelo comando `python editar.py reel`. O Python corta, planeja e chama o Remotion —
não desenha quadro nenhum.

Até outubro de 2026 havia um segundo renderizador em Pillow, que desenhava cada
quadro em Python a partir de roteiros YAML. Ele foi removido; se precisar
consultá-lo, está no commit `bed62b4`.

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

## 6. Trabalhando junto com o Claude

1. Crie uma pasta por vídeo dentro de `entrada/` e jogue lá o `.mp4` e as imagens
   que quiser usar (prints, logos, fotos). O nome da pasta vira o nome do job.
2. Me diga que o vídeo está lá. Eu pergunto o briefing: para que serve, qual o
   tom, quanto tempo, onde vai tocar, o que é para aparecer na tela.
3. Eu corto as pausas, planejo as cenas e te mostro os stills antes de renderizar.
4. Você corrige em português — *"a cena 3 está cedo demais"*, *"troca essa lista
   por um número"* — e eu refaço só aquela cena.

O conteúdo de cada cena é escrito nessa conversa, não por heurística: a fala
correspondente está no campo `_fala` do `scene_plan.json`.

## 7. Estrutura

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
  ffmpeg.py            verificação do FFmpeg e duração do arquivo
  texto_util.py        normalização de texto para casar fala com escrita
motion/                projeto Remotion
  src/theme.ts         ÚNICA fonte de cores, fontes e medidas
  src/motion.ts        ÚNICA fonte das curvas de animação
  src/scenes/          um componente por tipo de cena
  src/Reel.tsx         as três faixas montadas
  public/              vídeos publicados para o Remotion (fora do git)
planos/                scene_plan.json, legendas e props de cada vídeo
entrada/               uma pasta por job: o vídeo e as imagens (fora do git)
output/                render final e stills (fora do git)
```

As regras de estilo, ritmo, legenda, movimento e layout ficam nas skills em
`.claude/skills/`. Elas valem sobre qualquer coisa escrita aqui.
