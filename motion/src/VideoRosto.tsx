/**
 * O vídeo gravado, nítido, na faixa de baixo.
 *
 * Duas diferenças para a v1: o rosto desce para 1240 px (um terço do alto da
 * faixa, longe dos cards) e o topo do vídeo **dissolve** no fundo desfocado em
 * 150 px. É esse degradê que substitui a emenda reta de 900 px — a skill
 * `reels-composicao` proíbe qualquer linha reta separando as duas metades.
 */

import { Video } from "@remotion/media";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";

import { zoomEnfase } from "./motion";
import { cores, layout } from "./theme";
import type { Enquadramento, JanelaZoom } from "./tipos";

export const VideoRosto: React.FC<{
  arquivo: string;
  enquadramento: Enquadramento;
  fonte: { largura: number; altura: number };
  zooms?: readonly JanelaZoom[];
}> = ({ arquivo, enquadramento, fonte, zooms = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const faixa = { largura: 1080, altura: layout.video.altura };

  // Sem vídeo (os defaultProps do Studio), a faixa fica como um bloco vazio.
  if (!arquivo) {
    return (
      <div
        style={{
          position: "absolute",
          top: layout.video.topo,
          left: 0,
          width: faixa.largura,
          height: faixa.altura,
          backgroundColor: cores.reforco,
        }}
      />
    );
  }

  // Cover: a menor escala que ainda preenche a faixa inteira.
  const escalaCover = Math.max(
    faixa.largura / fonte.largura,
    faixa.altura / fonte.altura,
  );
  const escala = escalaCover * (enquadramento.zoom || 1);
  const largura = fonte.largura * escala;
  const altura = fonte.altura * escala;

  // Leva o rosto para `layout.rosto`, sem deixar borda vazia na faixa.
  const limitar = (valor: number, minimo: number) =>
    Math.min(0, Math.max(minimo, valor));

  // ...mas antes garante que a cabeça caia depois do degradê. A dissolução no
  // alto da faixa come o que estiver debaixo dela: com o rosto alto no quadro,
  // o topo da cabeça desaparecia. `topo_cabeca` é medido por vídeo.
  const topoCabeca =
    enquadramento.topo_cabeca ?? enquadramento.foco_rosto - 0.15;
  const fimDegrade = layout.video.degrade + layout.folgaCabeca;
  const alvoRosto = Math.max(
    layout.rosto - layout.video.topo,
    fimDegrade + (enquadramento.foco_rosto - topoCabeca) * altura,
  );

  const topo = limitar(
    alvoRosto - enquadramento.foco_rosto * altura,
    faixa.altura - altura,
  );
  const esquerda = limitar(
    (faixa.largura - largura) / 2,
    faixa.largura - largura,
  );

  // Sem isso o vídeo fica parado os 47 segundos inteiros. A skill
  // `reels-movimento` limita a um zoom a cada 8 s; quem espaça é o planejador.
  const janela = zooms.find(
    (z) => frame >= z.inicio * fps && frame < (z.fim + 1) * fps,
  );
  const ampliacao = janela
    ? zoomEnfase(
        frame,
        Math.round(janela.inicio * fps),
        Math.round((janela.fim - janela.inicio) * fps),
      )
    : 1;

  return (
    <div
      style={{
        position: "absolute",
        top: layout.video.topo,
        left: 0,
        width: faixa.largura,
        height: faixa.altura,
        overflow: "hidden",
        // O topo some gradualmente, revelando o fundo vivo por baixo.
        maskImage: `linear-gradient(to bottom, transparent 0px, black ${layout.video.degrade}px)`,
        WebkitMaskImage: `linear-gradient(to bottom, transparent 0px, black ${layout.video.degrade}px)`,
      }}
    >
      <Video
        src={staticFile(arquivo)}
        style={{
          position: "absolute",
          top: topo,
          left: esquerda,
          width: largura,
          height: altura,
          // Zoom de ênfase: cresce em torno do rosto, não do centro do
          // quadro, senão a cabeça escorrega para fora do enquadramento.
          scale: ampliacao,
          transformOrigin: `50% ${enquadramento.foco_rosto * 100}%`,
        }}
      />
    </div>
  );
};
