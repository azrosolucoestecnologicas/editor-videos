/**
 * `lista`: 2 a 4 itens, até 6 palavras cada, entrando um a um.
 *
 * Cada item entra na palavra que o nomeia (`_em`); sem palavra-gatilho, os
 * itens se escalonam pelo atraso padrão da skill `reels-movimento`.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { ATRASO_ITEM_FRAMES, entrada } from "../motion";
import { cores, espaco, raios, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, atrasoDe } from "./base";

export const Lista: React.FC<{
  cena: Extract<Cena, { tipo: "lista" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const itens = cena.conteudo.itens.map((item, i) => ({
    ...item,
    atraso: item._em != null
      ? atrasoDe(item._em, cena.inicio, fps)
      : ATRASO_ITEM_FRAMES * i,
  }));

  // O marcador em cobre acompanha o último item que entrou: assim só existe
  // um elemento cobre na tela a cada instante.
  const ativo = itens.reduce(
    (melhor, item, i) => (frame >= item.atraso ? i : melhor),
    -1,
  );

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      {cena.conteudo.titulo ? (
        <div
          style={{
            color: cores.creme60,
            ...tipografia.rotulo,
            ...entrada(frame, fps, 0),
          }}
        >
          {cena.conteudo.titulo}
        </div>
      ) : null}

      <div style={{ display: "flex", flexDirection: "column", gap: espaco.proximo }}>
        {itens.map((item, i) => (
          <div
            key={item.texto}
            style={{
              display: "flex",
              alignItems: "center",
              gap: espaco.proximo,
              ...entrada(frame, fps, item.atraso),
            }}
          >
            <div
              style={{
                width: 16,
                height: 16,
                borderRadius: raios.pilula,
                backgroundColor: i === ativo ? cores.cobre : cores.navySoft,
                flexShrink: 0,
              }}
            />
            <div style={{ color: cores.creme, ...tipografia.item }}>{item.texto}</div>
          </div>
        ))}
      </div>
    </AreaCena>
  );
};
