/**
 * O vídeo gravado, nítido, na faixa de baixo.
 *
 * Duas diferenças para a v1: o rosto desce para 1240 px (um terço do alto da
 * faixa, longe dos cards) e o topo do vídeo **dissolve** no fundo desfocado em
 * 150 px. É esse degradê que substitui a emenda reta de 900 px — a skill
 * `reels-composicao` proíbe qualquer linha reta separando as duas metades.
 */

import { Video } from "@remotion/media";
import { staticFile } from "remotion";

import { cores, layout } from "./theme";
import type { Enquadramento } from "./tipos";

export const VideoRosto: React.FC<{
  arquivo: string;
  enquadramento: Enquadramento;
  fonte: { largura: number; altura: number };
}> = ({ arquivo, enquadramento, fonte }) => {
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
          backgroundColor: cores.navySoft,
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
  const alvoNaFaixa = layout.rosto - layout.video.topo;
  const limitar = (valor: number, minimo: number) =>
    Math.min(0, Math.max(minimo, valor));
  const topo = limitar(
    alvoNaFaixa - enquadramento.foco_rosto * altura,
    faixa.altura - altura,
  );
  const esquerda = limitar((faixa.largura - largura) / 2, faixa.largura - largura);

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
        }}
      />
    </div>
  );
};
