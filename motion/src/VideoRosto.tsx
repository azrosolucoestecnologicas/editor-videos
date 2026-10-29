/**
 * O vídeo gravado, na faixa de baixo (1040 a 1920 px).
 *
 * Recorte em cover centralizado no rosto: a skill `reels-movimento` pede os
 * olhos no terço superior da metade de baixo, então o centro do rosto é
 * levado para 1/3 da altura da faixa. `foco_rosto` vem da detecção
 * automática e pode ser corrigido à mão no `scene_plan.json`.
 */

import { Video } from "@remotion/media";
import { staticFile } from "remotion";

import { cores, layout } from "./theme";
import type { Enquadramento } from "./tipos";

/** Onde o rosto deve ficar dentro da faixa: um terço a partir do topo. */
const TERCO = 1 / 3;

export const VideoRosto: React.FC<{
  arquivo: string;
  enquadramento: Enquadramento;
  fonte: { largura: number; altura: number };
}> = ({ arquivo, enquadramento, fonte }) => {
  const faixa = { largura: 1080, altura: layout.video.altura };

  // Sem vídeo (os defaultProps do Studio), a faixa fica como um bloco vazio
  // em vez de quebrar o `staticFile()`.
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

  // Leva o rosto para o terço superior da faixa, sem deixar borda vazia.
  const limitar = (valor: number, minimo: number) =>
    Math.min(0, Math.max(minimo, valor));
  const topo = limitar(
    faixa.altura * TERCO - enquadramento.foco_rosto * altura,
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
