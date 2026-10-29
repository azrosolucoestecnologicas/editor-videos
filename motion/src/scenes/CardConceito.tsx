/** `card_conceito`: define um termo. Termo + até 12 palavras de definição. */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { entrada, entradaSuave } from "../motion";
import { cores, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, Regua } from "./base";

export const CardConceito: React.FC<{
  cena: Extract<Cena, { tipo: "card_conceito" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      <Regua />
      <div style={{ color: cores.creme, ...tipografia.termo, ...entrada(frame, fps, 2) }}>
        {cena.conteudo.termo}
      </div>
      <div
        style={{
          color: cores.creme60,
          ...tipografia.corpo,
          maxWidth: 820,
          ...entradaSuave(frame, fps, 8),
        }}
      >
        {cena.conteudo.definicao}
      </div>
    </AreaCena>
  );
};
