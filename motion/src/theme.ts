/**
 * Fonte unica dos tokens visuais dos reels.
 *
 * Regra da skill `reels-estilo`: nenhum componente escreve cor, fonte ou
 * tamanho direto. Se um token nao existe, ele nasce aqui antes de ser usado.
 * Para outra marca, troque os valores deste arquivo, nunca os componentes.
 */

import { loadFont as carregarFraunces } from "@remotion/google-fonts/Fraunces";
import { loadFont as carregarHanken } from "@remotion/google-fonts/HankenGrotesk";
import { loadFont as carregarMono } from "@remotion/google-fonts/JetBrainsMono";

// As fontes sao carregadas no import do modulo: `loadFont` bloqueia o render
// ate a fonte estar pronta, entao nenhum frame sai com fonte do sistema.
const fraunces = carregarFraunces("normal", {
  weights: ["600"],
  subsets: ["latin", "latin-ext"],
});

const hanken = carregarHanken("normal", {
  weights: ["500", "600", "700"],
  subsets: ["latin", "latin-ext"],
});

const mono = carregarMono("normal", {
  weights: ["600"],
  subsets: ["latin", "latin-ext"],
});

/** Promessas de carregamento, para quem precisar aguardar explicitamente. */
export const fontesProntas = Promise.all([
  fraunces.waitUntilDone(),
  hanken.waitUntilDone(),
  mono.waitUntilDone(),
]);

/**
 * Os mundos. Um reel usa um do comeco ao fim; a escolha vem do plano.
 *
 * Nao sao paletas diferentes — e a mesma paleta AR com papeis trocados. No
 * mundo `palco` o navy e o chao e o creme e a tinta; no `documento` e o
 * contrario, e o reel ganha cara de peca impressa sem sair da identidade.
 * Um mundo novo nasce aqui e nenhuma cena muda, porque os componentes leem
 * `cores`, que aponta para variaveis CSS, nao para estes valores.
 */
export const mundos = {
  /** O palco: chao navy, luz de cobre. O reel de camera, com fundo vivo. */
  palco: {
    chao: "#0F2540",
    tinta: "#F5EFE4",
    tintaFraca: "rgba(245,239,228,0.6)",
    acento: "#B87333",
    acentoClaro: "#E8D5BC",
    superficie: "#F5EFE4",
    tintaSuperficie: "#0F2540",
    reforco: "#1C3A5E",
    veu: "rgba(15,37,64,0.72)",
    vidro: "rgba(15,37,64,0.85)",
    contorno: "#0F2540",
  },
  /**
   * O documento: papel, tinta e selo. Para peca explicativa e juridica.
   *
   * Mesma familia de cor do palco, com os papeis invertidos — o creme vira
   * chao e o navy vira tinta. O acento continua o mesmo cobre, porque e ele
   * que diz "isto e um reel seu" nos dois mundos.
   */
  documento: {
    // O chao e mais fundo que a superficie de proposito: creme sobre creme
    // apaga o card, e e a diferenca de valor que faz o card existir.
    chao: "#E7DAC6",
    tinta: "#122538",
    tintaFraca: "rgba(18,37,56,0.62)",
    acento: "#B87333",
    acentoClaro: "#8A5526",
    superficie: "#FDFAF4",
    tintaSuperficie: "#122538",
    reforco: "#D8C8AE",
    veu: "rgba(231,218,198,0.84)",
    vidro: "rgba(253,250,244,0.94)",
    contorno: "#122538",
  },
} as const;

export type Mundo = keyof typeof mundos;
export const MUNDO_PADRAO: Mundo = "palco";

/**
 * Os tokens como os componentes os usam: referencias, nao valores.
 *
 * Os nomes antigos (navy, creme, cobre) viraram papeis (chao, tinta, acento)
 * porque num mundo claro "navy" seria o texto, e um token que mente sobre o
 * que e atrapalha mais do que ajuda.
 */
