/**
 * Composição do reel: sobreposição com profundidade (skill `reels-composicao`).
 *
 *   1. fundo vivo   o próprio vídeo, ampliado, desfocado e escurecido
 *   2. véu + grade  contraste para o texto, sem matar a cor do cenário
 *   3. vídeo nítido você, com o topo dissolvendo no fundo desfocado
 *   4. cenas        cards flutuando sobre tudo
 *   5. legenda      na zona segura inferior
 *
 * Não existe mais faixa chapada nem emenda reta: é isso que tirava o ar de
 * amador. As cenas se sobrepõem de propósito — a atual sai enquanto a
 * próxima entra.
 */

import { AbsoluteFill, Sequence } from "remotion";

import { FundoVivo } from "./FundoVivo";
import { Legendas } from "./Legendas";
import { ANTECIPACAO_FRAMES, duracoes } from "./motion";
import { CenaDoPlano } from "./scenes";
import { cores, layout, tipografia } from "./theme";
import type { PropsReel } from "./tipos";
import { VideoRosto } from "./VideoRosto";

/** Assinatura discreta, na zona segura do topo. */
const Assinatura: React.FC<{ texto: string }> = ({ texto }) => (
  <div
    style={{
      position: "absolute",
      left: layout.margem,
      top: layout.topoSeguro,
      color: cores.creme60,
      ...tipografia.assinatura,
    }}
  >
    {texto}
  </div>
);

export const Reel: React.FC<PropsReel> = ({
  plano,
  legendas,
  video,
  videoFundo,
}) => {
  const { fps } = plano;

  return (
    <AbsoluteFill style={{ backgroundColor: cores.navy }}>
      <FundoVivo arquivo={videoFundo} />

      <VideoRosto
        arquivo={video}
        enquadramento={plano.enquadramento}
        fonte={plano.fonte}
      />

      {plano.assinatura ? <Assinatura texto={plano.assinatura} /> : null}

      {plano.cenas.map((cena) => {
        // O olho chega antes do ouvido: a cena entra alguns frames antes da
        // palavra-gatilho. A cauda extra deixa a saída terminar por cima da
        // cena seguinte.
        const inicio = Math.round(cena.inicio * fps) - ANTECIPACAO_FRAMES;
        const duracaoCena = Math.round((cena.fim - cena.inicio) * fps);

        return (
          <Sequence
            key={cena.id}
            name={`${cena.id} ${cena.tipo}`}
            from={Math.max(0, inicio)}
            durationInFrames={duracaoCena + duracoes.saida}
            layout="none"
          >
            <CenaDoPlano cena={cena} duracaoFrames={duracaoCena} />
          </Sequence>
        );
      })}

      <Legendas blocos={legendas} />
    </AbsoluteFill>
  );
};
