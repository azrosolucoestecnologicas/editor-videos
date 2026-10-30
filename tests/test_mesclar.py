"""`mesclar` é a promessa de que o seu trabalho à mão sobrevive ao recálculo.

Toda vez que você roda `editar.py plano` de novo, o planejador propõe cenas do
zero e o `mesclar` decide, cena a cena, se fica a sua ou a dele. Errar aqui não
dá erro nenhum: o vídeo simplesmente sai com outro conteúdo.
"""

from editor import plano


def cena(ident, gatilho, ocorrencia=1, **campos):
    """Uma cena como o planejador a propõe, com o hash já coerente.

    Hash coerente = cena intocada. Para simular uma edição sua, mude um campo
    depois de criar, sem recalcular o hash — é exatamente o que acontece quando
    você edita o JSON à mão.
    """
    base = {
        "id": ident,
        "inicio": 0.0,
        "fim": 4.0,
        "palavra_gatilho": gatilho,
        "ocorrencia": ocorrencia,
        "tipo": None,
        "conteudo": None,
        "editado": False,
        "_fala": f"fala de {gatilho}",
    }
    base.update(campos)
    base["_hash"] = plano._hash(base)
    return base


def pl(*cenas):
    return {"versao": 1, "video": "v.mp4", "duracao": 60.0, "cenas": list(cenas)}


def por_id(resultado):
    return {c["id"]: c for c in resultado["cenas"]}


# ------------------------------------------------------------------ o básico

def test_sem_plano_anterior_fica_a_proposta():
    novo = pl(cena("c01", "contrato"))
    assert plano.mesclar(None, novo) is novo


def test_cena_intocada_e_substituida_pela_proposta():
    antigo = pl(cena("c01", "contrato"))
    novo = pl(cena("c01", "contrato", tipo="lista", conteudo={"itens": ["a"]}))
    resultado = plano.mesclar(antigo, novo)
    assert resultado["cenas"][0]["tipo"] == "lista"


def test_cena_editada_a_mao_sobrevive():
    escrita = cena("c01", "contrato")
    escrita["tipo"] = "card_conceito"          # você editou e não recalculou o hash
    escrita["conteudo"] = {"termo": "Contrato"}

    novo = pl(cena("c01", "contrato", tipo="lista"))
    mantida = plano.mesclar(pl(escrita), novo)["cenas"][0]

    assert mantida["tipo"] == "card_conceito"
    assert mantida["editado"] is True
    assert mantida["_hash"] == plano._hash(mantida), "o hash tem que voltar coerente"


def test_fala_derivada_e_sempre_a_nova():
    escrita = cena("c01", "contrato")
    escrita["tipo"] = "sintese"
    novo = pl(cena("c01", "contrato"))
    novo["cenas"][0]["_fala"] = "a transcrição mudou"

    mantida = plano.mesclar(pl(escrita), novo)["cenas"][0]
    assert mantida["_fala"] == "a transcrição mudou"


def test_refazer_cena_devolve_ao_planejador():
    escrita = cena("c01", "contrato")
    escrita["tipo"] = "card_conceito"
    novo = pl(cena("c01", "contrato", tipo="lista"))

    resultado = plano.mesclar(pl(escrita), novo, refazer=["c01"])
    assert resultado["cenas"][0]["tipo"] == "lista"


def test_campos_de_topo_editaveis_sobrevivem():
    antigo = pl(cena("c01", "contrato"))
    antigo["assinatura"] = "Thiago Azeredo"
    antigo["enquadramento"] = {"foco_rosto": 0.41, "origem": "manual"}

    resultado = plano.mesclar(antigo, pl(cena("c01", "contrato")))
    assert resultado["assinatura"] == "Thiago Azeredo"
    assert resultado["enquadramento"]["foco_rosto"] == 0.41


