/**
 * `sintese`: o fechamento, uma frase de até 10 palavras.
 *
 * Depois da entrada ela fica parada: a skill `reels-ritmo` pede que os
 * últimos segundos não tenham animação nova.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { entradaSuave } from "../motion";
import { cores, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, FraseComChave, Regua } from "./base";

export const Sintese: React.FC<{
  cena: Extract<Cena, { tipo: "sintese" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AreaCena duracaoFrames={duracaoFrames} alinhamento="centro">
      <Regua largura={140} />
      <div
        style={{
          color: cores.tinta,
          ...tipografia.tituloCena,
          maxWidth: 880,
          lineHeight: 1.15,
          ...entradaSuave(frame, fps, 2),
        }}
      >
        <FraseComChave
          frase={cena.conteudo.frase}
          chave={cena.conteudo.chave}
          atrasoFrames={2}
        />
      </div>
    </AreaCena>
  );
};
