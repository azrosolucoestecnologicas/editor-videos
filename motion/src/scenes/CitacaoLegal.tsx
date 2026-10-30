/**
 * `citacao_legal`: artigo, súmula ou tese em destaque.
 *
 * Documento estilizado da skill `reels-estilo`: card creme, cabeçalho em
 * JetBrains Mono, corpo em Hanken e um sublinhado em cobre. Sem `trecho`,
 * mostra só a referência — é o que a skill `reels-composicao` manda fazer
 * quando o texto do dispositivo não foi conferido na fonte.
 */

import { cores, espaco, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, Card, LARGURA_UTIL, Regua } from "./base";

export const CitacaoLegal: React.FC<{
  cena: Extract<Cena, { tipo: "citacao_legal" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const { referencia, trecho } = cena.conteudo;

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      <Card
        preenchido
        brilho={cena.brilho}
        style={{
          // Sem trecho, o card encolhe para a referência em vez de esticar
          // uma faixa creme vazia pelo painel inteiro.
          width: trecho ? LARGURA_UTIL : "auto",
          maxWidth: LARGURA_UTIL,
          padding: espaco.distante,
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: espaco.proximo,
          }}
        >
          <div
            style={{ color: cores.tintaSuperficie, ...tipografia.referencia }}
          >
            {referencia}
          </div>
          {trecho ? (
            <>
              <Regua atrasoFrames={12} largura={140} />
              <div
                style={{ color: cores.tintaSuperficie, ...tipografia.corpo }}
              >
                {trecho}
              </div>
            </>
          ) : null}
        </div>
      </Card>
    </AreaCena>
  );
};
