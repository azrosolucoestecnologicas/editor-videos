/** `icone_destaque`: ideia-chave sem estrutura. Um ícone + até 4 palavras. */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { icone as buscarIcone } from "../icones";
import { entrada } from "../motion";
import { cores, icones, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena } from "./base";

export const IconeDestaque: React.FC<{
  cena: Extract<Cena, { tipo: "icone_destaque" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const Icone = buscarIcone(cena.conteudo.icone);

  return (
    <AreaCena duracaoFrames={duracaoFrames} alinhamento="centro">
      {/* O ícone é o único elemento cobre da cena. */}
      <div style={entrada(frame, fps, 0)}>
        <Icone
          size={icones.tamanho}
          color={cores.acento}
          strokeWidth={icones.strokeWidth}
        />
      </div>
      <div
        style={{
          color: cores.tinta,
          ...tipografia.termo,
          maxWidth: 820,
          ...entrada(frame, fps, 6),
        }}
      >
        {cena.conteudo.texto}
      </div>
    </AreaCena>
  );
};
