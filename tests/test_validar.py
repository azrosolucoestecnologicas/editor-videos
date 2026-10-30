"""As cotas de reel: regras que valem para o conjunto, não para a cena.

Uma cena isolada pode estar perfeita e o reel ainda estar errado — b-roll
demais, dois seguidos, brilho em todo card. Como nenhuma cena sozinha viola
nada, é o tipo de regra que passa batida sem um teste.
"""

from editor import plano


def transcricao():
    palavras = [
        {"palavra": f"p{i}", "inicio": i * 2.0, "fim": i * 2.0 + 1.5}
        for i in range(12)
    ]
    return {"idioma": "pt", "duracao": 24.0, "palavras": palavras,
            "segmentos": [{"inicio": 0.0, "fim": 24.0, "texto": "fala"}]}


def cena(ident, inicio, fim, tipo, conteudo):
    return {
        "id": ident, "inicio": inicio, "fim": fim, "tipo": tipo,
        "conteudo": conteudo, "palavra_gatilho": None, "ocorrencia": 1,
    }


def apoio(ident, inicio, fim=None):
    return cena(ident, inicio, fim if fim is not None else inicio + 3.0,
                "cena_apoio", {"clipe": "b.mp4", "rotulo": "no escritório"})


def sintese(ident, inicio, fim):
    return cena(ident, inicio, fim, "sintese", {"frase": "o fim"})


def montar(*cenas):
    return {"versao": 1, "video": "v.mp4", "duracao": 24.0, "fps": 30,
            "mundo": "palco", "cenas": list(cenas)}


def erros(achados):
    return [m for nivel, m in achados if nivel == "erro"]


def test_dois_b_rolls_passam():
    p = montar(apoio("c01", 0.0), sintese("c02", 3.0, 7.0),
               apoio("c03", 7.0), sintese("c04", 10.0, 24.0))
    assert not [m for m in erros(plano.validar(p, transcricao())) if "b-roll" in m]


def test_tres_b_rolls_estouram_a_cota():
    p = montar(apoio("c01", 0.0), sintese("c02", 3.0, 6.0),
               apoio("c03", 6.0), sintese("c04", 9.0, 12.0),
               apoio("c05", 12.0), sintese("c06", 15.0, 24.0))
    achados = erros(plano.validar(p, transcricao()))
    assert any("3 cenas de b-roll" in m for m in achados)


def test_dois_b_rolls_seguidos_sao_erro():
    p = montar(apoio("c01", 0.0), apoio("c02", 3.0), sintese("c03", 6.0, 24.0))
    achados = erros(plano.validar(p, transcricao()))
    assert any("logo depois de b-roll" in m for m in achados)
    assert any("c02" in m for m in achados)


def test_b_roll_longo_demais_vira_aviso():
    p = montar(apoio("c01", 0.0, 6.5), sintese("c02", 6.5, 24.0))
    avisos = [m for nivel, m in plano.validar(p, transcricao()) if nivel == "aviso"]
    assert any("b-roll de 6.50s" in m for m in avisos)


def test_b_roll_na_janela_dele_nao_reclama():
    """2 a 4 s é a janela do b-roll — e 3 s reclamaria se ele usasse a janela
    da cena comum, que começa em 3 s."""
    p = montar(apoio("c01", 0.0, 2.5), sintese("c02", 2.5, 24.0))
    avisos = [m for nivel, m in plano.validar(p, transcricao()) if nivel == "aviso"]
    assert not [m for m in avisos if "b-roll" in m]


def test_mundo_inexistente_e_erro():
    p = montar(sintese("c01", 0.0, 24.0))
    p["mundo"] = "neon"
    assert any("neon" in m for m in erros(plano.validar(p, transcricao())))


def test_clipe_sem_arquivo_e_erro():
    sem = cena("c01", 0.0, 3.0, "cena_apoio", {"clipe": "", "rotulo": "x"})
    assert plano.CATALOGO["cena_apoio"]["verificar"](sem["conteudo"])


def test_rotulo_longo_demais_e_erro():
    longo = {"clipe": "b.mp4", "rotulo": "um rótulo bem maior do que cabe aqui"}
    assert plano.CATALOGO["cena_apoio"]["verificar"](longo)


def test_rotulo_e_opcional():
    assert not plano.CATALOGO["cena_apoio"]["verificar"]({"clipe": "b.mp4"})
