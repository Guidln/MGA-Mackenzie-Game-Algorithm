from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import Response

from ..core import config
from ..schemas.models import CompareRequest, ExplanationRequest, Game, DraftIn, DraftIn, RecommendationRequest, SurveyIn
from ..services.insights import load_results
from ..services.community import Community
from ..services.survey import Survey

router = APIRouter(prefix="/api")


def engine(request: Request):
    e = getattr(request.app.state, "engine", None)
    if e is None:
        raise HTTPException(503, f"Base de dados não encontrada em {config.DATA_PATH}. "
                                 "Coloque a planilha em backend/data/ ou defina MGA_DATA_PATH.")
    return e


def check(e, *ids):
    for i in ids:
        if not e.valid_id(i):
            raise HTTPException(404, f"Jogo {i} não encontrado (ids válidos: 0 a {len(e.df) - 1}).")


@router.get("/health")
def health(request: Request):
    e = getattr(request.app.state, "engine", None)
    return {"status": "ok" if e else "dados_ausentes", "jogos": len(e.df) if e else 0,
            "matriz": list(e.X.shape) if e else None, "base": str(config.DATA_PATH),
            "mensagem": None if e else "Copie a planilha da base (aba Base_Jogos) para backend/data/ e reinicie a API."}


@router.get("/games", response_model=list[Game])
def games(request: Request):
    e = engine(request)
    return [e.game(i) for i in range(len(e.df))]


@router.get("/games/search", response_model=list[Game])
def search(request: Request, q: str = Query(min_length=1), limit: int = Query(10, ge=1, le=66)):
    return engine(request).search(q, limit)


@router.get("/games/{game_id}", response_model=Game)
def game(request: Request, game_id: int):
    e = engine(request); check(e, game_id)
    return e.game(game_id)


@router.post("/recommendations")
def recommendations(request: Request, body: RecommendationRequest):
    e = engine(request); check(e, body.game_id)
    comm = community(len(e.df)) if body.modo == "hibrido" else None
    return {"referencia": e.game(body.game_id), "k": body.k, "modo": "hibrido" if comm and comm.weight else "mga",
            "peso_comunidade": round(comm.weight, 3) if comm else 0, "respostas": comm.n_resp if comm else 0,
            "recomendacoes": e.recommend_hybrid(body.game_id, body.k, comm),
            "aviso": "A similaridade de cosseno mede proximidade entre vetores de atributos; não é probabilidade de preferência. "
                     "No modo com comunidade, o ranking também considera as respostas da pesquisa."}


@router.post("/explanations")
def explanations(request: Request, body: ExplanationRequest):
    e = engine(request); check(e, body.reference_id, body.recommended_id)
    if body.reference_id == body.recommended_id:
        raise HTTPException(422, "Os jogos devem ser diferentes.")
    return {"referencia": e.game(body.reference_id), "recomendado": e.game(body.recommended_id),
            **e.explain(body.reference_id, body.recommended_id)}


@router.post("/compare")
def compare(request: Request, body: CompareRequest):
    e = engine(request); check(e, body.game_a, body.game_b)
    if body.game_a == body.game_b:
        raise HTTPException(422, "Escolha dois jogos diferentes.")
    return e.compare(body.game_a, body.game_b)


def _results():
    if not config.RESULTS_PATH.exists():
        raise HTTPException(503, f"Planilha de resultados não encontrada em {config.RESULTS_PATH}.")
    return load_results(config.RESULTS_PATH)


@router.get("/insights")
def insights(request: Request):
    r = _results(); e = getattr(request.app.state, "engine", None)
    return {"total_jogos": len(e.df) if e else None, "total_atributos": e.X.shape[1] if e else None,
            "matriz": list(e.X.shape) if e else None,
            "baseline": r["ablacao"][0], "final": next(a for a in r["ablacao"] if a["configuracao"].startswith("F ")),
            "ablacao": r["ablacao"], "consistencia": r["consistencia"], "resumo_sensibilidade": r["resumo_sensibilidade"],
            "fonte": "MGA_Resultados_Etapa3.xlsx (mga_etapa3.py, execução de 29/10/2026)"}


