from typing import Annotated, Any, Optional
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
    modo: str = Field(default="hibrido", pattern="^(mga|hibrido)$", description="mga = só conteúdo; hibrido = conteúdo + feedback da comunidade")


class ExplanationRequest(BaseModel):
    reference_id: int = Field(ge=0)
    recommended_id: int = Field(ge=0)


class CompareRequest(BaseModel):
    game_a: int = Field(ge=0)
    game_b: int = Field(ge=0)


class JogoNota(BaseModel):
    game_id: int = Field(ge=0)
    nota: int = Field(ge=1, le=5)


class AvaliacaoRec(BaseModel):
    game_id: int = Field(ge=0)
    posicao: int = Field(ge=1, le=10)
    referencia_id: Optional[int] = Field(default=None, ge=0)
    similaridade: Optional[float] = None
    resposta: str = Field(pattern="^(quero|gostei|nao)$")  # quero jogar / já joguei e gostei / não me interessa


class SurveyIn(BaseModel):
    nome: Optional[str] = Field(default=None, max_length=80)
    faixa_etaria: Optional[str] = Field(default=None, max_length=20)
    horas_semana: Optional[str] = Field(default=None, max_length=20)
    plataformas: list[str] = Field(default_factory=list, max_length=15)
    generos: list[str] = Field(default_factory=list, max_length=25)
    jogos: list[JogoNota] = Field(default_factory=list, max_length=80)
    extras: list[str] = Field(default_factory=list, max_length=10)
    referencia_id: Optional[int] = Field(default=None, ge=0)
    avaliacoes: list[AvaliacaoRec] = Field(default_factory=list, max_length=10)
    nota_geral: Optional[int] = Field(default=None, ge=1, le=5)
    comentario: Optional[str] = Field(default=None, max_length=1000)
    regiao: Optional[str] = Field(default=None, max_length=30)
    anos_jogando: Optional[str] = Field(default=None, max_length=30)
    gasto_mensal: Optional[str] = Field(default=None, max_length=30)
    descoberta: list[str] = Field(default_factory=list, max_length=15)
    valores: dict[str, Annotated[int, Field(ge=1, le=5)]] = Field(default_factory=dict, max_length=20)
    estilo: Optional[str] = Field(default=None, max_length=30)
    wishlist: list[int] = Field(default_factory=list, max_length=80)
    favorito_id: Optional[int] = Field(default=None, ge=0)
    sistema: dict[str, Any] = Field(default_factory=dict, max_length=20)
    sid: Optional[str] = Field(default=None, max_length=64)
    consentimento: bool


class DraftIn(BaseModel):
    payload: dict[str, Any]
    sessao: Optional[str] = Field(default=None, max_length=64)


class DraftIn(BaseModel):
    sessao: str = Field(min_length=8, max_length=64)
    payload: dict
