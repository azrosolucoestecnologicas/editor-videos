/**
 * Fonte unica dos presets de animacao dos reels.
 *
 * Regra da skill `reels-movimento`: nenhum componente define curva ou duracao
 * propria. Cada preset devolve um objeto de estilo pronto para espalhar no
 * `style` do elemento, usando as propriedades CSS `scale`/`translate` em vez
 * de `transform` (recomendacao da skill oficial `remotion-markup`).
 *
 * Todos os tempos sao em frames a 30 fps.
 */

import { Easing, interpolate, spring } from "remotion";

const PRESO = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

/** Duracoes dos presets, em frames. Limite da skill: 8 a 24 frames. */
export const duracoes = {
  entrada: 14,
  entradaSuave: 20,
  /** Entrada com perspectiva de um card que flutua sobre o video. */
  flutuar: 18,
  /** Uma passada de brilho metalico. Nunca repete. */
  brilho: 22,
  saida: 8,
  destaqueSubida: 6,
  destaqueVolta: 10,
  desenho: 20,
  contador: 24,
  /** Cenas vizinhas se sobrepoem de 4 a 6 frames; nunca corte seco. */
  sobreposicaoCenas: 5,
  /**
   * Quanto a cena sobrevive depois do proprio fim. Curto de proposito: com
   * cauda longa, a cena que sai e a que entra ficam as duas em meia
   * opacidade no mesmo lugar da tela e o resultado e ilegivel.
   */
  caudaCena: 2,
  /** Wipe horizontal para mudanca de assunto. */
  wipe: 12,
  /** Transicao para o video em tela cheia. */
  telaCheia: 12,
} as const;

/**
 * O olho chega antes do ouvido: um elemento entra 3 frames antes do inicio da
 * palavra-gatilho (a skill pede 2 a 4).
 */
export const ANTECIPACAO_FRAMES = 3;

/** Atraso entre itens que entram juntos (a skill pede 6 a 8 frames). */
export const ATRASO_ITEM_FRAMES = 7;

/** Entrada padrao de qualquer elemento: sobe 24 px e aparece. */
export const entrada = (frame: number, fps: number, atrasoFrames = 0) => {
  const progresso = spring({
    frame: Math.max(0, frame - atrasoFrames),
    fps,
    config: { damping: 200, stiffness: 120 },
    durationInFrames: duracoes.entrada,
  });

  return {
    opacity: progresso,
    translate: `0px ${interpolate(progresso, [0, 1], [24, 0])}px`,
  };
};

/**
 * Entrada de um card que flutua sobre o video: sobe, aparece e vira de frente.
 * A rotacao e de eixo Y e some — e perspectiva, nao giro. Use sempre junto com
 * `profundidade`, que cresce a sombra no mesmo tempo.
 */
export const flutuar = (frame: number, fps: number, atrasoFrames = 0) => {
  const progresso = spring({
    frame: Math.max(0, frame - atrasoFrames),
    fps,
    config: { damping: 200, stiffness: 120 },
    durationInFrames: duracoes.flutuar,
  });

  return {
    opacity: progresso,
    translate: `0px ${interpolate(progresso, [0, 1], [28, 0])}px`,
    rotate: `y ${interpolate(progresso, [0, 1], [-6, 0])}deg`,
    scale: interpolate(progresso, [0, 1], [0.96, 1], {
      output: "perceptual-scale",
    }),
  };
};

/**
 * Sombra do card crescendo junto com o `flutuar`: o card "descola" da tela.
 * Devolve só a `boxShadow`, para espalhar ao lado do `flutuar`.
 */
export const profundidade = (frame: number, fps: number, atrasoFrames = 0) => {
  const progresso = spring({
    frame: Math.max(0, frame - atrasoFrames),
    fps,
    config: { damping: 200, stiffness: 120 },
    durationInFrames: duracoes.flutuar,
  });

  return {
    boxShadow: `0 ${interpolate(progresso, [0, 1], [8, 24])}px ${interpolate(
      progresso,
      [0, 1],
      [20, 60],
    )}px rgba(0,0,0,${interpolate(progresso, [0, 1], [0.2, 0.45])})`,
  };
};

/**
 * Varredura especular atravessando um card com borda metálica.
 *
 * Uma passada por card, na entrada, NUNCA em laço — e no máximo duas cenas por
 * reel usam brilho (skill `reels-movimento`). Devolve a posição da faixa em
 * porcentagem; `null` quando a passada já terminou, para o componente deixar
 * de desenhar o brilho.
 */
