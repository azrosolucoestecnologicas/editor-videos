"""O glossário corrige a GRAFIA, nunca o conteúdo nem o tempo.

A invariante que importa: o que ele devolve ainda casa, palavra por palavra,
com o áudio. Se ele mexesse num tempo, a legenda descolaria da fala e a cena
entraria no segundo errado.
"""

from editor.glossario import Glossario


def p(palavra, inicio, fim):
    return {"palavra": palavra, "inicio": inicio, "fim": fim}


def test_corrige_a_grafia_de_uma_palavra():
    g = Glossario({"palavras": {"rag": "RAG"}})
    assert g.aplicar([p("rag", 1.0, 1.4)])[0]["palavra"] == "RAG"


def test_preserva_a_pontuacao_grudada():
    g = Glossario({"palavras": {"rag": "RAG"}})
    assert g.aplicar([p("rag.", 1.0, 1.4)])[0]["palavra"] == "RAG."


def test_casa_sem_acento_e_sem_caixa():
    g = Glossario({"palavras": {"sumula": "Súmula"}})
    assert g.aplicar([p("SÚMULA", 0.0, 0.5)])[0]["palavra"] == "Súmula"


def test_expressao_vira_uma_entrada_do_inicio_ao_fim():
    g = Glossario({"expressoes": [{"de": "sumula 331", "para": "Súmula 331"}]})
    saida = g.aplicar([p("súmula", 1.0, 1.5), p("331", 1.5, 2.0)])

    assert len(saida) == 1
    assert saida[0] == {"palavra": "Súmula 331", "inicio": 1.0, "fim": 2.0}


def test_expressao_mais_longa_ganha_da_mais_curta():
    g = Glossario({
        "expressoes": [
            {"de": "sumula", "para": "Súmula"},
            {"de": "sumula 331", "para": "Súmula 331"},
        ],
    })
    saida = g.aplicar([p("sumula", 1.0, 1.5), p("331", 1.5, 2.0)])
    assert saida[0]["palavra"] == "Súmula 331"


def test_muleta_some():
    g = Glossario({"muletas": [{"palavra": "tipo"}]})
    saida = g.aplicar([p("é", 0.0, 0.2), p("tipo", 0.2, 0.5), p("assim", 0.5, 0.9)])
    assert [x["palavra"] for x in saida] == ["é", "assim"]


def test_muleta_fica_quando_tem_uso_legitimo():
    """"tipo de contrato" é uso legítimo; "é tipo assim" é muleta."""
    g = Glossario({"muletas": [{"palavra": "tipo", "nao_remover_antes_de": ["de"]}]})
    saida = g.aplicar([p("tipo", 0.0, 0.3), p("de", 0.3, 0.5), p("contrato", 0.5, 1.0)])
    assert [x["palavra"] for x in saida] == ["tipo", "de", "contrato"]


def test_os_tempos_nunca_mudam():
    g = Glossario({"palavras": {"rag": "RAG"}, "muletas": [{"palavra": "hum"}]})
    entrada = [p("hum", 0.0, 0.2), p("rag", 0.2, 0.6), p("funciona", 0.6, 1.2)]
    saida = g.aplicar(entrada)

    assert [(x["inicio"], x["fim"]) for x in saida] == [(0.2, 0.6), (0.6, 1.2)]


def test_glossario_vazio_devolve_tudo_igual():
    g = Glossario()
    entrada = [p("uma", 0.0, 0.3), p("frase", 0.3, 0.8)]
    assert g.aplicar(entrada) == entrada
    assert g.vazio
