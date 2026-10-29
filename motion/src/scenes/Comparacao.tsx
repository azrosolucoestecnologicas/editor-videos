/**
 * `comparacao`: duas colunas, até 3 linhas cada.
 *
 * A coluna da direita carrega o acento em cobre — é o lado que a frase
 * enfatiza (o depois, o problema, a IA). A da esquerda fica neutra.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { ATRASO_ITEM_FRAMES, entrada } from "../motion";
import { cores, espaco, raios, sombras, tipografia } from "../theme";
import type { Cena, Coluna as TipoColuna } from "../tipos";
import { AreaCena, LARGURA_UTIL } from "./base";

const LARGURA_COLUNA = (LARGURA_UTIL - espaco.proximo) / 2;

const Coluna: React.FC<{
  coluna: TipoColuna;
  destacada: boolean;
  atrasoFrames: number;
}> = ({ coluna, destacada, atrasoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div
      style={{
        width: LARGURA_COLUNA,
        padding: espaco.proximo,
        borderRadius: raios.card,
        backgroundColor: cores.navySoft,
        boxShadow: sombras.card,
        display: "flex",
        flexDirection: "column",
        gap: espaco.proximo,
        ...entrada(frame, fps, atrasoFrames),
      }}
    >
      <div style={{ color: destacada ? cores.cobre : cores.creme60, ...tipografia.rotulo }}>
        {coluna.titulo}
      </div>
      {coluna.linhas.map((linha) => (
        <div key={linha} style={{ color: cores.creme, ...tipografia.item }}>
          {linha}
        </div>
      ))}
    </div>
  );
};

export const Comparacao: React.FC<{
  cena: Extract<Cena, { tipo: "comparacao" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => (
  <AreaCena duracaoFrames={duracaoFrames}>
    {/* Entram na ordem de leitura: esquerda, depois direita. */}
    <div style={{ display: "flex", gap: espaco.proximo, alignItems: "flex-start" }}>
      <Coluna coluna={cena.conteudo.esquerda} destacada={false} atrasoFrames={0} />
      <Coluna
        coluna={cena.conteudo.direita}
        destacada
        atrasoFrames={ATRASO_ITEM_FRAMES}
      />
    </div>
  </AreaCena>
);
