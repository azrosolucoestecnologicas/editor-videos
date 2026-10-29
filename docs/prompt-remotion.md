Contexto: este repositório (editor-videos) é meu pipeline de reels. Eu gravo falando para a câmera, coloco o vídeo em entrada/ e o pipeline em Python faz transcrição, cortes, legendas e textos. Tudo isso funciona e deve ser preservado. Não altere o comportamento dos comandos existentes de editar.py.

O que já existe (Fase 0 concluída; confira lendo o código, não precisa refazer o diagnóstico do zero):
- editar.py: linha de comando com os subcomandos transcrever, cortar, novo, eventos, quadro e renderizar.
- editor/transcricao.py: faster-whisper com word_timestamps; o modelo fica em modelos/. Gera entrada/<nome>.transcricao.json no formato
  {"idioma", "duracao", "segmentos": [{"inicio", "fim", "texto"}], "palavras": [{"palavra", "inicio", "fim"}]}
  com tempos em segundos e a pontuação grudada na palavra.
- editor/cortes.py: `python editar.py cortar entrada/X.mp4` remove pausas maiores que 0,35 s e muletas (hã, hum...) com base no tempo de cada palavra. Gera entrada/X_cortado.mp4, entrada/X_cortado.transcricao.json (já remapeada) e entrada/X_cortado.cortes.json.
- editor/legendas.py: agrupa as palavras em blocos de até 3 palavras e destaca a palavra falada (reaproveitar essa lógica de agrupamento).
- editor/roteiro.py: a classe Localizador encontra em que momento uma frase foi falada (ignora acentos e tolera pequenas diferenças). Reaproveitar para a palavra_gatilho.
- editor/compositor.py + editor/animacoes/: tela dividida feita em Pillow. Funciona, mas o visual é fraco; é isso que o Remotion vai substituir.
- exemplos/gerar_demo.py gera um vídeo de teste sintético; para os testes de verdade, use um reel meu que está em entrada/.

Objetivo: o reel final com TELA DIVIDIDA, com animações na parte de cima ilustrando o que estou falando (diagramas, cards de conceito, listas, comparações, números, fluxos) e eu na parte de baixo, feito com Remotion (React gerando vídeo) e renderizado localmente no meu computador. Uso individual, então a Free License do Remotion se aplica.

Decisões já tomadas:
- Fluxo final: vídeo bruto -> transcrição (Whisper atual) -> cortes (editar.py cortar) -> scene_plan.json -> render Remotion.
- As legendas migram para a composição Remotion (uma renderização só), posicionadas na divisória, usando os blocos calculados pela lógica de editor/legendas.py exportados em JSON.
- O scene_plan.json terá um id por cena; ao rodar o planejador de novo, cenas que eu editei à mão são preservadas e só o resto é recalculado.

Antes de começar, pergunte-me (numa única mensagem):
1. Quem escreve o scene_plan.json: (a) você, nesta conversa, com um script validador das regras; ou (b) um script que chama a API do Claude (precisa de chave de API e tem custo por vídeo, mas roda sozinho no comando único).
2. Enquadramento do rosto: detecção automática (ex.: MediaPipe) ou o ajuste manual atual (foco_rosto)?
3. A identidade visual do theme.ts (cores, fontes, estilo).

FASE 1 - Setup
1. Crie um projeto Remotion dentro do repositório (pasta /motion) e instale as Agent Skills oficiais do Remotion seguindo a documentação atual em remotion.dev (consulte a doc, não use API de memória).
2. Formato fixo: 1080x1920, 30fps.
3. Crie /motion/theme.ts com os tokens visuais (cores, fontes, raios, sombras, duração padrão de entrada e saída) conforme a identidade que eu escolher.

FASE 2 - Planejador de cenas
1. Crie uma etapa que lê a transcrição com timestamps (a do vídeo cortado) e gera um scene_plan.json com uma lista de cenas: {id, inicio, fim, tipo, conteudo, palavra_gatilho}.
2. Tipos de cena (catálogo fechado, cada um vira um componente React):
   - card_conceito: termo + definição curta
   - lista: 2 a 4 itens entrando um a um
   - comparacao: duas colunas (antes/depois, humano/IA)
   - fluxo: caixas e setas, de 3 a 5 etapas
   - numero: estatística animada (contador)
   - citacao_legal: artigo de lei ou súmula em destaque
   - icone_destaque: ícone grande + palavra-chave
3. Regras do planejador:
   - Uma mudança visual a cada 3 a 6 segundos, sem trechos mortos.
   - A entrada de cada elemento sincroniza com o timestamp da palavra_gatilho.
   - No máximo 8 palavras na tela por elemento. Nunca repetir a legenda.
   - Conteúdo fiel ao que eu falei; não inventar dados nem citações.
   - Português com acentuação completa, sem emojis.
4. O scene_plan.json deve ser editável à mão: se eu mudar um texto ou tempo e rodar de novo, só aquilo muda.

FASE 3 - Composição
1. Uma composição Remotion que recebe o scene_plan.json e o vídeo cortado como props:
   - metade de cima: cenas animadas (transições suaves, spring, sem efeitos exagerados)
   - metade de baixo: meu vídeo (OffthreadVideo), com reenquadramento centralizado no rosto
   - legendas: na divisória, migradas para a composição
2. Antes do render completo, gere stills (npx remotion still) de 4 a 6 frames-chave e me mostre para validação.
3. Render final local para /output/<nome>_final.mp4.

FASE 4 - Integração
1. Um único comando que roda tudo: vídeo bruto -> transcrição -> cortes -> scene_plan.json -> render final (por exemplo, `python editar.py reel entrada/X.mp4`).
2. Documente no README como reeditar uma cena.

Regras gerais:
- Teste tudo com um único reel meu antes de generalizar.
- Faça commits pequenos por fase e me mostre o resultado ao fim de cada fase antes de seguir para a próxima.
- Não faça push nem crie pull request sem eu pedir.
