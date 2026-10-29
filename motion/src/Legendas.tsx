/**
 * Legendas na zona segura inferior, sobre o vídeo.
 *
 * Três níveis de ênfase (skill `reels-legendas`): normal em creme, chave em
 * cobre e máxima em creme sobre pílula cobre. Cada palavra dá um pop ao ser
 * falada — é pop, não balanço.
 *
 * O contorno navy agora é obrigatório: a legenda ficou sobre a imagem, não
 * sobre fundo chapado.
 */

import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

import { cores, layout, legenda as tokens, raios, tipografia } from "./theme";
import type { BlocoLegenda } from "./tipos";

type Nivel = "normal" | "chave" | "maxima";

const Palavra: React.FC<{
  texto: string;
  nivel: Nivel;
  inicio: number;
}> = ({ texto, nivel, inicio }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const inicioFrame = Math.round(inicio * fps);
  const pop = interpolate(
    frame - inicioFrame,
    [0, tokens.framesPop, tokens.framesPop * 2],
    [1, tokens.escalaPop, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      output: "perceptual-scale",
    },
  );

  const maxima = nivel === "maxima";

  return (
    <span
      style={{
        display: "inline-block",
        scale: pop,
        color: maxima
          ? tokens.maximaTexto
          : nivel === "chave"
            ? tokens.corChave
            : tokens.corTexto,
        ...(maxima
          ? {
              backgroundColor: tokens.maximaFundo,
              borderRadius: raios.pilula,
              padding: tokens.maximaPadding,
              // Na pílula o contorno atrapalha: o fundo já dá o contraste.
              WebkitTextStroke: "0px transparent",
            }
          : null),
      }}
    >
      {texto}
    </span>
  );
};

export const Legendas: React.FC<{ blocos: readonly BlocoLegenda[] }> = ({
  blocos,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const segundos = frame / fps;

  const bloco = blocos.find((b) => b.inicio <= segundos && segundos < b.fim);
  if (!bloco) {
    return null;
  }

  const nivelDe = (i: number): Nivel => {
    if (bloco.maxima === i) {
      return "maxima";
    }
    return bloco.destaque === i ? "chave" : "normal";
  };

  return (
    <div
      style={{
        position: "absolute",
        // Centrada em `layout.legenda`, dentro da zona segura inferior.
        top: layout.legenda - 110,
        left: 0,
        width: 1080,
        height: 220,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: `0 ${layout.margem}px`,
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          // O contorno de 6 px cresce para os dois lados de cada palavra e come
          // o espaço entre elas: sem compensar, "dupla Black" vira "duplaBlack".
          columnGap: 14 + tokens.contorno * 2,
          rowGap: 6,
          maxWidth: tokens.larguraMaxima,
          lineHeight: 1.1,
          ...tipografia.legenda,
          WebkitTextStroke: `${tokens.contorno}px ${cores.navy}`,
          paintOrder: "stroke fill",
        }}
      >
        {bloco.palavras.map((palavra, i) => (
          <Palavra
            key={`${palavra.inicio}-${palavra.texto}`}
            texto={palavra.texto}
            nivel={nivelDe(i)}
            inicio={palavra.inicio}
          />
        ))}
      </div>
    </div>
  );
};