export const cores = {
  /** O fundo do mundo. */
  chao: "var(--chao)",
  /** Texto principal e tracos sobre o chao. */
  tinta: "var(--tinta)",
  /** Texto de apoio e rotulos. */
  tintaFraca: "var(--tinta-fraca)",
  /** Destaque. Sinal, nao decoracao: no maximo um elemento por cena. */
  acento: "var(--acento)",
  /** O claro do fio metalico; so dentro de `metal`. */
  acentoClaro: "var(--acento-claro)",
  /** Fundo do card preenchido. Claro nos dois mundos. */
  superficie: "var(--superficie)",
  /** Texto sobre o card preenchido — nao e a mesma coisa que `tinta`. */
  tintaSuperficie: "var(--tinta-superficie)",
  /** Faixa atras do video, conectores inativos, grades. */
  reforco: "var(--reforco)",
  /** Veu sobre o fundo vivo, para o texto ter contraste. */
  veu: "var(--veu)",
  /** Corpo de card translucido: deixa a luz do cenario atravessar. */
  vidro: "var(--vidro)",
  /**
   * Contorno da legenda. Fica escuro nos dois mundos: ele corre sobre o
   * video, nao sobre o chao, e e so ali que a legenda precisa de borda.
   */
  contorno: "var(--contorno)",
} as const;

/** As variaveis CSS de um mundo, para o estilo da raiz da composicao. */
export const variaveisDoMundo = (nome: Mundo | undefined) => {
  const mundo = mundos[nome ?? MUNDO_PADRAO] ?? mundos[MUNDO_PADRAO];
  const estilo: Record<string, string> = {};
  for (const [papel, valor] of Object.entries(mundo)) {
    // chao -> --chao, tintaFraca -> --tinta-fraca
    estilo[`--${papel.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}`] =
      valor;
  }
  return estilo;
};

/**
 * Acabamento metalico. O fio da borda tem 1,5 px: acima disso vira moldura de
 * convite de casamento (skill `reels-estilo`).
 */
export const metal = {
  borda: `linear-gradient(135deg, ${cores.acento}, ${cores.acentoClaro}, ${cores.acento})`,
  face: "linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.12))",
  brilho:
    "linear-gradient(105deg, transparent 40%, rgba(245,239,228,0.22) 50%, transparent 60%)",
  fio: 1.5,
} as const;

export const fontes = {
  /** Titulo de cena, termo. Peso 600. */
  titulo: fraunces.fontFamily,
  /** Corpo, itens de lista, legenda. Pesos 500/600/700. */
  corpo: hanken.fontFamily,
  /** Numeros, artigos de lei, codigo. Peso 600. */
  mono: mono.fontFamily,
} as const;

/** Formato fixo do reel. */
export const formato = {
  largura: 1080,
  altura: 1920,
  fps: 30,
} as const;

/**
 * Camadas da sobreposicao com profundidade (skill `reels-composicao`).
 *
 * Nao ha mais tela dividida: o video ocupa a tela inteira e o fundo da zona
 * de cenas e o proprio video ampliado e desfocado. A emenda reta virou um
 * degrade, e e por isso que o reel deixa de parecer "duas coisas coladas".
 */
