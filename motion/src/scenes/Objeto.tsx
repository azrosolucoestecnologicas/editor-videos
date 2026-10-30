/**
 * `objeto`: uma ilustração como metáfora, com o título que ela carrega.
 *
 * É a cena das imagens geradas — a casa, o selo, a balança, as alianças. O
 * que ela faz que nenhuma outra faz: mostrar a coisa de que a fala trata, em
 * vez de descrevê-la com palavras num card.
 *
 * A imagem não vem de código: é um arquivo que o Thiago gera e deixa na pasta
 * do job, e que o `exportar_props` publica. Por isso ela pode faltar — e,
 * faltando, a cena ainda tem que entregar o título em vez de abrir um buraco.
 */

import { Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

import { entrada, entradaSuave } from "../motion";
import { cores, objeto, tipografia } from "../theme";
import type { Cena } from "../tipos";
import { AreaCena, FraseComChave } from "./base";

export const Objeto: React.FC<{
  cena: Extract<Cena, { tipo: "objeto" }>;
  duracaoFrames: number;
}> = ({ cena, duracaoFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { imagem, titulo, chave } = cena.conteudo;

  return (
    <AreaCena duracaoFrames={duracaoFrames} alinhamento="centro">
      {imagem ? (
        <Img
          src={staticFile(imagem)}
          style={{
            height: objeto.altura,
            objectFit: "contain",
            // A sombra vem do próprio objeto, não de um card: ele pousa no
            // chão do mundo, não flutua numa caixa.
            filter: objeto.sombra,
            ...entrada(frame, fps, 0),
          }}
        />
      ) : null}

      <div
        style={{
          color: cores.tinta,
          ...tipografia.tituloCena,
          maxWidth: objeto.larguraTitulo,
          lineHeight: 1.15,
          ...entradaSuave(frame, fps, objeto.atrasoTitulo),
        }}
      >
        <FraseComChave
          frase={titulo}
          chave={chave}
          atrasoFrames={objeto.atrasoTitulo}
        />
      </div>
    </AreaCena>
  );
};
