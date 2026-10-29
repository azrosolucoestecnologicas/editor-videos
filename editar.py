#!/usr/bin/env python3
"""Editor de Reels: transcreve, legenda, divide a tela e anima conforme o roteiro.

Uso rápido:
  python editar.py transcrever entrada/meu_video.mp4
  python editar.py cortar entrada/meu_video.mp4        # tira pausas -> entrada/meu_video_cortado.mp4
  python editar.py novo entrada/meu_video.mp4          # cria roteiros/meu_video.yaml
  python editar.py eventos roteiros/meu_video.yaml     # confere os tempos dos gatilhos
  python editar.py quadro roteiros/meu_video.yaml 12.5 # PNG de um instante
  python editar.py renderizar roteiros/meu_video.yaml  # gera o vídeo final
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from editor import cortes, render, transcricao  # noqa: E402
from editor.animacoes import REGISTRO  # noqa: E402
from editor.roteiro import Roteiro, ler_tempo  # noqa: E402

MODELO_ROTEIRO = """\
# Roteiro de edição de "{nome}"
# Gatilhos: use `quando: "frase falada"` (o tempo vem da transcrição) ou `em: "0:12.5"`.
# Fim do evento: `duracao: 4`, `ate: "0:20"` ou `ate_quando: "frase"`.
# Animações disponíveis: {animacoes}
# Veja exemplos completos em roteiros/exemplo.yaml

video: {video}
saida: saida/{nome}_editado.mp4

legendas:
  ativas: true
  estilo: destaque        # destaque | caixa | simples
  palavras_por_bloco: 3

divisao:
  proporcao: 0.5          # metade de cima para a animação
  foco_rosto: 0.36        # ajuste se o seu rosto ficar cortado na tela dividida

eventos: []
#  - quando: "primeira frase de impacto"
#    duracao: 3
#    animacao:
#      tipo: texto
#      texto: "FRASE DE IMPACTO"

# ---------------------------------------------------------------
# Transcrição (referência para escolher os gatilhos):
{transcricao}
"""


def cmd_transcrever(args):
    render.verificar_ffmpeg()
    transcricao.transcrever(args.video, modelo=args.modelo, idioma=args.idioma)


def cmd_cortar(args):
    render.verificar_ffmpeg()
    muletas = None if args.muletas is None else [m.strip() for m in args.muletas.split(",") if m.strip()]
    cortes.cortar(args.video, pausa_max=args.pausa_max, margem=args.margem, muletas=muletas, modelo=args.modelo)


def cmd_novo(args):
    video = Path(args.video)
    arq_trans = transcricao.caminho_transcricao(video)
    if not arq_trans.exists():
        transcricao.transcrever(video, modelo=args.modelo)
    dados = transcricao.carregar(arq_trans)
    linhas = "\n".join(f"#  [{transcricao.formatar_tempo(s['inicio'])}] {s['texto']}" for s in dados["segmentos"])
    destino = RAIZ / "roteiros" / f"{video.stem}.yaml"
    if destino.exists() and not args.sobrescrever:
        raise SystemExit(f"{destino} já existe (use --sobrescrever para recriar).")
    try:
        caminho_video = video.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        caminho_video = video.resolve().as_posix()
    destino.write_text(MODELO_ROTEIRO.format(nome=video.stem, video=caminho_video, transcricao=linhas,
                                             animacoes=", ".join(sorted(REGISTRO))), encoding="utf-8")
    print(f"Roteiro criado: {destino}")


def cmd_eventos(args):
    roteiro = Roteiro(args.roteiro)
    eventos = roteiro.eventos()
    for e in eventos:
        print(render.descrever(e))
        for item in (e.animacao or {}).get("itens", []) or []:
            if isinstance(item, dict) and item.get("_t") is not None:
                print(f"      item \"{item.get('texto')}\" aparece em {e.inicio + item['_t']:.2f}s")
    if not eventos:
        print("Nenhum evento definido.")


def cmd_quadro(args):
    roteiro = Roteiro(args.roteiro)
    tempo = ler_tempo(args.tempo)
    destino = Path(args.saida or f"saida/quadro_{tempo:06.2f}.png")
    destino.parent.mkdir(parents=True, exist_ok=True)
    render.exportar_quadro(roteiro, tempo, destino, previa=args.previa)


def cmd_renderizar(args):
    roteiro = Roteiro(args.roteiro)
    render.renderizar(roteiro, previa=args.previa, inicio=ler_tempo(args.inicio), fim=ler_tempo(args.fim),
                      saida=Path(args.saida) if args.saida else None)


def main():
    ap = argparse.ArgumentParser(description="Editor automático de Reels")
    sub = ap.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("transcrever", help="gera a transcrição com tempo de cada palavra")
    p.add_argument("video")
    p.add_argument("--modelo", default="small", help="tiny, base, small, medium, large-v3 (maior = mais preciso)")
    p.add_argument("--idioma", default="pt")
    p.set_defaults(func=cmd_transcrever)

    p = sub.add_parser("cortar", help="remove pausas longas e muletas (hã, hum) usando a transcrição")
    p.add_argument("video")
    p.add_argument("--pausa-max", type=float, default=0.35, help="pausas maiores que isso (s) são cortadas")
    p.add_argument("--margem", type=float, default=0.08, help="respiro mantido antes/depois de cada fala (s)")
    p.add_argument("--muletas", help='lista separada por vírgula; "" para não remover nenhuma')
    p.add_argument("--modelo", default="small")
    p.set_defaults(func=cmd_cortar)

    p = sub.add_parser("novo", help="cria um roteiro YAML a partir do vídeo")
    p.add_argument("video")
    p.add_argument("--modelo", default="small")
    p.add_argument("--sobrescrever", action="store_true")
    p.set_defaults(func=cmd_novo)

    p = sub.add_parser("eventos", help="mostra em que segundo cada gatilho acontece")
    p.add_argument("roteiro")
    p.set_defaults(func=cmd_eventos)

    p = sub.add_parser("quadro", help="salva um PNG de um instante, para conferir o visual")
    p.add_argument("roteiro")
    p.add_argument("tempo", help="ex.: 12.5 ou 0:12.5")
    p.add_argument("--saida")
    p.add_argument("--previa", action="store_true")
    p.set_defaults(func=cmd_quadro)

    p = sub.add_parser("renderizar", help="gera o vídeo editado")
    p.add_argument("roteiro")
    p.add_argument("--previa", action="store_true", help="metade da resolução, bem mais rápido")
    p.add_argument("--inicio", help="renderizar só a partir deste tempo")
    p.add_argument("--fim", help="renderizar só até este tempo")
    p.add_argument("--saida")
    p.set_defaults(func=cmd_renderizar)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
