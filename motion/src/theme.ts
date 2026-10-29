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

/** Paleta AR. Proporcao por cena: ~70% navy, ~25% creme, no maximo 5% cobre. */
export const cores = {
  /** Fundo do painel de animacao; texto principal sobre fundo claro. */
  navy: "#0F2540",
  /** Destaque. Sinal, nao decoracao: no maximo um elemento cobre por cena. */
  cobre: "#B87333",
  /** Fundo de cards; texto sobre navy. */
  creme: "#F5EFE4",
  /** Cards secundarios, grades, conectores inativos. */
  navySoft: "#1C3A5E",
  /** Texto de apoio e rotulos. */
  creme60: "rgba(245,239,228,0.6)",
  /** Veu sobre o fundo vivo, para o texto ter contraste. */
  veu: "rgba(15,37,64,0.72)",
  /**
   * Corpo de card translucido: deixa a luz do cenario atravessar sem perder o
   * navy. Base navy, nao navySoft: sobre as partes claras do palco o navySoft
   * a 55% resultava num cinza-barro que nao pertence a paleta.
   */
  vidro: "rgba(15,37,64,0.85)",
} as const;

/**
 * Acabamento metalico. O fio da borda tem 1,5 px: acima disso vira moldura de
 * convite de casamento (skill `reels-estilo`).
 */
export const metal = {
  borda: `linear-gradient(135deg, ${cores.cobre}, #E8D5BC, ${cores.cobre})`,
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
  fundoVivo: { escala: 2.2, desfoque: 3, brilho: 0.45 },
  /** Veu + grade cobrem do topo ate o inicio do video nitido. */
  veu: { topo: 0, altura: 1010 },
  /** Onde as cenas vivem. */
  cenas: { topo: 150, altura: 710 },
  /** Video nitido, com o topo dissolvendo no fundo desfocado. */
  video: { topo: 1010, altura: 910, degrade: 150 },
  /** Centro do rosto, em pixels absolutos: um terco do alto da faixa nitida. */
  rosto: 1240,
  /** O rosto nunca sobe disso: acima daqui ele disputa espaco com os cards. */
  rostoMaximo: 1100,
  /** Centro da legenda. */
  legenda: 1620,
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
} as const;

/** Grade sutil opcional atras das cenas. */
export const grade = {
  cor: cores.navySoft,
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
export const legenda = {
  corTexto: cores.creme,
  corChave: cores.cobre,
  /** Nivel maximo: creme sobre pilula cobre. */
  maximaFundo: cores.cobre,
  maximaTexto: cores.creme,
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
