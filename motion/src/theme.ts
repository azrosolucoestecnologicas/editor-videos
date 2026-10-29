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
 * Faixas da tela dividida (skill `reels-composicao`).
 * A proporcao pode virar 50/50, mas fica igual no video inteiro.
 */
export const layout = {
  painel: { topo: 0, altura: 900 },
  divisoria: { topo: 900, altura: 140 },
  video: { topo: 1040, altura: 880 },
  /** Margem lateral do painel. */
  margem: 72,
  /** Nada importante acima disso (barra do Instagram). */
  topoSeguro: 120,
  /** Livre na lateral direita inferior (botoes de curtir, comentar). */
  lateralSegura: 140,
  /** Distancia minima da legenda a borda inferior. */
  baseSegura: 180,
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

/** Sombra maxima permitida pela skill de estilo. */
export const sombras = {
  card: "0 8px 24px rgba(0,0,0,0.25)",
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

/** Legenda: contorno ou caixa navy, conforme a skill `reels-legendas`. */
export const legenda = {
  corTexto: cores.creme,
  corDestaque: cores.cobre,
  escalaDestaque: 1.06,
  contorno: 6,
  caixaFundo: "rgba(15,37,64,0.85)",
  caixaRaio: 14,
  maxLinhas: 2,
  maxCaracteresLinha: 28,
} as const;