export const layout = {
  /** O proprio video, ampliado e desfocado, atras de tudo. */
  /**
   * Fundo desfocado. O desfoque em si nao mora aqui: quem o aplica e o
   * `gblur=sigma=6` de `gerar_fundo`, em editor/plano.py, uma vez por video
   * em vez de uma vez por frame. `brilho` vira a opacidade do veu escuro.
   */
  fundoVivo: { escala: 2.2, brilho: 0.45 },
  /** Veu + grade cobrem do topo ate o inicio do video nitido. */
  veu: { topo: 0, altura: 690 },
  /** Onde as cenas vivem. */
  cenas: { topo: 150, altura: 484 },
  /**
   * Video nitido, com o topo dissolvendo no fundo desfocado.
   *
   * A altura de 1230 px nao e estetica, e uma medida: o arquivo deste reel
   * ja vem editado, com selo do MEC ate y=1355 e legendas queimadas a
   * partir de y=1389. A janela visivel precisa alcancar o selo sem chegar
   * nas legendas antigas, senao o reel fica com duas legendas ao mesmo
   * tempo. Com video bruto, esta faixa pode voltar a ser menor.
   */
  video: { topo: 690, altura: 1230, degrade: 60 },
  /**
   * Centro do rosto, em pixels absolutos.
   *
   * O topo da cabeca fica ~292 px acima deste ponto (medido no material).
   * Ele TEM que cair depois do fim do degrade (820+140=960), senao a
   * dissolucao come a cabeca: com rosto em 1240 o topo caia em 948, 62 px
   * acima do inicio da faixa, e sumia de vez.
   */
  rosto: 1090,
  /** Folga minima entre o fim do degrade e o topo da cabeca. */
  folgaCabeca: 40,
  /**
   * Centro da legenda.
   *
   * 1480 e nao 1620: o selo do MEC que ele segura ocupa de 1585 a 1900 na
   * composicao, e a legenda caia em cima justamente do elemento que o
   * enquadramento foi alargado para mostrar.
   */
  legenda: 1480,
  /** Margem lateral. */
  margem: 72,
  /** Nada importante acima disso (barra do Instagram). */
  topoSeguro: 120,
  /** Livre na lateral direita inferior (botoes de curtir, comentar). */
  lateralSegura: 140,
  /** Nada importante abaixo disso. */
  baseSegura: 1740,
  /** Profundidade da cena: fica no container, nunca no card. */
  perspectiva: 1400,
} as const;

/** Espacamento vertical entre elementos dentro de uma cena. */
export const espaco = {
  /** Elementos relacionados. */
  proximo: 32,
  /** Blocos distintos. */
  distante: 64,
} as const;

/** Raios: 20 px em cards, 999 px em pilulas. Nada no meio. */
export const raios = {
  card: 20,
  pilula: 999,
} as const;

/**
 * Sombras. A do card flutuante e grande de proposito: e ela que faz o card
 * parecer estar no ambiente em vez de colado na tela. Sem isso, o resto da
 * profundidade nao convence.
 */
export const sombras = {
  flutuante: "0 24px 60px rgba(0,0,0,0.45)",
  /** De onde a sombra parte, para crescer junto com a entrada. */
  flutuanteInicial: "0 8px 20px rgba(0,0,0,0.20)",
  /** Elemento dentro de um card. */
  interna: "0 4px 12px rgba(0,0,0,0.20)",
} as const;

/** Tamanhos base para 1080 px de largura. */
export const tipografia = {
  tituloCena: { fontFamily: fontes.titulo, fontWeight: 600, fontSize: 84 },
  termo: { fontFamily: fontes.titulo, fontWeight: 600, fontSize: 72 },
  corpo: { fontFamily: fontes.corpo, fontWeight: 500, fontSize: 48 },
  item: { fontFamily: fontes.corpo, fontWeight: 500, fontSize: 44 },
  rotulo: {
    fontFamily: fontes.corpo,
    fontWeight: 600,
    fontSize: 30,
    textTransform: "uppercase" as const,
    letterSpacing: "0.08em",
  },
  /** Rótulo dentro de caixa estreita (etapas de fluxo). */
  rotuloCaixa: {
    fontFamily: fontes.corpo,
    fontWeight: 600,
    fontSize: 26,
    textTransform: "uppercase" as const,
    letterSpacing: "0.04em",
  },
  numero: { fontFamily: fontes.mono, fontWeight: 600, fontSize: 120 },
  referencia: { fontFamily: fontes.mono, fontWeight: 600, fontSize: 56 },
  // 54 px é o piso da faixa que a skill permite: com 56 px duas linhas
  // encostam na borda do vídeo.
  legenda: { fontFamily: fontes.corpo, fontWeight: 700, fontSize: 54 },
  assinatura: { fontFamily: fontes.corpo, fontWeight: 600, fontSize: 28 },
  /** Aviso fixo. Pequeno, mas nunca abaixo do piso de leitura do 9:16. */
  aviso: { fontFamily: fontes.corpo, fontWeight: 600, fontSize: 30 },
  /** Nome do instrumento no cabecalho do `documento`. */
  documentoTitulo: {
    fontFamily: fontes.mono,
    fontWeight: 600,
    fontSize: 38,
    letterSpacing: "0.14em",
    textTransform: "uppercase" as const,
  },
} as const;

