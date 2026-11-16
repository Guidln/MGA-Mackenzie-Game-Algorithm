"""Testes do núcleo (requerem a base original em backend/data/ ou MGA_DATA_PATH)."""
import numpy as np
import openpyxl
import pytest

from conftest import needs_data, ROOT
from algorithm.metrics import final_metrics, topk
from app.core import config

pytestmark = needs_data


def test_dataset_carregado(engine):
    assert engine.df.shape == (66, 14)
    assert engine.df.jogo.is_unique


def test_matriz_de_atributos(engine):
    assert engine.X.shape == (66, 34)
    assert set(engine.blocks) == {"numerico", "genero", "plataforma", "pais"}


def test_jogo_inexistente(engine):
    assert not engine.valid_id(66) and not engine.valid_id(-1)


def test_top5_exclui_o_proprio_jogo(engine):
    for i in range(len(engine.df)):
        rec = engine.recommend(i, 5)
        assert len(rec) == 5
        assert i not in [r["jogo"]["id"] for r in rec]
        s = [r["similaridade"] for r in rec]
        assert s == sorted(s, reverse=True)


def test_intervalo_dos_escores(engine):
    assert engine.S.min() >= -1 - 1e-9 and engine.S.max() <= 1 + 1e-9


def test_explicacoes_so_com_atributos_compartilhados(engine):
    X = engine.X
    for i in range(len(engine.df)):
        for r in engine.recommend(i, 5):
            j = r["jogo"]["id"]
            for a in engine.explain(i, j)["compartilhados"]:
                assert X.iloc[i][a["atributo"]] > 0 and X.iloc[j][a["atributo"]] > 0


def test_comparacao(engine):
    i = int(engine.df.index[engine.df.jogo == "Elden Ring"][0])
    j = int(engine.df.index[engine.df.jogo == "Baldur’s Gate 3"][0])
    c = engine.compare(i, j)
    assert c["similaridade"] == pytest.approx(0.8351, abs=1e-4)
    assert "RPG" in c["generos_em_comum"] and "PC" in c["plataformas_em_comum"]


def _referencia():
    ws = openpyxl.load_workbook(config.RESULTS_PATH, data_only=True)
    return ws["Consultas_Top5"], ws["Ablacao"]


def test_reproduz_consultas_do_relatorio(engine):
    consultas, _ = _referencia()
    for ref, pos, jogo, escore, *_ in consultas.iter_rows(min_row=2, values_only=True):
        if ref is None:
            continue
        i = int(engine.df.index[engine.df.jogo == ref][0])
        r = engine.recommend(i, 5)[pos - 1]
        assert r["jogo"]["jogo"] == jogo
        assert r["similaridade"] == pytest.approx(escore, abs=1e-4)


def test_reproduz_indicadores_do_modelo_final(engine):
    _, ab = _referencia()
    ref = next(r for r in ab.iter_rows(min_row=3, values_only=True) if r[0] and r[0].startswith("F "))
    m = final_metrics(engine.S, engine.df)
    assert m["GC5"] == pytest.approx(ref[2], abs=1e-6)
    assert m["PC5"] == pytest.approx(ref[3], abs=1e-6)
    assert m["cobertura"] == pytest.approx(ref[4], abs=1e-6)
    assert m["max_recs"] == ref[5]
    assert m["gini"] == pytest.approx(ref[6], abs=1e-6)
    assert m["div_intralista"] == pytest.approx(ref[9], abs=1e-6)
