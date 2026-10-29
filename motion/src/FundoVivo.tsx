/**
 * O fundo da zona de cenas é o próprio vídeo, ampliado, desfocado e escurecido.
 *
 * É o que resolve os três problemas da v1 de uma vez: acaba a emenda reta entre
 * painel e vídeo, o fundo ganha profundidade sem nenhum asset novo, e a luz do
 * palco — que muda de cor ao longo da gravação — vaza sozinha para trás dos
 * cards. É por isso que os cards passam a parecer estar no ambiente.
 *
 * Custo: um segundo decode do mesmo arquivo. É o preço do efeito; não há como
 * desfocar "o que está atrás" de um elemento com outra transformação.
 */

import { Video } from "@remotion/media";
import { AbsoluteFill, staticFile } from "remotion";

import { cores, grade, layout } from "./theme";

const Grade: React.FC = () => {
  const altura = layout.veu.altura;
  const colunas = Math.floor(1080 / grade.passo);
  const linhas = Math.floor(altura / grade.passo);

  return (
    <svg
      width={1080}
      height={altura}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        opacity: 0.2,
        // A grade também some antes de encostar no vídeo nítido.
        maskImage: `linear-gradient(to bottom, black ${altura - 260}px, transparent ${altura}px)`,
        WebkitMaskImage: `linear-gradient(to bottom, black ${altura - 260}px, transparent ${altura}px)`,
      }}
    >
      {Array.from({ length: colunas + 1 }, (_, i) => (
        <line
          key={`v${i}`}
          x1={i * grade.passo}
          y1={0}
          x2={i * grade.passo}
          y2={altura}
          stroke={grade.cor}
          strokeWidth={1}
        />
      ))}
      {Array.from({ length: linhas + 1 }, (_, i) => (
        <line
          key={`h${i}`}
          x1={0}
          y1={i * grade.passo}
          x2={1080}
          y2={i * grade.passo}
          stroke={grade.cor}
          strokeWidth={1}
        />
      ))}
    </svg>
  );
};

export const FundoVivo: React.FC<{ arquivo: string }> = ({ arquivo }) => {
  const { escala, desfoque, brilho } = layout.fundoVivo;
  const largura = 1080 * escala;
  const altura = 1920 * escala;

  return (
    <AbsoluteFill style={{ backgroundColor: cores.navy, overflow: "hidden" }}>
      {arquivo ? (
        <Video
          src={staticFile(arquivo)}
          muted
          style={{
            position: "absolute",
            // Centralizado e maior que a tela: o desfoque precisa de material
            // sobrando nas bordas, senão aparece a franja do blur.
            left: (1080 - largura) / 2,
            top: (1920 - altura) / 2,
            width: largura,
            height: altura,
            filter: `blur(${desfoque}px) brightness(${brilho})`,
          }}
        />
      ) : null}

      {/* Véu: dá contraste ao texto sem matar a cor que veio do cenário.
          Ele DISSOLVE no fim em vez de terminar reto — um retângulo com borda
          seca aqui recria exatamente a emenda que a v2 veio eliminar. */}
      <div
        style={{
          position: "absolute",
          top: layout.veu.topo,
          left: 0,
          width: 1080,
          height: layout.veu.altura + layout.video.degrade,
          background: `linear-gradient(to bottom, ${cores.veu} 0px, ${cores.veu} ${
            layout.veu.altura - layout.video.degrade
          }px, transparent ${layout.veu.altura + layout.video.degrade}px)`,
        }}
      />
      <Grade />
    </AbsoluteFill>
  );
};
