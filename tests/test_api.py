"""Testes da API (requerem a base original)."""
import pytest
from conftest import needs_data


def test_health_inicializa(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] in ("ok", "dados_ausentes")


def test_insights_usam_planilha_de_resultados(client):
    d = client.get("/api/insights").json()
    assert d["baseline"]["coerencia_genero"] == pytest.approx(0.3333, abs=1e-3)
    assert d["final"]["coerencia_genero"] == pytest.approx(0.5030, abs=1e-3)
    assert client.get("/api/insights/sensitivity").json()["resumo"]["n"] == 54


@needs_data
def test_catalogo_e_busca(client):
    assert len(client.get("/api/games").json()) == 66
    assert any(g["jogo"] == "Elden Ring" for g in client.get("/api/games/search", params={"q": "elden"}).json())


@needs_data
def test_jogo_inexistente_retorna_404(client):
    assert client.get("/api/games/999").status_code == 404
    assert client.post("/api/recommendations", json={"game_id": 999}).status_code == 404


@needs_data
def test_validacao_de_entrada(client):
    assert client.post("/api/recommendations", json={"game_id": -1}).status_code == 422
    assert client.post("/api/compare", json={"game_a": 1, "game_b": 1}).status_code == 422


@needs_data
def test_fluxo_recomendacao_explicacao_comparacao(client):
    i = client.get("/api/games/search", params={"q": "elden ring"}).json()[0]["id"]
    rec = client.post("/api/recommendations", json={"game_id": i}).json()
    assert len(rec["recomendacoes"]) == 5
    assert rec["recomendacoes"][0]["jogo"]["jogo"] == "Baldur’s Gate 3"
    j = rec["recomendacoes"][0]["jogo"]["id"]
    ex = client.post("/api/explanations", json={"reference_id": i, "recommended_id": j}).json()
    assert ex["compartilhados"]
    assert client.post("/api/compare", json={"game_a": i, "game_b": j}).json()["similaridade"] == ex["similaridade"]
