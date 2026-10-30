#!/usr/bin/env python3
"""Editor de Reels: corta as pausas, planeja as cenas e renderiza no Remotion.

Uso rápido:
  python editar.py transcrever entrada/meu_video.mp4
  python editar.py cortar entrada/meu_video.mp4        # tira pausas -> entrada/meu_video_cortado.mp4
  python editar.py plano entrada/meu_video_cortado.mp4 # gera/atualiza o scene_plan.json
  python editar.py validar-plano planos/meu_video_cortado.scene_plan.json
  python editar.py reel entrada/meu_video.mp4          # tudo de uma vez
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from editor import (  # noqa: E402
    cortes, ffmpeg, plano as mod_plano, remotion as mod_remotion, rosto, transcricao,
)


def cmd_transcrever(args):
    ffmpeg.verificar()
    transcricao.transcrever(args.video, modelo=args.modelo, idioma=args.idioma)


def cmd_cortar(args):
    ffmpeg.verificar()
    muletas = None if args.muletas is None else [m.strip() for m in args.muletas.split(",") if m.strip()]
    cortes.cortar(args.video, pausa_max=args.pausa_max, margem=args.margem, muletas=muletas, modelo=args.modelo)


def _relatorio(achados):
    """Imprime os achados da validação e devolve quantos erros havia."""
    erros = [m for n, m in achados if n == "erro"]
    avisos = [m for n, m in achados if n == "aviso"]
    for m in erros:
        print(f"  ERRO   {m}")
    for m in avisos:
        print(f"  aviso  {m}")
    if not achados:
        print("  Plano válido: nenhum erro, nenhum aviso.")
    else:
        print(f"\n  {len(erros)} erro(s), {len(avisos)} aviso(s).")
    return len(erros)


def gerar_plano(video, assinatura="", refazer=False, refazer_cena=(),
                detectar_rosto=False, saida=None):
    """Gera ou atualiza o plano de um vídeo cortado.

    Devolve ``(plano, legendas, caminhos, achados_da_validacao)``. É o miolo
    tanto do subcomando `plano` quanto do `reel`.
    """
    # Aqui, e não só no `reel`: planejar desfoca o fundo e sonda as dimensões com
    # ffmpeg, então sem ele o erro saía como um FileNotFoundError cru lá no meio.
    ffmpeg.verificar()
    video = Path(video)
    arq_trans = transcricao.caminho_transcricao(video)
    if not arq_trans.exists():
        raise SystemExit(
            f"Transcrição não encontrada: {arq_trans}\n"
            f'Rode antes: python editar.py cortar "{video}"'
        )
    dados = transcricao.carregar(arq_trans)

    destino_plano, destino_legendas, destino_props = mod_plano.caminhos(video)
    if saida:
        destino_plano = Path(saida)

    anterior = None if refazer else mod_plano.carregar(destino_plano)
    novo = mod_plano.esqueleto(dados, video, assinatura=assinatura)
    mesclado = mod_plano.mesclar(anterior, novo, refazer=refazer_cena or ())
    final = mod_plano.resolver_gatilhos(mesclado, dados)

    # O enquadramento sobrevive ao recálculo (o `mesclar` o preserva); só é
    # refeito quando você pede, para a detecção não desfazer um ajuste à mão.
    nunca_detectado = final["enquadramento"].get("origem") == "padrao"
    if detectar_rosto or nunca_detectado:
        foco, topo_cabeca, deteccoes, quadros = rosto.detectar(video)
        if deteccoes >= rosto.MINIMO_DETECCOES:
            final["enquadramento"]["foco_rosto"] = foco
            final["enquadramento"]["topo_cabeca"] = topo_cabeca
            final["enquadramento"]["origem"] = "auto"
            print(f"Rosto detectado em {deteccoes}/{quadros} quadros: foco_rosto={foco}")
        else:
            print(
                f"Rosto detectado em só {deteccoes}/{quadros} quadros; "
                f'mantendo foco_rosto={final["enquadramento"]["foco_rosto"]} '
                "(ajuste à mão no plano se o enquadramento sair torto)."
            )
    legendas = mod_plano.legendas_do_plano(dados)

    mod_plano.salvar(final, destino_plano)
    mod_plano.salvar(legendas, destino_legendas)
    mod_plano.exportar_props(final, legendas, video, destino_props)

    preservadas = sum(1 for c in final["cenas"] if c.get("editado"))
    pendentes = [c["id"] for c in final["cenas"] if c.get("tipo") is None]
    print(f"Plano: {destino_plano}")
    print(f"Legendas: {destino_legendas} ({len(legendas)} bloco(s))")
    print(f"Props do Remotion: {destino_props}")
    print(
        f"{len(final['cenas'])} cena(s): {preservadas} preservada(s) da sua edição, "
        f"{len(pendentes)} ainda sem tipo."
    )

    achados = mod_plano.validar(final, dados, legendas)
    return final, legendas, (destino_plano, destino_legendas, destino_props), achados


def cmd_plano(args):
    _, _, _, achados = gerar_plano(
        args.video, assinatura=args.assinatura, refazer=args.refazer,
        refazer_cena=args.refazer_cena, detectar_rosto=args.detectar_rosto,
        saida=args.saida,
    )
    print("\nValidação:")
    _relatorio(achados)


def cmd_validar_plano(args):
    alvo = Path(args.plano)
    if alvo.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"}:
        alvo = mod_plano.caminhos(alvo)[0]
    dados_plano = mod_plano.carregar(alvo)
    if dados_plano is None:
        raise SystemExit(f"Plano não encontrado: {alvo}")

    video = RAIZ / dados_plano["video"]
    arq_trans = transcricao.caminho_transcricao(video)
    if not arq_trans.exists():
        raise SystemExit(
            f"Transcrição não encontrada: {arq_trans}\n"
            f'Rode antes: python editar.py cortar "{video}"'
        )
    dados = transcricao.carregar(arq_trans)
    _, arq_legendas, _props = mod_plano.caminhos(video)
    legendas = mod_plano.carregar(arq_legendas)

    print(f"{alvo} ({len(dados_plano.get('cenas') or [])} cena(s))")
    if _relatorio(mod_plano.validar(dados_plano, dados, legendas)):
        raise SystemExit(1)


def _video_cortado(video, pausa_max, margem, muletas, modelo):
    """Devolve o vídeo cortado, cortando agora se ainda não existir."""
    video = Path(video)
    if video.stem.endswith("_cortado"):
        return video
    cortado = video.with_name(video.stem + "_cortado.mp4")
    if cortado.exists():
        print(f"[1/4] Vídeo já cortado: {cortado}")
        return cortado
    print("[1/4] Transcrevendo e cortando pausas e muletas...")
    return cortes.cortar(video, pausa_max=pausa_max, margem=margem,
                         muletas=muletas, modelo=modelo)


def cmd_reel(args):
    """Vídeo bruto -> transcrição -> cortes -> scene_plan.json -> render."""
    ffmpeg.verificar()
    mod_remotion.verificar()

    muletas = None if args.muletas is None else [
        m.strip() for m in args.muletas.split(",") if m.strip()
    ]
    cortado = _video_cortado(args.video, args.pausa_max, args.margem, muletas, args.modelo)

    print("\n[2/4] Planejando as cenas...")
    plano, _legendas, caminhos, achados = gerar_plano(
        cortado, assinatura=args.assinatura, refazer=args.refazer,
        refazer_cena=args.refazer_cena, detectar_rosto=args.detectar_rosto,
    )
    _, _, arq_props = caminhos

    print("\n[3/4] Validando contra as skills...")
    if _relatorio(achados):
        pendentes = [c["id"] for c in plano["cenas"] if c.get("tipo") is None]
        if pendentes:
            print(
                f"\n{len(pendentes)} cena(s) sem tipo: {', '.join(pendentes)}.\n"
                "O conteúdo de cada cena é escrito por quem entende o que foi dito.\n"
                f"Abra {caminhos[0]} e preencha `tipo` e `conteudo`, ou peça ao\n"
                "Claude para preencher (a fala de cada cena está no campo `_fala`)."
            )
        raise SystemExit(1)

    destino = Path(args.saida) if args.saida else (
        RAIZ / "output" / f"{Path(cortado).stem.replace('_cortado', '')}_final.mp4"
    )

    if args.stills:
        frames = mod_remotion.frames_chave(plano)
        print(f"\n[4/4] Gerando stills dos frames {frames}...")
        pasta = RAIZ / "output" / "stills" / Path(cortado).stem
        gerados = mod_remotion.stills(arq_props, frames, pasta)
        print(f"\n{len(gerados)} still(s) em {pasta}")
        return

    print(f"\n[4/4] Renderizando {'a prévia' if args.previa else 'o vídeo final'}...")
    mod_remotion.renderizar(arq_props, destino, previa=args.previa,
                            concorrencia=args.concorrencia)
    print(f"\nPronto: {destino}")


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

    p = sub.add_parser("plano", help="gera/atualiza o scene_plan.json do vídeo cortado")
    p.add_argument("video", help="o vídeo JÁ CORTADO (entrada/..._cortado.mp4)")
    p.add_argument("--assinatura", default="", help="nome exibido no canto do painel")
    p.add_argument("--saida", help="caminho do scene_plan.json")
    p.add_argument("--refazer", action="store_true",
                   help="descarta as edições à mão e recalcula tudo")
    p.add_argument("--refazer-cena", action="append", metavar="ID",
                   help="devolve só esta cena ao planejador (pode repetir)")
    p.add_argument("--detectar-rosto", action="store_true",
                   help="redetecta o enquadramento do rosto, descartando o ajuste manual")
    p.set_defaults(func=cmd_plano)

    p = sub.add_parser("validar-plano", help="confere o plano contra as regras das skills")
    p.add_argument("plano", help="o scene_plan.json ou o vídeo cortado")
    p.set_defaults(func=cmd_validar_plano)

    p = sub.add_parser("reel", help="faz tudo: corta, planeja e renderiza no Remotion")
    p.add_argument("video", help="o vídeo bruto (entrada/...)")
    p.add_argument("--assinatura", default="", help="nome exibido no canto do painel")
    p.add_argument("--saida", help="caminho do mp4 final (padrão: output/<nome>_final.mp4)")
    p.add_argument("--stills", action="store_true",
                   help="em vez do vídeo, gera um PNG por cena para conferência")
    p.add_argument("--previa", action="store_true", help="metade da resolução, bem mais rápido")
    p.add_argument("--concorrencia", type=int, help="quantos frames em paralelo")
    p.add_argument("--refazer", action="store_true",
                   help="descarta as edições à mão do plano e recalcula tudo")
    p.add_argument("--refazer-cena", action="append", metavar="ID",
                   help="devolve só esta cena ao planejador (pode repetir)")
    p.add_argument("--detectar-rosto", action="store_true",
                   help="redetecta o enquadramento, descartando o ajuste manual")
    p.add_argument("--pausa-max", type=float, default=0.35,
                   help="pausas maiores que isso (s) são cortadas")
    p.add_argument("--margem", type=float, default=0.08,
                   help="respiro mantido antes/depois de cada fala (s)")
    p.add_argument("--muletas", help='lista separada por vírgula; "" para não remover nenhuma')
    p.add_argument("--modelo", default="small", help="modelo do Whisper")
    p.set_defaults(func=cmd_reel)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
