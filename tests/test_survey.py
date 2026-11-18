import numpy as np
from app.services.community import Community
from app.services.survey import Survey

NAMES = ["A", "B", "C"]
BASE = dict(nome="x", faixa_etaria="18–24", horas_semana="3–10 h", plataformas=["PC"], generos=["RPG"], descoberta=["YouTube"],
            valores=dict(historia=5), sistema=dict(nps=10, clareza=4), wishlist=[2, 99], favorito_id=0, sid="abc12345",
            jogos=[dict(game_id=0, nota=5), dict(game_id=1, nota=3), dict(game_id=99, nota=1)],
            extras=["Hollow Knight", "hollow  knight!"], referencia_id=0,
            avaliacoes=[dict(game_id=1, posicao=1, similaridade=.9, resposta="quero"), dict(game_id=2, posicao=2, resposta="nao")],
            nota_geral=4, comentario="ok")


def test_survey_roundtrip(tmp_path):
    s = Survey(tmp_path / "t.db")
    s.save_draft("abc12345", {"parcial": True})
    s.add(BASE, 3); s.add(dict(BASE, sid="zzz98765"), 3)
    r = s.summary(NAMES)
    assert r["total_respostas"] == 2 and r["rascunhos"]["concluidos"] == 2
    assert r["mais_jogados"][0]["jogo"] == "A" and r["mais_jogados"][0]["citacoes"] == 2   # id 99 descartado
    assert r["sugeridos_pelos_usuarios"] == [dict(titulo="Hollow Knight", votos=2)]         # duplicatas normalizadas
    assert r["recomendacoes"]["aprovacao"] == 0.5 and r["sistema"]["nps"] == 100 and r["quero_jogar"][0]["jogo"] == "C"
    assert "rascunhos" in s.export_json() and s.export_csv(NAMES).count("\n") == 1 + 2 * 6


def test_comunidade_reordena_sem_quebrar_baseline(tmp_path):
    S = np.array([[1, .9, .8, .7], [.9, 1, .5, .5], [.8, .5, 1, .5], [.7, .5, .5, 1]])
    vazio = Community(4, 0, [], {})
    assert vazio.weight == 0
    # 40 usuários aprovam 3 (4º jogo) para a referência 0 e reprovam 1
    pairs = {(0, 3): (40, 40), (0, 1): (0, 40)}
    users = [{0: 5, 3: 5, 1: 2} for _ in range(40)]
    c = Community(4, 40, users, pairs)
    assert 0 < c.weight <= 0.5
    base = [j for j, *_ in vazio.rank(S[0], 0, 3)] if vazio.weight else [1, 2, 3]
    novo = [j for j, *_ in c.rank(S[0], 0, 3)]
    assert base == [1, 2, 3] and novo[0] == 3 and novo[-1] == 1   # consenso da comunidade sobe o 3 e desce o 1
