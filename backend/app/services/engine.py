"""Carrega a base e constrói X e S uma única vez (na inicialização da API)."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from algorithm import mga_pipeline as mga  # noqa: E402
from algorithm.mga_pipeline import GENRE_MAP, PLAT_MAP, multi_hot  # noqa: E402

from ..core import config  # noqa: E402

NUM_COLS = ["ano", "quantidade_premios", "vendas_milhoes", "jogadores_concluiram_hltb",
            "nota_publico_metacritic", "nota_critica_metacritic"]
CAT_PREFIX = ("genero_", "plat_", "pais_")


def _clean(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return v.item() if hasattr(v, "item") else v


def _families(p):
    return set(c.split("_", 1)[1] for c in multi_hot(pd.Series([p]), PLAT_MAP, "p", " / ").columns)


class Engine:
    def __init__(self, data_path=None):
        self.df = mga.load(str(data_path or config.DATA_PATH)).reset_index(drop=True)
        self.X, self.blocks = mga.build(self.df)
        self.S = mga.sim_matrix(self.X)
        self.covers = {}
        if config.COVERS_PATH.exists():
            self.covers = json.loads(config.COVERS_PATH.read_text(encoding="utf-8"))

    def game(self, i):
        r = self.df.iloc[i]
        return dict(id=int(i), jogo=r.jogo, ano=int(r.ano), diretor=_clean(r.diretor),
                    quantidade_premios=_clean(r.quantidade_premios), vendas_milhoes=_clean(r.vendas_milhoes),
                    pais_maior_vendas=_clean(r.pais_maior_vendas), plataforma=r.plataforma, genero=r.genero,
                    jogadores_concluiram_hltb=_clean(r.jogadores_concluiram_hltb),
                    nota_publico_metacritic=_clean(r.nota_publico_metacritic),
                    nota_critica_metacritic=_clean(r.nota_critica_metacritic),
                    cover_url=self.covers.get(r.jogo))

    def valid_id(self, i):
        return 0 <= i < len(self.df)

    def search(self, q, limit=10):
        q = q.strip().lower()
        return [self.game(i) for i in range(len(self.df)) if q in self.df.jogo[i].lower()][:limit]

    def recommend(self, i, k=5):
        """Usa recommend() do pipeline original; o próprio jogo já é removido do ranking."""
        recs = mga.recommend(self.S, self.df, self.df.jogo[i], k)
        names = list(self.df.jogo)
        return [dict(posicao=p, similaridade=round(s, 4), jogo=self.game(names.index(n)))
                for p, (n, s) in enumerate(recs, 1)]

    def explain(self, i, j):
        """Usa explain() do pipeline original."""
        a, b = self.df.iloc[i], self.df.iloc[j]
        shared, close = [], []
        for c in mga.explain(self.X, self.df, i, j):
            if c.startswith(CAT_PREFIX):
                tipo, _, val = c.partition("_")
                shared.append(dict(atributo=c, bloco={"genero": "Gênero", "plat": "Plataforma", "pais": "País"}[tipo], valor=val))
            else:
                close.append(dict(atributo=c, valor_referencia=_clean(a[c]), valor_recomendado=_clean(b[c])))
        return dict(similaridade=round(float(self.S[i, j]), 4), compartilhados=shared, numericos_proximos=close,
                    nota=("Resultado de explain(): atributos categóricos com valor positivo nos dois jogos e atributos "
                          "numéricos padronizados, de mesmo sinal, com diferença inferior a 0,5 desvio-padrão. "
                          "O algoritmo não calcula a contribuição individual de cada atributo ao escore."))

    def compare(self, i, j):
        a, b = self.df.iloc[i], self.df.iloc[j]
        ga, gb = set(GENRE_MAP[a.genero]), set(GENRE_MAP[b.genero])
        pa, pb = _families(a.plataforma), _families(b.plataforma)
        order = [x for x in np.argsort(-self.S[i], kind="stable") if x != i]
        return dict(
            jogo_a=self.game(i), jogo_b=self.game(j),
            similaridade=round(float(self.S[i, j]), 4), posicao_de_b_no_ranking_de_a=order.index(j) + 1,
            generos_em_comum=sorted(ga & gb), generos_so_a=sorted(ga - gb), generos_so_b=sorted(gb - ga),
            plataformas_em_comum=sorted(pa & pb), plataformas_so_a=sorted(pa - pb), plataformas_so_b=sorted(pb - pa),
            mesmo_pais=bool(a.pais_maior_vendas == b.pais_maior_vendas), pais_a=a.pais_maior_vendas, pais_b=b.pais_maior_vendas,
            numericos=[dict(atributo=c, jogo_a=_clean(a[c]), jogo_b=_clean(b[c])) for c in NUM_COLS],
            explicacao=self.explain(i, j))
