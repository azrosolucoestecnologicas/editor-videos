/**
 * Formato do `scene_plan.json` e do `legendas.json` gerados pelo Python.
 * O catálogo de tipos é fechado: ele espelha a tabela da skill
 * `reels-composicao` e o `CATALOGO` de `editor/plano.py`.
 */

import type { Mundo } from "./theme";

/** Campos com prefixo `_` são derivados: o planejador os recalcula a cada rodada. */
type Gatilho = {
  readonly palavra_gatilho?: string | null;
  /** Segundo em que a palavra-gatilho é falada, no vídeo já cortado. */
  readonly _em?: number | null;
};

export type ItemLista = Gatilho & { readonly texto: string };
export type EtapaFluxo = Gatilho & { readonly rotulo: string };
export type ClausulaDoc = Gatilho & { readonly texto: string };
export type Coluna = {
  readonly titulo: string;
  readonly linhas: readonly string[];
};

export type ConteudoPorTipo = {
  card_conceito: { readonly termo: string; readonly definicao: string };
  lista: { readonly titulo?: string; readonly itens: readonly ItemLista[] };
  comparacao: { readonly esquerda: Coluna; readonly direita: Coluna };
  fluxo: { readonly etapas: readonly EtapaFluxo[] };
  numero: Gatilho & { readonly valor: string; readonly rotulo: string };
  citacao_legal: { readonly referencia: string; readonly trecho?: string };
  icone_destaque: { readonly icone: string; readonly texto: string };
  documento: {
    readonly titulo: string;
    readonly clausulas: readonly ClausulaDoc[];
  };
  sintese: { readonly frase: string; readonly chave?: string };
};

export type TipoCena = keyof ConteudoPorTipo;

type CenaBase = Gatilho & {
  readonly id: string;
  /** Segundos no vídeo já cortado. */
  readonly inicio: number;
  readonly fim: number;
  readonly ocorrencia?: number;
  readonly editado?: boolean;
  /**
   * Liga a varredura especular nos cards desta cena. A skill
   * `reels-movimento` limita a 2 cenas por reel e o validador conta.
   */
  readonly brilho?: boolean;
  /** Dá um zoom leve no vídeo durante esta cena. Espaçados em 8 s no mínimo. */
  readonly zoom?: boolean;
};

/** União discriminada: cada `tipo` casa com o formato do seu `conteudo`. */
export type Cena = {
  [T in TipoCena]: CenaBase & {
    readonly tipo: T;
    readonly conteudo: ConteudoPorTipo[T];
  };
}[TipoCena];

export type Enquadramento = {
  /** Altura do rosto no vídeo original: 0 = topo, 1 = base. */
  readonly foco_rosto: number;
  /** Topo da cabeça, mesma escala. A dissolução tem que terminar acima dele. */
  readonly topo_cabeca?: number;
  readonly zoom: number;
  readonly origem: "padrao" | "auto" | "manual";
};

/** Trecho em que o vídeo recebe o zoom de ênfase. */
export type JanelaZoom = { readonly inicio: number; readonly fim: number };

/** Dimensões do arquivo de vídeo, para o recorte em cover. */
export type Fonte = { readonly largura: number; readonly altura: number };

export type Plano = {
  readonly versao: number;
  readonly video: string;
  readonly duracao: number;
  readonly fps: number;
  readonly fonte: Fonte;
  readonly assinatura: string;
  readonly enquadramento: Enquadramento;
  /**
   * Em que mundo o reel acontece (`theme.ts`). Um reel usa um só, do começo
   * ao fim. Ausente = `palco`, que é o padrão e o que todo plano antigo usa.
   */
  readonly mundo?: Mundo;
  /**
   * Aviso fixo no topo, o reel inteiro. Vazio ou ausente = sem aviso.
   * Ex.: "Conteúdo informativo · não é consultoria jurídica".
   */
  readonly aviso?: string;
  readonly cenas: readonly Cena[];
};

export type PalavraLegenda = {
  readonly texto: string;
  readonly inicio: number;
  readonly fim: number;
};

export type BlocoLegenda = {
  readonly inicio: number;
  readonly fim: number;
  /** Índice da palavra em nível "chave" (cobre), ou null. Máximo 1 por bloco. */
  readonly destaque: number | null;
  /**
   * Índice da palavra em nível "máxima" (pílula cobre), ou null.
   * A skill `reels-legendas` dá cota de 3 no reel inteiro.
   */
  readonly maxima?: number | null;
  readonly palavras: readonly PalavraLegenda[];
};

export type PropsReel = {
  readonly plano: Plano;
  readonly legendas: readonly BlocoLegenda[];
  /** Nome do arquivo dentro de `motion/public/`, para o `staticFile()`. */
  readonly video: string;
  /** Versão pequena e desfocada do vídeo, usada pelo fundo vivo. */
  readonly videoFundo: string;
};