/**
 * Aviso fixo no topo (`aviso` no plano).
 *
 * Para conteudo juridico ele nao e enfeite: e o que separa informar de
 * parecer dar consultoria. Fica o reel inteiro, acima de tudo, e empurra a
 * assinatura para baixo em vez de disputar o mesmo canto.
 */
/**
 * Sublinhado da palavra-chave de um titulo.
 *
 * Entra depois da frase assentar: sublinhar enquanto o texto ainda se move
 * faz o traco parecer parte da entrada, e nao a enfase que ele e.
 */
export const textoChave = {
  espessura: 6,
  /** Quanto o traco fica abaixo da linha de base. */
  descida: 4,
  /** Frames de espera depois da entrada da frase. */
  atraso: 8,
} as const;

/**
 * Cena `documento`: instrumento juridico com selo e clausulas.
 *
 * O selo nao e enfeite: e ele que diz "isto e um papel que existe", que e a
 * diferenca entre esta cena e uma lista comum.
 */
export const documento = {
  selo: 56,
  marcador: 34,
  padding: "10px 14px",
  /** Frames ate o selo entrar, depois do cabecalho. */
  atrasoSelo: 10,
  /** Frames ate a primeira clausula, quando nao ha palavra-gatilho. */
  atrasoPrimeira: 16,
} as const;

/**
 * Cena `objeto`: a ilustracao gerada e o titulo que ela carrega.
 *
 * A altura e menor do que a zona de cenas comporta porque o titulo divide o
 * espaco com ela: objeto grande demais empurra o titulo para fora.
 */
export const objeto = {
  altura: 300,
  larguraTitulo: 880,
  sombra: "drop-shadow(0 20px 28px rgba(0,0,0,0.28))",
  /** Frames ate o titulo entrar, depois do objeto pousar. */
  atrasoTitulo: 10,
} as const;

/** Cena `cena_apoio`: o clipe de b-roll e o rotulo sobre ele. */
export const cenaApoio = {
  paddingRotulo: "8px 18px",
  /** Frames ate o rotulo entrar, depois do clipe aparecer. */
  atrasoRotulo: 8,
} as const;

export const aviso = {
  padding: "10px 24px",
  espacoIcone: 10,
  tamanhoIcone: 26,
  larguraMaxima: 860,
  /** Quanto a assinatura desce quando ha aviso. */
  alturaOcupada: 76,
} as const;

/** Grade sutil opcional atras das cenas. */
export const grade = {
  cor: cores.reforco,
  opacidade: 0.3,
  passo: 72,
} as const;

/** Icones: linha, strokeWidth 2, um unico estilo no video inteiro. */
export const icones = {
  strokeWidth: 2,
  tamanho: 160,
} as const;

/**
 * Legenda. Agora fica sobre a imagem, nao sobre fundo chapado, entao o
 * contorno navy e obrigatorio. Tres niveis de enfase, com cota (skill
 * `reels-legendas`): normal, chave (1 por bloco) e maxima (3 no reel inteiro).
 */
/**
 * A legenda e a unica coisa que NAO segue o mundo.
 *
 * Ela corre sobre o video, nao sobre o chao: num mundo claro, seguir `tinta`
 * a deixaria navy sobre o terno escuro, ilegivel. Entao as cores dela sao
 * fixas — creme sobre o video, contorno navy — e so o acento, que e o mesmo
 * nos dois mundos, vem do token.
 */
export const legenda = {
  corTexto: "#F5EFE4",
  corChave: cores.acento,
  /** Nivel maximo: creme sobre pilula cobre. */
  maximaFundo: cores.acento,
  maximaTexto: "#F5EFE4",
  maximaPadding: "8px 20px",
  contorno: 6,
  /** Pop da palavra no momento em que e falada. E pop, nao balanco. */
  escalaPop: 1.04,
  framesPop: 4,
  maxLinhas: 2,
  maxCaracteresLinha: 28,
  /** Largura que forca a quebra em ~28 caracteres no corpo de 54 px. */
  larguraMaxima: 760,
} as const;
