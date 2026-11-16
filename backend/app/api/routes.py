from fastapi import APIRouter, HTTPException, Query, Request

from ..core import config
from ..schemas.models import CompareRequest, ExplanationRequest, Game, RecommendationRequest
from ..services.insights import load_results

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
    return {"referencia": e.game(body.game_id), "k": body.k, "recomendacoes": e.recommend(body.game_id, body.k),
            "aviso": "A similaridade de cosseno mede proximidade entre vetores de atributos; não é probabilidade de preferência."}


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
