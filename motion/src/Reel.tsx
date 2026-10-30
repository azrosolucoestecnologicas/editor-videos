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

import { Info } from "lucide-react";
import { AbsoluteFill, Sequence } from "remotion";

import { FundoVivo } from "./FundoVivo";
import { Legendas } from "./Legendas";
import { ANTECIPACAO_FRAMES, duracoes } from "./motion";
import { CenaDoPlano } from "./scenes";
import {
  aviso,
  cores,
  layout,
  raios,
  tipografia,
  variaveisDoMundo,
} from "./theme";
import type { PropsReel } from "./tipos";
import { VideoRosto } from "./VideoRosto";

/**
 * Aviso fixo no topo, para o reel inteiro.
 *
 * Não é cena e não entra nem sai: fica os 100% do tempo, porque um aviso que
 * aparece só num trecho não avisa quem assistiu o resto. É o que separa
 * informar de parecer dar consultoria, então ele vem antes do conteúdo na
 * ordem de leitura e fica acima de tudo na pilha.
 */
const Aviso: React.FC<{ texto: string }> = ({ texto }) => (
  <div
    style={{
      position: "absolute",
      top: layout.topoSeguro,
      left: 0,
      width: "100%",
      display: "flex",
      justifyContent: "center",
      zIndex: 10,
    }}
  >
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: aviso.espacoIcone,
        maxWidth: aviso.larguraMaxima,
        padding: aviso.padding,
        borderRadius: raios.pilula,
        backgroundColor: cores.superficie,
        color: cores.tintaSuperficie,
        ...tipografia.aviso,
      }}
    >
      <Info size={aviso.tamanhoIcone} strokeWidth={2.2} aria-hidden />
      <span>{texto}</span>
    </div>
  </div>
);

/** Assinatura discreta, na zona segura do topo. */
const Assinatura: React.FC<{ texto: string; desce: number }> = ({
  texto,
  desce,
}) => (
  <div
    style={{
      position: "absolute",
      left: layout.margem,
      top: layout.topoSeguro + desce,
      color: cores.tintaFraca,
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
    // As variaveis do mundo nascem aqui, na raiz: todo `cores.*` abaixo é um
    // `var()` que resolve contra elas. Trocar de mundo não toca em cena alguma.
    <AbsoluteFill
      style={{ ...variaveisDoMundo(plano.mundo), backgroundColor: cores.chao }}
    >
      <FundoVivo arquivo={videoFundo} />

      <VideoRosto
        arquivo={video}
        enquadramento={plano.enquadramento}
        fonte={plano.fonte}
        zooms={plano.cenas
          .filter((c) => c.zoom)
          .map((c) => ({ inicio: c.inicio, fim: c.fim }))}
      />

      {plano.aviso ? <Aviso texto={plano.aviso} /> : null}

      {plano.assinatura ? (
        <Assinatura
          texto={plano.assinatura}
          desce={plano.aviso ? aviso.alturaOcupada : 0}
        />
      ) : null}

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
            durationInFrames={duracaoCena + duracoes.caudaCena}
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
