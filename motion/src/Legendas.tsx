/**
 * Legendas na faixa da divisória (900 a 1040 px).
 *
 * Padrão da skill `reels-legendas`: Hanken Grotesk 700, creme, contorno de
 * 6 px em navy, no máximo 2 linhas. Uma palavra destacada por bloco, em
 * cobre, com o pulso de escala do preset `destaque` no frame em que ela é
 * falada — o mesmo frame em que a cena correspondente entra.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { destaque } from "./motion";
import { cores, layout, legenda as tokens, tipografia } from "./theme";
import type { BlocoLegenda } from "./tipos";

const Palavra: React.FC<{
  texto: string;
  destacada: boolean;
  inicio: number;
}> = ({ texto, destacada, inicio }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <span
      style={{
        display: "inline-block",
        color: destacada ? tokens.corDestaque : tokens.corTexto,
        ...(destacada ? destaque(frame, Math.round(inicio * fps)) : null),
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

  return (
    <div
      style={{
        position: "absolute",
        top: layout.divisoria.topo,
        left: 0,
        width: 1080,
        height: layout.divisoria.altura,
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
          columnGap: 14,
          rowGap: 0,
          // ~28 caracteres por linha no corpo de 54 px: passando disso, o
          // bloco quebra na segunda linha em vez de esticar de ponta a ponta.
          maxWidth: 760,
          lineHeight: 1.1,
          ...tipografia.legenda,
          // Contorno navy: a legenda continua legível quando encosta na
          // borda do vídeo.
          WebkitTextStroke: `${tokens.contorno}px ${cores.navy}`,
          paintOrder: "stroke fill",
        }}
      >
        {bloco.palavras.map((palavra, i) => (
          <Palavra
            key={`${palavra.inicio}-${palavra.texto}`}
            texto={palavra.texto}
            destacada={i === bloco.destaque}
            inicio={palavra.inicio}
          />
        ))}
      </div>
    </div>
  );
};
