/** `card_conceito`: define um termo. Termo + até 12 palavras de definição. */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { entradaSuave } from "../motion";
import { cores, espaco, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, Card, LARGURA_UTIL, Regua } from "./base";

export const CardConceito: React.FC<{
  cena: Extract<Cena, { tipo: "card_conceito" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      <Card
        brilho={cena.brilho}
        style={{
          width: LARGURA_UTIL,
          padding: espaco.distante,
          display: "flex",
          flexDirection: "column",
          gap: espaco.proximo,
        }}
      >
        <Regua atrasoFrames={6} />
        <div style={{ color: cores.creme, ...tipografia.termo }}>
          {cena.conteudo.termo}
        </div>
        <div
          style={{
            color: cores.creme60,
            ...tipografia.corpo,
            ...entradaSuave(frame, fps, 10),
          }}
        >
          {cena.conteudo.definicao}
        </div>
      </Card>
    </AreaCena>
  );
};
