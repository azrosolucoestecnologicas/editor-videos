"""De onde sai a duração do plano.

Ela define o `fim` da última cena E o tamanho da composição Remotion. Saindo
da transcrição, era a soma dos trechos mantidos no corte; o mp4 sai de
`select` + `setpts=N/30/TB` e difere por arredondamento de quadro. A sobra
aparecia como quadro preto no fim ou síntese cortada — nunca como erro.

Precisa de ffmpeg. Sem ele, os testes se marcam como pulados em vez de falhar.
"""

import json
import shutil
import subprocess

import pytest

from editor import plano

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="precisa de ffmpeg e ffprobe",
)

DURACAO_REAL = 3.0
DURACAO_MENTIROSA = 11.0


@pytest.fixture
def video(tmp_path):
    """Um vídeo de 3 segundos, preto, que serve só para ser medido."""
    destino = tmp_path / "v.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", f"color=c=black:s=320x180:d={DURACAO_REAL}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(destino)],
        check=True,
    )
    return destino


def transcricao(duracao):
    """Uma transcrição que afirma uma duração — possivelmente errada."""
    palavras = [
        {"palavra": "primeira", "inicio": 0.2, "fim": 0.8},
        {"palavra": "segunda", "inicio": 1.0, "fim": 1.6},
        {"palavra": "terceira", "inicio": 1.8, "fim": 2.4},
    ]
    return {
        "idioma": "pt",
        "duracao": duracao,
        "palavras": palavras,
        "segmentos": [{"inicio": 0.2, "fim": 2.4,
                       "texto": "primeira segunda terceira"}],
    }


def test_a_duracao_vem_do_arquivo_e_nao_da_transcricao(video):
    p = plano.esqueleto(transcricao(DURACAO_MENTIROSA), video)
    assert p["duracao"] == pytest.approx(DURACAO_REAL, abs=0.2), (
        "a transcrição dizia 11s; quem manda é o arquivo"
    )


def test_a_ultima_cena_termina_dentro_do_video(video):
    p = plano.esqueleto(transcricao(DURACAO_MENTIROSA), video)
    assert p["cenas"], "o esqueleto tem que produzir ao menos uma cena"
    assert p["cenas"][-1]["fim"] <= p["duracao"] + 1e-6


def test_duracao_explicita_ganha_de_tudo(video):
    p = plano.esqueleto(transcricao(DURACAO_MENTIROSA), video, duracao=7.0)
    assert p["duracao"] == pytest.approx(7.0)


def test_transcricao_e_a_reserva_quando_o_arquivo_some(tmp_path):
    """Arquivo ilegível não derruba o planejamento: cai na transcrição."""
    fantasma = tmp_path / "nao_existe.mp4"
    p = plano.esqueleto(transcricao(DURACAO_MENTIROSA), fantasma)
    assert p["duracao"] == pytest.approx(DURACAO_MENTIROSA)


def test_as_dimensoes_saem_do_arquivo(video):
    assert plano.dimensoes(video) == {"largura": 320, "altura": 180}


def test_dimensoes_avisa_quando_nao_consegue_medir(tmp_path, capsys):
    """O padrão 1080x1920 mente sobre um vídeo horizontal — tem que avisar."""
    caido = plano.dimensoes(tmp_path / "nao_existe.mp4")
    assert caido == {"largura": 1080, "altura": 1920}
    assert "não consegui medir" in capsys.readouterr().out.lower()


def test_gerar_fundo_nao_deixa_parcial_para_tras(video, tmp_path):
    destino = tmp_path / "fundo.mp4"
    plano.gerar_fundo(video, destino)
    assert destino.exists()
    assert not list(tmp_path.glob("*.parcial.*"))


def test_fundo_quebrado_nao_vira_arquivo_valido(tmp_path):
    """ffmpeg falhando não pode deixar um mp4 truncado que pareça pronto."""
    destino = tmp_path / "fundo.mp4"
    with pytest.raises(subprocess.CalledProcessError):
        plano.gerar_fundo(tmp_path / "nao_existe.mp4", destino)
    assert not destino.exists()
    assert not list(tmp_path.glob("*.parcial.*"))


def test_o_plano_salvo_e_relido_igual(video, tmp_path):
    p = plano.esqueleto(transcricao(DURACAO_MENTIROSA), video)
    destino = tmp_path / "p.scene_plan.json"
    plano.salvar(p, destino)
    assert json.loads(destino.read_text(encoding="utf-8")) == p
