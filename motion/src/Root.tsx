import { Composition, Still } from "remotion";

import { Reel } from "./Reel";
import { Tokens } from "./Tokens";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Reel"
        component={Reel}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ assinatura: "Thiago Azeredo" }}
      />
      <Still id="Tokens" component={Tokens} width={1080} height={1920} />
    </>
  );
};
