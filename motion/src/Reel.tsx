/**
 * Composição do reel: três faixas fixas, conforme a skill `reels-composicao`.
 *
 *   0 a  900  painel de animação (cenas do scene_plan.json)
 * 900 a 1040  divisória com a legenda
 * 1040 a 1920 o vídeo gravado, reenquadrado no rosto
 *
 * As cenas se sobrepõem de propósito: a atual sai enquanto a próxima entra.
 */

import { AbsoluteFill, Sequence } from "remotion";

import { Legendas } from "./Legendas";
import { ANTECIPACAO_FRAMES, duracoes } from "./motion";
import { CenaDoPlano } from "./scenes";
import { cores, grade, layout, tipografia } from "./theme";
import type { PropsReel } from "./tipos";
import { VideoRosto } from "./VideoRosto";

/** Grade sutil atrás das cenas: linhas navySoft a 30%, espaçamento 72 px. */
const Grade: React.FC = () => {
  const altura = layout.painel.altura;
  const colunas = Math.floor(1080 / grade.passo);
  const linhas = Math.floor(altura / grade.passo);

  return (
    <svg
      width={1080}
      height={altura}
      style={{ position: "absolute", inset: 0, opacity: grade.opacidade }}
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

/** Assinatura discreta, fixa no canto superior esquerdo do painel. */
const Assinatura: React.FC<{ texto: string }> = ({ texto }) => (
  <div
    style={{
      position: "absolute",
      left: layout.margem,
      // Na zona segura: nada importante acima de 120 px, onde fica a barra
      // do Instagram.
      top: layout.topoSeguro,
      color: cores.creme60,
      ...tipografia.assinatura,
    }}
  >
    {texto}
  </div>
);

export const Reel: React.FC<PropsReel> = ({ plano, legendas, video }) => {
  const { fps } = plano;

  return (
    <AbsoluteFill style={{ backgroundColor: cores.navy }}>
      {/* --- painel de animação --- */}
      <div
        style={{
          position: "absolute",
          top: layout.painel.topo,
          left: 0,
          width: 1080,
          height: layout.painel.altura,
          overflow: "hidden",
        }}
      >
        <Grade />
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
      </div>

      {/* --- vídeo --- */}
      <VideoRosto
        arquivo={video}
        enquadramento={plano.enquadramento}
        fonte={plano.fonte}
      />

      {/* --- legenda, por cima de tudo --- */}
      <Legendas blocos={legendas} />
    </AbsoluteFill>
  );
};