@router.get("/insights/sensitivity")
def sensitivity():
    r = _results()
    return {"resumo": r["resumo_sensibilidade"], "configuracoes": r["sensibilidade"]}


# ---------- Pesquisa com usuários ----------
_survey = None


def survey():
    global _survey
    if _survey is None:
        _survey = Survey(config.SURVEY_DB)
    return _survey


def admin(x_admin_token: Optional[str] = Header(default=None)):
    if config.ADMIN_TOKEN and x_admin_token != config.ADMIN_TOKEN:
        raise HTTPException(401, "Token de administrador inválido ou ausente.")


_comm = (None, None)


def community(n_games):
    """Recalcula o modelo da comunidade só quando chegam respostas novas."""
    global _comm
    n, users, pairs, sig = survey().community_data()
    if _comm[0] != (sig, n_games):
        _comm = ((sig, n_games), Community(n_games, n, users, pairs))
    return _comm[1]


@router.get("/community")
def community_info(request: Request):
    e = engine(request); c = community(len(e.df)); names = list(e.df.jogo)
    pop = sorted([j for j in range(len(names)) if c.count[j] >= 1], key=lambda j: (-c.quality[j], -c.count[j]))[:6]
    sug = survey().summary(names)["sugeridos_pelos_usuarios"][:8]
    return {"respostas": c.n_resp, "peso": round(c.weight, 3), "sugeridos": sug,
            "populares": [dict(jogo=e.game(j), nota_media=round(float(c.mean[j]), 2), notas=int(c.count[j])) for j in pop]}


@router.put("/survey/draft/{sid}")
def survey_draft(sid: str, body: DraftIn):
    if not (8 <= len(sid) <= 64) or not sid.replace("-", "").isalnum() or len(str(body.payload)) > 60_000:
        raise HTTPException(422, "Rascunho inválido.")
    survey().save_draft(sid, body.payload)
    return {"salvo": True}


@router.post("/survey", status_code=201)
def survey_submit(request: Request, body: SurveyIn):
    e = engine(request)
    if not body.consentimento:
        raise HTTPException(422, "É necessário aceitar o uso anônimo das respostas para participar.")
    if not body.jogos and not body.extras:
        raise HTTPException(422, "Selecione ao menos um jogo que você já jogou ou sugira um título.")
    if len(str(body.sistema)) > 5000:
        raise HTTPException(422, "Respostas abertas muito longas.")
    rid = survey().add(body.model_dump(), len(e.df))
    return {"id": rid, "mensagem": "Obrigado! Sua resposta foi registrada."}


@router.get("/survey/summary")
def survey_summary(request: Request, x_admin_token: Optional[str] = Header(default=None)):
    admin(x_admin_token)
    return survey().summary(list(engine(request).df.jogo))


@router.get("/survey/export.csv")
def survey_export(request: Request, token: Optional[str] = None, x_admin_token: Optional[str] = Header(default=None)):
    admin(x_admin_token or token)
    return Response(survey().export_csv(list(engine(request).df.jogo)), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=respostas_mga.csv"})


@router.post("/survey/draft", status_code=204)
def survey_draft(body: DraftIn):
    """Salva o formulário parcial (autosave) para não perder nada do que foi preenchido."""
    import json
    if len(json.dumps(body.payload)) > 60_000:
        raise HTTPException(413, "Rascunho grande demais.")
    survey().save_draft(body.sessao, body.payload)


@router.get("/survey/export.json")
def survey_export_json(token: Optional[str] = None, x_admin_token: Optional[str] = Header(default=None)):
    admin(x_admin_token or token)
    return Response(survey().export_json(), media_type="application/json; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=respostas_mga_completo.json"})


@router.get("/survey/export.json")
def survey_export_json(token: Optional[str] = None, x_admin_token: Optional[str] = Header(default=None)):
    admin(x_admin_token or token)
    return Response(survey().export_json(), media_type="application/json; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=respostas_mga_completo.json"})
