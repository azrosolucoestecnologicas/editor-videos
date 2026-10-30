/**
 * Despacho do catálogo fechado de cenas.
 *
 * Tipo novo só existe depois de entrar na tabela da skill
 * `reels-composicao` e no `CATALOGO` de `editor/plano.py`. O `switch`
 * exaustivo faz o TypeScript reclamar se um tipo for esquecido aqui.
 */

import type { Cena } from "../tipos";
import { CardConceito } from "./CardConceito";
import { CitacaoLegal } from "./CitacaoLegal";
import { Documento } from "./Documento";
import { Comparacao } from "./Comparacao";
import { Fluxo } from "./Fluxo";
import { IconeDestaque } from "./IconeDestaque";
import { Lista } from "./Lista";
import { Numero } from "./Numero";
import { Objeto } from "./Objeto";
import { Sintese } from "./Sintese";

export const CenaDoPlano: React.FC<{ cena: Cena; duracaoFrames: number }> = ({
  cena,
  duracaoFrames,
}) => {
  switch (cena.tipo) {
    case "card_conceito":
      return <CardConceito cena={cena} duracaoFrames={duracaoFrames} />;
    case "lista":
      return <Lista cena={cena} duracaoFrames={duracaoFrames} />;
    case "comparacao":
      return <Comparacao cena={cena} duracaoFrames={duracaoFrames} />;
    case "fluxo":
      return <Fluxo cena={cena} duracaoFrames={duracaoFrames} />;
    case "numero":
      return <Numero cena={cena} duracaoFrames={duracaoFrames} />;
    case "citacao_legal":
      return <CitacaoLegal cena={cena} duracaoFrames={duracaoFrames} />;
    case "icone_destaque":
      return <IconeDestaque cena={cena} duracaoFrames={duracaoFrames} />;
    case "documento":
      return <Documento cena={cena} duracaoFrames={duracaoFrames} />;
    case "objeto":
      return <Objeto cena={cena} duracaoFrames={duracaoFrames} />;
    case "sintese":
      return <Sintese cena={cena} duracaoFrames={duracaoFrames} />;
    default: {
      const naoTratado: never = cena;
      return naoTratado;
    }
  }
};
