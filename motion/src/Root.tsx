import { CalculateMetadataFunction, Composition, Still } from "remotion";

import { Reel } from "./Reel";
import { Tokens } from "./Tokens";
import type { PropsReel } from "./tipos";

/** Duração e fps saem do próprio plano, que já conhece o vídeo cortado. */
const calcularMetadados: CalculateMetadataFunction<PropsReel> = ({
  props,
}) => ({
  durationInFrames: Math.max(
    1,
    Math.round(props.plano.duracao * props.plano.fps),
  ),
  fps: props.plano.fps,
});

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Reel"
        component={Reel}
        calculateMetadata={calcularMetadados}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          plano: {
            versao: 1,
            video: "",
            duracao: 10,
            fps: 30,
            assinatura: "",
            fonte: { largura: 1080, altura: 1920 },
            enquadramento: {
              foco_rosto: 0.36,
              zoom: 1,
              origem: "padrao" as const,
            },
            cenas: [],
          },
          legendas: [],
          video: "",
          videoFundo: "",
        }}
      />
      <Still id="Tokens" component={Tokens} width={1080} height={1920} />
    </>
  );
};
