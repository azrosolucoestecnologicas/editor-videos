"""Escrita de arquivo e identidade de arquivo.

Os dois erram calado. Um plano meio escrito parece existir; um inode que
coincide entre discos faz o vídeo da rodada passada ser servido como novo.
"""

import json
import os
from unittest import mock

import pytest

from editor import glossario, plano


# ------------------------------------------------- escrita atômica

def test_salvar_escreve_o_json(tmp_path):
    destino = tmp_path / "sub" / "p.json"
    plano.salvar({"a": 1}, destino)
    assert json.loads(destino.read_text(encoding="utf-8")) == {"a": 1}


def test_salvar_nao_deixa_temporario_para_tras(tmp_path):
    destino = tmp_path / "p.json"
    plano.salvar({"a": 1}, destino)
    assert list(tmp_path.iterdir()) == [destino], "nada de .parcial sobrando"


def test_falha_no_meio_nao_deixa_plano_pela_metade(tmp_path):
    """O arquivo antigo tem que sobreviver inteiro a uma escrita que quebrou."""
    destino = tmp_path / "p.json"
    plano.salvar({"versao": 1}, destino)

    with mock.patch("editor.plano.os.replace", side_effect=OSError("disco cheio")):
        with pytest.raises(OSError):
            plano.salvar({"versao": 2}, destino)

    assert json.loads(destino.read_text(encoding="utf-8")) == {"versao": 1}
    assert list(tmp_path.iterdir()) == [destino], "o parcial tem que ser limpo"


# ------------------------------------------------- identidade do arquivo

# Estes dois cobrem `_identidade`, não o ponto onde ela é usada: quem decide
# se o vídeo já está publicado é o `exportar_props`, e exercitá-lo exigiria um
# mp4 de verdade e a pasta public/. Se alguém trocar a chamada de volta por
# `st_ino`, estes testes continuam passando. O guardião aqui é a revisão.
def test_identidade_usa_disco_e_inode(tmp_path):
    arquivo = tmp_path / "v.mp4"
    arquivo.write_bytes(b"x")
    info = arquivo.stat()
    assert plano._identidade(arquivo) == (info.st_dev, info.st_ino)


def test_identidade_distingue_arquivos_iguais_em_discos_diferentes(tmp_path):
    """Dois arquivos com o mesmo inode em discos distintos NÃO são o mesmo.

    É o caso real de `entrada/` e `motion/public/` em discos separados:
    comparando só o inode, o vídeo antigo passava por publicado.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"x")
    b.write_bytes(b"y")

    real = os.stat

    def mesmo_inode(caminho, *args, **kwargs):
        info = real(caminho, *args, **kwargs)
        # Mesmo inode nos dois, discos diferentes.
        disco = 1 if str(caminho).endswith("a") else 2
        return os.stat_result((
            info.st_mode, 42, disco, info.st_nlink, info.st_uid,
            info.st_gid, info.st_size, info.st_atime, info.st_mtime,
            info.st_ctime,
        ))

    with mock.patch("editor.plano.Path.stat", autospec=True,
                    side_effect=lambda self, **kw: mesmo_inode(self)):
        assert plano._identidade(a) != plano._identidade(b)


# ------------------------------------------------- cache do glossário

def test_glossario_le_o_arquivo_uma_vez_so(tmp_path):
    arquivo = tmp_path / "g.json"
    arquivo.write_text(json.dumps({"palavras": {"rag": "RAG"}}), encoding="utf-8")

    glossario.carregar.cache_clear()
    primeiro = glossario.carregar(str(arquivo))
    segundo = glossario.carregar(str(arquivo))

    assert primeiro is segundo, "a segunda chamada tem que vir do cache"
    assert primeiro.palavras == {"rag": "RAG"}
    glossario.carregar.cache_clear()
