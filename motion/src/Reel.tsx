/**
 * Esqueleto da composicao do reel.
 *
 * Fase 1: fixa o formato (1080x1920 @ 30 fps) e as tres faixas da skill
 * `reels-composicao`. As cenas, as legendas e o video entram na Fase 3.
 */

import { AbsoluteFill } from "remotion";

import { cores, grade, layout, tipografia } from "./theme";

/** Grade sutil atras das cenas: linhas navySoft a 30%, espacamento 72 px. */
export const Grade: React.FC<{ altura: number }> = ({ altura }) => {
  const colunas = Math.floor(layout.painel.altura / grade.passo);
  const linhas = Math.floor(altura / grade.passo);

  return (
    <svg
      width={1080}
      height={altura}
      style={{ position: "absolute", inset: 0, opacity: grade.opacidade }}
    >
      {Array.from({ length: colunas + 1 }, (_, i) => (
        <line
          key={`v${i}`}
          x1={i * grade.passo}
          y1={0}
          x2={i * grade.passo}
          y2={altura}
          stroke={grade.cor}
          strokeWidth={1}
        />
      ))}
      {Array.from({ length: linhas + 1 }, (_, i) => (
        <line
          key={`h${i}`}
          x1={0}
          y1={i * grade.passo}
          x2={1080}
          y2={i * grade.passo}
          stroke={grade.cor}
          strokeWidth={1}
        />
      ))}
    </svg>
  );
};

/** Assinatura discreta, fixa no canto superior esquerdo do painel. */
export const Assinatura: React.FC<{ texto: string }> = ({ texto }) => (
  <div
    style={{
      position: "absolute",
      left: layout.margem,
      top: layout.topoSeguro,
      color: cores.creme60,
      ...tipografia.assinatura,
    }}
  >
    {texto}
  </div>
);

export const Reel: React.FC<{ assinatura: string }> = ({ assinatura }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: cores.navy }}>
      {/* Painel de animacao: 0 a 900 px */}
      <div
        style={{
          position: "absolute",
          top: layout.painel.topo,
          left: 0,
          width: 1080,
          height: layout.painel.altura,
          backgroundColor: cores.navy,
        }}
      >
        <Grade altura={layout.painel.altura} />
        <Assinatura texto={assinatura} />
      </div>

      {/* Faixa da divisoria: 900 a 1040 px (legendas na Fase 3) */}
      <div
        style={{
          position: "absolute",
          top: layout.divisoria.topo,
          left: 0,
          width: 1080,
          height: layout.divisoria.altura,
          backgroundColor: cores.navy,
        }}
      />

      {/* Video: 1040 a 1920 px (entra na Fase 3) */}
      <div
        style={{
          position: "absolute",
          top: layout.video.topo,
          left: 0,
          width: 1080,
          height: layout.video.altura,
          backgroundColor: cores.navySoft,
        }}
      />
    </AbsoluteFill>
  );
};
