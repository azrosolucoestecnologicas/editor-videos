/**
 * Still de conferencia dos tokens: paleta, tipografia, raios e sombra.
 * Nao faz parte do reel; existe para validar `theme.ts` num PNG.
 */

import { AbsoluteFill } from "remotion";

import { cores, espaco, layout, raios, sombras, tipografia } from "./theme";

const Amostra: React.FC<{ nome: string; valor: string; escura?: boolean }> = ({
  nome,
  valor,
  escura,
}) => (
  <div style={{ display: "flex", alignItems: "center", gap: espaco.proximo }}>
    <div
      style={{
        width: 160,
        height: 100,
        backgroundColor: valor,
        borderRadius: raios.card,
        boxShadow: sombras.card,
        border: escura ? `1px solid ${cores.navySoft}` : "none",
      }}
    />
    <div>
      <div style={{ color: cores.creme, ...tipografia.item }}>{nome}</div>
      <div style={{ color: cores.creme60, ...tipografia.rotulo }}>{valor}</div>
    </div>
  </div>
);

export const Tokens: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: cores.navy,
      padding: layout.margem,
      paddingTop: layout.topoSeguro,
      display: "flex",
      flexDirection: "column",
      gap: espaco.distante,
    }}
  >
    <div style={{ color: cores.creme, ...tipografia.tituloCena }}>
      Tokens dos reels
    </div>

    <div style={{ display: "flex", flexDirection: "column", gap: espaco.proximo }}>
      <Amostra nome="navy" valor={cores.navy} escura />
      <Amostra nome="cobre" valor={cores.cobre} />
      <Amostra nome="creme" valor={cores.creme} />
      <Amostra nome="navySoft" valor={cores.navySoft} />
    </div>

    <div style={{ display: "flex", flexDirection: "column", gap: espaco.proximo }}>
      <div style={{ color: cores.creme, ...tipografia.termo }}>
        Fraunces 600, termo
      </div>
      <div style={{ color: cores.creme, ...tipografia.corpo }}>
        Hanken Grotesk 500, corpo com acentuacao: coacao, inducao, Sumula
      </div>
      <div style={{ color: cores.creme60, ...tipografia.rotulo }}>
        Rotulo de diagrama
      </div>
      <div style={{ color: cores.cobre, ...tipografia.numero }}>331</div>
      <div style={{ color: cores.creme, ...tipografia.referencia }}>
        Art. 7o, XIII
      </div>
      <div style={{ color: cores.creme, ...tipografia.legenda }}>
        Legenda em Hanken 700
      </div>
    </div>
  </AbsoluteFill>
);
