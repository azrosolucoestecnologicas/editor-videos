/**
 * `fluxo`: 3 a 5 caixas ligadas por setas, rótulos de até 3 palavras.
 *
 * Ordem da skill `reels-movimento`: caixa, depois a seta desenhando, depois a
 * próxima caixa. Até 3 etapas o fluxo é horizontal; de 4 em diante ele empilha,
 * senão as caixas ficam estreitas demais para o rótulo.
 *
 * Todas as caixas levam o fio metálico — ele é material, não sinal. O cobre
 * preenchido da cena é o rótulo da última caixa: é onde o fluxo chega.
 */

import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

import { ATRASO_ITEM_FRAMES, desenho, duracoes } from "../motion";
import { cores, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, atrasoDe, Card, LARGURA_UTIL } from "./base";

const SETA_HORIZONTAL = 72;
const SETA_VERTICAL = 44;
/** Empilhado, a caixa não precisa da largura toda: o rótulo é curto. */
const FRACAO_VERTICAL = 0.72;
/** A seta começa a ser desenhada quando a caixa anterior terminou de entrar. */
const ATRASO_SETA = 10;

const Seta: React.FC<{ atrasoFrames: number; vertical: boolean }> = ({
  atrasoFrames,
  vertical,
}) => {
  const frame = useCurrentFrame();
  const comprimento = vertical ? SETA_VERTICAL : SETA_HORIZONTAL;
  const decorrido = frame - atrasoFrames;
  // A ponta só aparece depois que a linha chegou ao fim.
  const opacidadePonta = interpolate(
    decorrido,
    [duracoes.desenho - 4, duracoes.desenho + 4],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const largura = vertical ? 24 : comprimento;
  const altura = vertical ? comprimento : 24;

  return (
    <svg width={largura} height={altura} style={{ flexShrink: 0 }}>
      <line
        x1={vertical ? 12 : 0}
        y1={vertical ? 0 : 12}
        x2={vertical ? 12 : comprimento - 10}
        y2={vertical ? comprimento - 10 : 12}
        style={{ stroke: cores.tintaFraca }}
        strokeWidth={3}
        strokeLinecap="round"
        {...desenho(decorrido, comprimento)}
      />
      <polyline
        points={
          vertical
            ? `6,${comprimento - 14} 12,${comprimento - 2} 18,${comprimento - 14}`
            : `${comprimento - 14},6 ${comprimento - 2},12 ${comprimento - 14},18`
        }
        fill="none"
        style={{ stroke: cores.tintaFraca }}
        strokeWidth={3}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={opacidadePonta}
      />
    </svg>
  );
};

export const Fluxo: React.FC<{
  cena: Extract<Cena, { tipo: "fluxo" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const { fps } = useVideoConfig();

  const etapas = cena.conteudo.etapas;
  const vertical = etapas.length > 3;
  const atrasos = etapas.map((etapa, i) =>
    etapa._em != null
      ? atrasoDe(etapa._em, cena.inicio, fps)
      : ATRASO_ITEM_FRAMES * 2 * i,
  );

  const larguraCaixa = vertical
    ? LARGURA_UTIL * FRACAO_VERTICAL
    : (LARGURA_UTIL - SETA_HORIZONTAL * (etapas.length - 1)) / etapas.length;

  return (
    <AreaCena duracaoFrames={duracaoFrames} alinhamento="centro">
      <div
        style={{
          display: "flex",
          flexDirection: vertical ? "column" : "row",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {etapas.map((etapa, i) => {
          const ultima = i === etapas.length - 1;
          return (
            <span key={etapa.rotulo} style={{ display: "contents" }}>
              {i > 0 ? (
                <Seta
                  atrasoFrames={atrasos[i - 1] + ATRASO_SETA}
                  vertical={vertical}
                />
              ) : null}
              <Card
                atrasoFrames={atrasos[i]}
                brilho={ultima && cena.brilho}
                style={{
                  width: larguraCaixa,
                  minHeight: vertical ? undefined : 150,
                  padding: vertical ? 16 : 20,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div
                  style={{
                    textAlign: "center",
                    color: ultima ? cores.acento : cores.tinta,
                    ...tipografia.rotuloCaixa,
                  }}
                >
                  {etapa.rotulo}
                </div>
              </Card>
            </span>
          );
        })}
      </div>
    </AreaCena>
  );
};
