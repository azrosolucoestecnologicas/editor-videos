/**
 * `documento`: um instrumento jurídico com selo e cláusulas entrando uma a uma.
 *
 * É a cena para quando a fala percorre as cláusulas de um documento —
 * escritura, contrato, procuração. A diferença para a `lista` é o que a cena
 * afirma: a lista enumera ideias, o documento mostra um papel que existe e as
 * cláusulas que estão nele. Por isso o card é preenchido, o título vem em
 * mono caixa-alta e há um selo: é a gramática de peça impressa.
 *
 * A cláusula que acabou de entrar fica no acento, as anteriores recuam para
 * checada. Assim só existe um elemento acento preenchido por instante, que é
 * a regra da skill `reels-estilo`.
 */

import { Check } from "lucide-react";
import { useCurrentFrame, useVideoConfig } from "remotion";

import { ATRASO_ITEM_FRAMES, entrada } from "../motion";
import { cores, documento, espaco, raios, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, atrasoDe, Card, LARGURA_UTIL } from "./base";

/** O selo de cera: um disco no acento com o anel mais escuro por dentro. */
const Selo: React.FC<{ atrasoFrames: number }> = ({ atrasoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div
      style={{
        width: documento.selo,
        height: documento.selo,
        borderRadius: raios.pilula,
        backgroundColor: cores.acento,
        border: `3px solid ${cores.acentoClaro}`,
        flexShrink: 0,
        ...entrada(frame, fps, atrasoFrames),
      }}
    />
  );
};

export const Documento: React.FC<{
  cena: Extract<Cena, { tipo: "documento" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const clausulas = cena.conteudo.clausulas.map((clausula, i) => ({
    ...clausula,
    atraso:
      clausula._em != null
        ? atrasoDe(clausula._em, cena.inicio, fps)
        : documento.atrasoPrimeira + ATRASO_ITEM_FRAMES * i,
  }));

  const ativa = clausulas.reduce(
    (melhor, clausula, i) => (frame >= clausula.atraso ? i : melhor),
    -1,
  );

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      <Card
        brilho={cena.brilho}
        preenchido
        style={{
          width: LARGURA_UTIL,
          padding: espaco.distante,
          display: "flex",
          flexDirection: "column",
          gap: espaco.proximo,
        }}
      >
        {/* Cabeçalho: o nome do instrumento e o selo, como num papel real. */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: espaco.proximo,
            paddingBottom: espaco.proximo,
            borderBottom: `2px solid ${cores.acento}`,
          }}
        >
          <div
            style={{
              color: cores.tintaSuperficie,
              ...tipografia.documentoTitulo,
            }}
          >
            {cena.conteudo.titulo}
          </div>
          <Selo atrasoFrames={documento.atrasoSelo} />
        </div>

        {clausulas.map((clausula, i) => {
          const atual = i === ativa;
          return (
            <div
              key={clausula.texto}
              style={{
                display: "flex",
                alignItems: "center",
                gap: espaco.proximo,
                padding: documento.padding,
                borderRadius: raios.card,
                // Só a cláusula da vez recebe o fundo do acento; as já ditas
                // ficam neutras para não disputarem o olho com ela.
                backgroundColor: atual ? cores.acento : "transparent",
                ...entrada(frame, fps, clausula.atraso),
              }}
            >
              <div
                style={{
                  width: documento.marcador,
                  height: documento.marcador,
                  borderRadius: 6,
                  border: `2px solid ${atual ? cores.superficie : cores.acento}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                {i <= ativa ? (
                  <Check
                    size={documento.marcador - 8}
                    strokeWidth={3}
                    color={atual ? cores.superficie : cores.acento}
                  />
                ) : null}
              </div>
              <div
                style={{
                  color: atual ? cores.superficie : cores.tintaSuperficie,
                  ...tipografia.item,
                }}
              >
                {clausula.texto}
              </div>
            </div>
          );
        })}
      </Card>
    </AreaCena>
  );
};
