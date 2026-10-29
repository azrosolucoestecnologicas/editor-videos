/**
 * `citacao_legal`: artigo, súmula ou tese em destaque.
 *
 * Documento estilizado da skill `reels-estilo`: card creme, cabeçalho em
 * JetBrains Mono, corpo em Hanken e um sublinhado em cobre. Sem `trecho`,
 * mostra só a referência — é o que a skill `reels-composicao` manda fazer
 * quando o texto do dispositivo não foi conferido na fonte.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { entradaSuave } from "../motion";
import { cores, espaco, raios, sombras, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, LARGURA_UTIL, Regua } from "./base";

export const CitacaoLegal: React.FC<{
  cena: Extract<Cena, { tipo: "citacao_legal" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { referencia, trecho } = cena.conteudo;

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      <div
        style={{
          width: LARGURA_UTIL,
          padding: espaco.distante,
          borderRadius: raios.card,
          backgroundColor: cores.creme,
          boxShadow: sombras.card,
          display: "flex",
          flexDirection: "column",
          gap: espaco.proximo,
          ...entradaSuave(frame, fps, 0),
        }}
      >
        <div style={{ color: cores.navy, ...tipografia.referencia }}>{referencia}</div>
        {trecho ? (
          <>
            <Regua atrasoFrames={10} largura={140} />
            <div style={{ color: cores.navy, ...tipografia.corpo }}>{trecho}</div>
          </>
        ) : null}
      </div>
    </AreaCena>
  );
};
