/**
 * Peças comuns a todas as cenas.
 *
 * `AreaCena` entrega a zona de cenas com perspectiva (skill
 * `reels-composicao`: a perspectiva fica no contêiner, nunca no card) e a
 * saída da cena. `Card` entrega o acabamento metálico. Cada elemento lá
 * dentro cuida da própria entrada, com o atraso da palavra-gatilho dele.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import {
  brilhoMetal,
  desenho,
  duracoes,
  flutuar,
  profundidade,
  saida,
} from "../motion";
import { cores, espaco, metal, raios, layout } from "../theme";

/** Largura útil, já descontadas as margens laterais. */
export const LARGURA_UTIL = 1080 - layout.margem * 2;

/** Altura da zona de cenas. */
export const ALTURA_UTIL = layout.cenas.altura;

/**
 * Quantos frames depois do início da cena um elemento entra.
 * `_em` é o segundo em que a palavra-gatilho do elemento é falada.
 */
export const atrasoDe = (
  em: number | null | undefined,
  inicioCena: number,
  fps: number,
) => (em == null ? 0 : Math.max(0, Math.round((em - inicioCena) * fps)));

export const AreaCena: React.FC<{
  duracaoFrames: number;
  alinhamento?: "esquerda" | "centro";
  children: React.ReactNode;
}> = ({ duracaoFrames, alinhamento = "esquerda", children }) => {
  const frame = useCurrentFrame();
  // A cena começa a sair antes de acabar, para a próxima entrar por cima:
  // nunca um corte seco entre cenas animadas. A saída termina logo depois
  // do fim da cena, não muito depois — senão duas cenas convivem meio
  // transparentes e se tornam ilegíveis.
  const inicioSaida = Math.max(
    1,
    duracaoFrames + duracoes.caudaCena - duracoes.saida,
  );
  const estiloSaida = frame >= inicioSaida ? saida(frame, inicioSaida) : null;
  const centro = alinhamento === "centro";

  return (
    <div
      style={{
        position: "absolute",
        left: layout.margem,
        top: layout.cenas.topo,
        width: LARGURA_UTIL,
        height: ALTURA_UTIL,
        perspective: layout.perspectiva,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: centro ? "center" : "flex-start",
        textAlign: centro ? "center" : "left",
        gap: espaco.proximo,
        ...estiloSaida,
      }}
    >
      {children}
    </div>
  );
};

/**
 * Superfície de vidro com fio metálico, flutuando sobre o vídeo.
 *
 * O fio tem 1,5 px: acima disso vira moldura. A sombra cresce junto com a
 * entrada (`profundidade`), que é o que faz o card descolar da tela.
 *
 * `brilho` liga a varredura especular — uma passada só, na entrada. A skill
 * `reels-movimento` limita a 2 cenas por reel, e quem conta é o validador.
 */
export const Card: React.FC<{
  atrasoFrames?: number;
  brilho?: boolean;
  preenchido?: boolean;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ atrasoFrames = 0, brilho = false, preenchido = false, style, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const posicaoBrilho = brilho ? brilhoMetal(frame, atrasoFrames + 6) : null;
  const fundo = preenchido ? cores.creme : cores.vidro;

  return (
    <div
      style={{
        position: "relative",
        overflow: "hidden",
        borderRadius: raios.card,
        // Truque do fio metálico: o corpo pinta até o padding-box e o gradiente
        // só aparece na faixa da borda.
        background: `linear-gradient(${fundo}, ${fundo}) padding-box, ${metal.borda} border-box`,
        border: `${metal.fio}px solid transparent`,
        // Sem `backdrop-filter` aqui: o que passa por tras do card ja vem
        // desfocado do fundo vivo, e com o vidro a 85% o efeito nao aparece.
        // So custava tempo de render.
        ...flutuar(frame, fps, atrasoFrames),
        ...profundidade(frame, fps, atrasoFrames),
        ...style,
      }}
    >
      {/* Leve sombreado de cima para baixo: dá volume à face do card. */}
      {preenchido ? null : (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: metal.face,
            pointerEvents: "none",
          }}
        />
      )}

      {posicaoBrilho === null ? null : (
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: `${posicaoBrilho}%`,
            width: "60%",
            background: metal.brilho,
            pointerEvents: "none",
          }}
        />
      )}

      <div style={{ position: "relative" }}>{children}</div>
    </div>
  );
};

/**
 * Régua curta em cobre, desenhada da esquerda para a direita.
 * É o acento da cena: cobre preenchido, no máximo um por cena.
 */
export const Regua: React.FC<{ atrasoFrames?: number; largura?: number }> = ({
  atrasoFrames = 0,
  largura = 96,
}) => {
  const frame = useCurrentFrame();

  return (
    <svg width={largura} height={6} style={{ display: "block" }}>
      <line
        x1={0}
        y1={3}
        x2={largura}
        y2={3}
        stroke={cores.cobre}
        strokeWidth={6}
        strokeLinecap="round"
        {...desenho(frame - atrasoFrames, largura)}
      />
    </svg>
  );
};
