/**
 * `comparacao`: duas colunas, até 3 linhas cada.
 *
 * A coluna da direita carrega o acento em cobre — é o lado que a frase
 * enfatiza (o depois, o problema, a IA). A da esquerda fica neutra.
 */

import { ATRASO_ITEM_FRAMES } from "../motion";
import { cores, espaco, tipografia } from "../theme";
import type { Cena, Coluna as TipoColuna } from "../tipos";
import { AreaCena, Card, LARGURA_UTIL } from "./base";

const LARGURA_COLUNA = (LARGURA_UTIL - espaco.proximo) / 2;

const Coluna: React.FC<{
  coluna: TipoColuna;
  destacada: boolean;
  atrasoFrames: number;
  brilho?: boolean;
}> = ({ coluna, destacada, atrasoFrames, brilho }) => (
  <Card
    atrasoFrames={atrasoFrames}
    brilho={brilho}
    style={{
      width: LARGURA_COLUNA,
      // Iguala a altura das duas colunas quando uma delas quebra numa
      // segunda linha.
      alignSelf: "stretch",
      padding: espaco.proximo,
    }}
  >
    <div style={{ display: "flex", flexDirection: "column", gap: espaco.proximo }}>
      <div
        style={{
          color: destacada ? cores.cobre : cores.creme60,
          ...tipografia.rotulo,
        }}
      >
        {coluna.titulo}
      </div>
      {coluna.linhas.map((linha) => (
        <div key={linha} style={{ color: cores.creme, ...tipografia.item }}>
          {linha}
        </div>
      ))}
    </div>
  </Card>
);

export const Comparacao: React.FC<{
  cena: Extract<Cena, { tipo: "comparacao" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => (
  <AreaCena duracaoFrames={duracaoFrames}>
    {/* Entram na ordem de leitura: esquerda, depois direita. */}
    <div style={{ display: "flex", gap: espaco.proximo, alignItems: "stretch" }}>
      <Coluna coluna={cena.conteudo.esquerda} destacada={false} atrasoFrames={0} />
      <Coluna
        coluna={cena.conteudo.direita}
        destacada
        atrasoFrames={ATRASO_ITEM_FRAMES}
        brilho={cena.brilho}
      />
    </div>
  </AreaCena>
);
