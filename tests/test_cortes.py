"""`planejar` escolhe o que fica e `remapear` reescreve o relógio.

Se os dois discordarem, a transcrição aponta para um segundo que não é mais o
daquela fala — e toda cena do plano entra fora de hora, sem nada reclamar.
"""

import pytest

from editor import cortes


def p(palavra, inicio, fim):
    return {"palavra": palavra, "inicio": inicio, "fim": fim}


# ---------------------------------------------------------------- planejar

def test_fala_continua_vira_um_trecho_so():
    palavras = [p("uma", 1.0, 1.3), p("frase", 1.35, 1.8)]
    trechos, _ = cortes.planejar(palavras, duracao=5.0, pausa_max=0.35, margem=0.0)
    assert len(trechos) == 1


def test_pausa_longa_parte_em_dois():
    palavras = [p("antes", 1.0, 1.4), p("depois", 4.0, 4.5)]
    trechos, _ = cortes.planejar(palavras, duracao=6.0, pausa_max=0.35, margem=0.0)
    assert len(trechos) == 2


def test_muleta_e_removida_da_lista_de_palavras():
    palavras = [p("é", 1.0, 1.2), p("hum", 1.2, 1.5), p("assim", 1.5, 2.0)]
    _, mantidas = cortes.planejar(palavras, duracao=5.0, muletas=["hum"])
    assert [x["palavra"] for x in mantidas] == ["é", "assim"]


def test_lista_de_muletas_vazia_nao_remove_nada():
    palavras = [p("hum", 1.0, 1.4)]
    _, mantidas = cortes.planejar(palavras, duracao=3.0, muletas=[])
    assert len(mantidas) == 1


def test_trechos_saem_alinhados_ao_quadro():
    palavras = [p("fala", 1.017, 1.983)]
    trechos, _ = cortes.planejar(palavras, duracao=5.0, margem=0.0, fps=30)
    for inicio, fim in trechos:
        assert abs(inicio * 30 - round(inicio * 30)) < 1e-9
        assert abs(fim * 30 - round(fim * 30)) < 1e-9


def test_margem_nao_passa_dos_limites_do_video():
    palavras = [p("fala", 0.0, 5.0)]
    trechos, _ = cortes.planejar(palavras, duracao=5.0, margem=1.0)
    assert trechos[0][0] >= 0.0
    assert trechos[0][1] <= 5.0


# ---------------------------------------------------------------- remapear

TRECHOS = [(1.0, 2.0), (4.0, 5.5)]


@pytest.mark.parametrize("t, esperado", [
    (0.5, 0.0),    # antes de tudo: encosta no zero
    (1.0, 0.0),    # começo do primeiro trecho
    (1.5, 0.5),    # meio do primeiro
    (2.0, 1.0),    # fim do primeiro
    (3.0, 1.0),    # dentro do buraco: colapsa no fim do anterior
    (4.0, 1.0),    # começo do segundo, colado no fim do primeiro
    (5.5, 2.5),    # fim de tudo = soma dos trechos
])
def test_remapear_leva_o_tempo_para_o_video_cortado(t, esperado):
    assert cortes.remapear(t, TRECHOS) == pytest.approx(esperado)


def test_remapear_e_monotonico():
    anterior = -1.0
    for i in range(0, 700):
        agora = cortes.remapear(i / 100, TRECHOS)
        assert agora >= anterior
        anterior = agora


def test_o_fim_bate_com_a_soma_dos_trechos():
    soma = sum(b - a for a, b in TRECHOS)
    assert cortes.remapear(TRECHOS[-1][1], TRECHOS) == pytest.approx(soma)


def test_planejar_e_remapear_concordam():
    """O fim da última palavra mantida tem que cair dentro do vídeo cortado."""
    palavras = [p("um", 1.0, 1.4), p("dois", 5.0, 5.6), p("tres", 5.65, 6.2)]
    trechos, mantidas = cortes.planejar(palavras, duracao=8.0, margem=0.0)
    total = sum(b - a for a, b in trechos)

    fim = cortes.remapear(mantidas[-1]["fim"], trechos)
    assert 0 <= fim <= total + 1e-9