export const brilhoMetal = (frame: number, atrasoFrames = 0) => {
  const f = frame - atrasoFrames;
  if (f < 0 || f > duracoes.brilho) {
    return null;
  }
  return interpolate(f, [0, duracoes.brilho], [-140, 240], {
    ...PRESO,
    easing: Easing.inOut(Easing.cubic),
  });
};

/** Entrada mais longa e discreta: textos longos e citacoes legais. */
export const entradaSuave = (frame: number, fps: number, atrasoFrames = 0) => {
  const progresso = spring({
    frame: Math.max(0, frame - atrasoFrames),
    fps,
    config: { damping: 200, stiffness: 120 },
    durationInFrames: duracoes.entradaSuave,
  });

  return {
    opacity: progresso,
    translate: `0px ${interpolate(progresso, [0, 1], [12, 0])}px`,
  };
};

/** Saida de qualquer elemento: sobe 12 px e desaparece em 8 frames. */
export const saida = (frame: number, inicioFrame: number) => {
  const f = frame - inicioFrame;

  return {
    opacity: interpolate(f, [0, duracoes.saida], [1, 0], {
      ...PRESO,
      easing: Easing.in(Easing.cubic),
    }),
    translate: `0px ${interpolate(f, [0, duracoes.saida], [0, -12], {
      ...PRESO,
      easing: Easing.in(Easing.cubic),
    })}px`,
  };
};

/** Enfase de uma palavra ou elemento: 1 para 1,06 e volta. */
export const destaque = (frame: number, inicioFrame: number) => {
  const f = frame - inicioFrame;
  const subida = duracoes.destaqueSubida;

  return {
    scale: interpolate(
      f,
      [0, subida, subida + duracoes.destaqueVolta],
      [1, 1.06, 1],
      { ...PRESO, output: "perceptual-scale" },
    ),
  };
};

/**
 * Desenho de uma linha, seta, conector ou sublinhado.
 * `comprimento` e o comprimento total do path (use `getTotalLength()` ou o
 * comprimento calculado do segmento).
 */
export const desenho = (
  frame: number,
  comprimento: number,
  inicioFrame = 0,
  duracaoFrames = duracoes.desenho,
) => ({
  strokeDasharray: comprimento,
  strokeDashoffset: interpolate(
    frame - inicioFrame,
    [0, duracaoFrames],
    [comprimento, 0],
    { ...PRESO, easing: Easing.out(Easing.cubic) },
  ),
});

/**
 * Numero subindo. A contagem termina exatamente no frame em que o numero e
 * falado, por isso o parametro e o frame FINAL, nao o inicial.
 */
export const contador = (
  frame: number,
  fimFrame: number,
  valorFinal: number,
  valorInicial = 0,
  duracaoFrames = duracoes.contador,
) =>
  interpolate(
    frame,
    [fimFrame - duracaoFrames, fimFrame],
    [valorInicial, valorFinal],
    { ...PRESO, easing: Easing.out(Easing.cubic) },
  );

/**
 * Entrada e saida combinadas de uma cena inteira.
 * `duracaoCena` em frames; a saida comeca `sobreposicaoCenas` frames antes do
 * fim, para que a cena seguinte entre por cima.
 */
export const cena = (frame: number, fps: number, duracaoCena: number) => {
  const inicioSaida = duracaoCena - duracoes.sobreposicaoCenas;

  if (frame < inicioSaida) {
    return flutuar(frame, fps);
  }

  return saida(frame, inicioSaida);
};

/** Wipe horizontal para mudanca de assunto: faixa navySoft atravessando. */
export const wipe = (frame: number, inicioFrame: number) =>
  interpolate(frame - inicioFrame, [0, duracoes.wipe], [0, 1], {
    ...PRESO,
    easing: Easing.inOut(Easing.cubic),
  });

/**
 * Zoom leve de enfase no video gravado: 1,0 para 1,08 em 20 frames, mantido
 * ate `duracaoFrames`, voltando em 12 frames. No maximo um a cada 8 segundos.
 */
export const zoomEnfase = (
  frame: number,
  inicioFrame: number,
  duracaoFrames: number,
) =>
  interpolate(
    frame - inicioFrame,
    [0, 20, Math.max(21, duracaoFrames), Math.max(21, duracaoFrames) + 12],
    [1, 1.08, 1.08, 1],
    { ...PRESO, output: "perceptual-scale" },
  );
