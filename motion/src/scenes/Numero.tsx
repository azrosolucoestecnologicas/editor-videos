/**
 * `numero`: uma estatística + rótulo de até 6 palavras.
 *
 * O contador termina exatamente no frame em que o número é falado
 * (skill `reels-ritmo`). Valor que não é um inteiro puro — "R$ 10.000",
 * "11/11" — aparece estático, porque contar até ele não faria sentido.
 */

import { useCurrentFrame, useVideoConfig } from "remotion";

import { contador, duracoes, entrada } from "../motion";
import { cores, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, atrasoDe } from "./base";

export const Numero: React.FC<{
  cena: Extract<Cena, { tipo: "numero" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const { valor, rotulo } = cena.conteudo;
  const inteiro = /^\d+$/.test(valor);
  // Sem palavra-gatilho própria, a contagem termina logo após a entrada.
  const fimContagem = Math.max(
    duracoes.contador,
    atrasoDe(cena.conteudo._em, cena.inicio, fps),
  );

  const exibido = inteiro
    ? String(Math.round(contador(frame, fimContagem, Number(valor))))
    : valor;

  return (
    <AreaCena duracaoFrames={duracaoFrames} alinhamento="centro">
      <div
        style={{
          color: cores.cobre,
          ...tipografia.numero,
          fontVariantNumeric: "tabular-nums",
          ...entrada(frame, fps, 0),
        }}
      >
        {exibido}
      </div>
      {/* Sem régua aqui: o número já é o elemento cobre da cena. */}
      <div
        style={{
          color: cores.creme,
          ...tipografia.corpo,
          maxWidth: 760,
          ...entrada(frame, fps, 6),
        }}
      >
        {rotulo}
      </div>
    </AreaCena>
  );
};
