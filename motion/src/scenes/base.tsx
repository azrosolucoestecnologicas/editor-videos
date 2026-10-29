/**
 * Peças comuns a todas as cenas.
 *
 * `AreaCena` entrega a zona segura do painel (skill `reels-composicao`) e a
 * saída da cena; cada elemento lá dentro cuida da própria entrada, com o
 * atraso que a palavra-gatilho dele determina.
 */

import { useCurrentFrame } from "remotion";

import { desenho, duracoes, saida } from "../motion";
import { cores, espaco, layout } from "../theme";

/** Largura útil do painel, já descontadas as margens laterais. */
export const LARGURA_UTIL = 1080 - layout.margem * 2;

/** A assinatura ocupa a primeira faixa logo abaixo do topo seguro. */
const TOPO_CONTEUDO = layout.topoSeguro + 56;

/** Altura útil: da assinatura até um respiro antes da divisória. */
export const ALTURA_UTIL =
  layout.painel.altura - TOPO_CONTEUDO - espaco.distante;

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
  // nunca um corte seco entre cenas animadas.
  const inicioSaida = Math.max(1, duracaoFrames - duracoes.sobreposicaoCenas);
  const estiloSaida = frame >= inicioSaida ? saida(frame, inicioSaida) : null;
  const centro = alinhamento === "centro";

  return (
    <div
      style={{
        position: "absolute",
        left: layout.margem,
        top: TOPO_CONTEUDO,
        width: LARGURA_UTIL,
        height: ALTURA_UTIL,
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
 * Régua curta em cobre, desenhada da esquerda para a direita.
 * É o acento da cena: no máximo um elemento cobre por cena.
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
