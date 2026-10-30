/**
 * `cena_apoio`: b-roll ilustrando a fala.
 *
 * É um card cujo conteúdo é vídeo, não um corte para tela cheia — mesmos
 * cantos, mesma sombra, mesma entrada e saída das outras cenas. A skill
 * `reels-movimento` é explícita: nunca corte seco para o b-roll, porque é
 * isso que faz parecer clipe de banco colado por cima.
 *
 * Mudo, sempre. O áudio do reel é a fala dele, e um clipe com som próprio
 * disputaria com ela.
 */

import {
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import { entrada } from "../motion";
import { cenaApoio, cores, espaco, raios, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { ALTURA_UTIL, AreaCena, Card, LARGURA_UTIL } from "./base";

export const CenaApoio: React.FC<{
  cena: Extract<Cena, { tipo: "cena_apoio" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { clipe, rotulo } = cena.conteudo;

  return (
    <AreaCena duracaoFrames={duracaoFrames}>
      {/* Sem flex e sem padding: o clipe é o conteúdo do card, de borda a
          borda, e o rótulo pousa sobre ele. */}
      <Card style={{ width: LARGURA_UTIL, height: ALTURA_UTIL, padding: 0 }}>
        {clipe ? (
          // OffthreadVideo e não Video: o quadro é extraído fora da aba, que
          // é o que mantém o render previsível quando há vídeo dentro de
          // vídeo. `muted` não é opção — ver o cabeçalho.
          <OffthreadVideo
            src={staticFile(clipe)}
            muted
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        ) : null}

        {rotulo ? (
          <div
            style={{
              position: "absolute",
              left: espaco.proximo,
              bottom: espaco.proximo,
              padding: cenaApoio.paddingRotulo,
              borderRadius: raios.pilula,
              // O rótulo precisa de fundo próprio: ele corre sobre imagem,
              // que pode ser clara ou escura no mesmo clipe.
              backgroundColor: cores.vidro,
              color: cores.tinta,
              ...tipografia.rotulo,
              ...entrada(frame, fps, cenaApoio.atrasoRotulo),
            }}
          >
            {rotulo}
          </div>
        ) : null}
      </Card>
    </AreaCena>
  );
};
