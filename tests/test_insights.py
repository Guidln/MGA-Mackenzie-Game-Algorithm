"""Roda sem a base original e sem FastAPI: confere a leitura da planilha de resultados."""
import pytest
from app.core import config
from app.services.insights import load_results


@pytest.fixture(scope="module")
def r():
    return load_results(config.RESULTS_PATH)


def test_ablacao_comeca_no_baseline(r):
    assert len(r["ablacao"]) == 10
    assert r["ablacao"][0]["configuracao"].startswith("Baseline")
    assert r["ablacao"][0]["coerencia_genero"] == pytest.approx(0.3333, abs=1e-3)


def test_modelo_final(r):
    f = next(a for a in r["ablacao"] if a["configuracao"].startswith("F "))
    assert f["coerencia_genero"] == pytest.approx(0.5030, abs=1e-3) and f["n_atributos"] == 34


def test_sensibilidade_e_consistencia(r):
    s = r["resumo_sensibilidade"]
    assert s["n"] == 54 and s["jaccard_medio"] == pytest.approx(0.6228, abs=1e-3)
    assert r["consistencia"]["Validade das explicações — final"] == 1