# ---------------------------------------------- zoom e brilho são autorais
# Os dois ficavam de fora do CAMPOS_DO_HASH: ligar um deles à mão não marcava
# a cena como editada, e a rodada seguinte a trocava pela proposta automática.

def test_zoom_ligado_a_mao_sobrevive():
    escrita = cena("c01", "contrato", tipo="sintese")
    escrita["zoom"] = True

    mantida = plano.mesclar(pl(escrita), pl(cena("c01", "contrato", tipo="sintese")))["cenas"][0]
    assert mantida["zoom"] is True


def test_brilho_ligado_a_mao_sobrevive():
    escrita = cena("c01", "contrato", tipo="sintese")
    escrita["brilho"] = True

    mantida = plano.mesclar(pl(escrita), pl(cena("c01", "contrato", tipo="sintese")))["cenas"][0]
    assert mantida["brilho"] is True


def test_zoom_que_o_planejador_distribuiu_nao_conta_como_edicao():
    """O `_espacar_zooms` roda antes do hash, então o zoom automático é a linha
    de base — e uma cena só com ele tem que aceitar a proposta nova."""
    automatica = cena("c01", "contrato", zoom=True)
    novo = pl(cena("c01", "contrato", tipo="lista", zoom=True))

    assert plano.mesclar(pl(automatica), novo)["cenas"][0]["tipo"] == "lista"


# ------------------------------------- o conteúdo segue a fala, não a posição
# Casar por id (`c05`) fazia o texto escrito para uma fala reaparecer colado a
# outra assim que uma correção no glossário deslocava as fronteiras.

def test_conteudo_segue_a_fala_quando_uma_cena_e_inserida_antes():
    escrita = cena("c02", "prazo", tipo="numero")
    escrita["conteudo"] = {"valor": "15 dias"}

    antigo = pl(cena("c01", "contrato"), escrita)
    # A transcrição mudou e nasceu uma cena nova no começo: "prazo" virou c03.
    novo = pl(cena("c01", "abertura"), cena("c02", "contrato"), cena("c03", "prazo"))

    resultado = por_id(plano.mesclar(antigo, novo))
    assert resultado["c03"]["conteudo"] == {"valor": "15 dias"}, "o texto tem que seguir 'prazo'"
    assert resultado["c02"]["conteudo"] is None, "e não encostar na fala vizinha"


def test_ocorrencia_distingue_duas_falas_da_mesma_palavra():
    primeira = cena("c01", "prazo", ocorrencia=1, tipo="numero")
    primeira["conteudo"] = {"valor": "primeiro"}
    segunda = cena("c02", "prazo", ocorrencia=2, tipo="numero")
    segunda["conteudo"] = {"valor": "segundo"}

    novo = pl(cena("c01", "prazo", ocorrencia=1), cena("c02", "prazo", ocorrencia=2))
    resultado = por_id(plano.mesclar(pl(primeira, segunda), novo))

    assert resultado["c01"]["conteudo"] == {"valor": "primeiro"}
    assert resultado["c02"]["conteudo"] == {"valor": "segundo"}


def test_gatilho_que_sumiu_reaproveita_pela_posicao_mas_marca_a_cena():
    escrita = cena("c01", "contrato", tipo="sintese")
    escrita["conteudo"] = {"frase": "escrita à mão"}
    # "contrato" não existe mais na transcrição corrigida.
    novo = pl(cena("c01", "acordo"))

    mantida = plano.mesclar(pl(escrita), novo)["cenas"][0]
    assert mantida["conteudo"] == {"frase": "escrita à mão"}, "não joga fora o seu texto"
    assert mantida["_gatilho_mudou"] is True, "mas pede conferida"


def test_marca_de_gatilho_some_quando_a_fala_volta_a_casar():
    escrita = cena("c01", "contrato", tipo="sintese")
    escrita["_gatilho_mudou"] = True

    mantida = plano.mesclar(pl(escrita), pl(cena("c01", "contrato")))["cenas"][0]
    assert "_gatilho_mudou" not in mantida
