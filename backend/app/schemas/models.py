from typing import Optional
from pydantic import BaseModel, Field


class Game(BaseModel):
    id: int
    jogo: str
    ano: int
    diretor: Optional[str] = None
    quantidade_premios: Optional[float] = None
    vendas_milhoes: Optional[float] = None
    pais_maior_vendas: Optional[str] = None
    plataforma: str
    genero: str
    jogadores_concluiram_hltb: Optional[float] = None
    nota_publico_metacritic: Optional[float] = None
    nota_critica_metacritic: Optional[float] = None
    cover_url: Optional[str] = None


class RecommendationRequest(BaseModel):
    game_id: int = Field(ge=0, description="Índice do jogo de referência no catálogo")
    k: int = Field(default=5, ge=1, le=10)


class ExplanationRequest(BaseModel):
    reference_id: int = Field(ge=0)
    recommended_id: int = Field(ge=0)


class CompareRequest(BaseModel):
    game_a: int = Field(ge=0)
    game_b: int = Field(ge=0)
