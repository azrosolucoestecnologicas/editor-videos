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
        boxShadow: sombras.flutuante,
        border: escura ? `1px solid ${cores.reforco}` : "none",
      }}
    />
    <div>
      <div style={{ color: cores.tinta, ...tipografia.item }}>{nome}</div>
      <div style={{ color: cores.tintaFraca, ...tipografia.rotulo }}>
        {valor}
      </div>
    </div>
  </div>
);

export const Tokens: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: cores.chao,
      padding: layout.margem,
      paddingTop: layout.topoSeguro,
      display: "flex",
      flexDirection: "column",
      gap: espaco.distante,
    }}
  >
    <div style={{ color: cores.tinta, ...tipografia.tituloCena }}>
      Tokens dos reels
    </div>

    <div
      style={{ display: "flex", flexDirection: "column", gap: espaco.proximo }}
    >
      <Amostra nome="chao" valor={cores.chao} escura />
      <Amostra nome="cobre" valor={cores.acento} />
      <Amostra nome="tinta" valor={cores.tinta} />
      <Amostra nome="navySoft" valor={cores.reforco} />
    </div>

    <div
      style={{ display: "flex", flexDirection: "column", gap: espaco.proximo }}
    >
      <div style={{ color: cores.tinta, ...tipografia.termo }}>
        Fraunces 600, termo
      </div>
      <div style={{ color: cores.tinta, ...tipografia.corpo }}>
        Hanken Grotesk 500, corpo com acentuacao: coacao, inducao, Sumula
      </div>
      <div style={{ color: cores.tintaFraca, ...tipografia.rotulo }}>
        Rotulo de diagrama
      </div>
      <div style={{ color: cores.acento, ...tipografia.numero }}>331</div>
      <div style={{ color: cores.tinta, ...tipografia.referencia }}>
        Art. 7o, XIII
      </div>
      <div style={{ color: cores.tinta, ...tipografia.legenda }}>
        Legenda em Hanken 700
      </div>
    </div>
  </AbsoluteFill>
);
