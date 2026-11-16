"""Indicadores da Etapa 3 (mesmas definições de mga_etapa3.py), para reprodução e testes."""
import itertools
import numpy as np
from .mga_pipeline import GENRE_MAP, PLAT_MAP, multi_hot
import pandas as pd


def topk(S, k=5):
    n = len(S)
    return [[j for j in np.argsort(-S[i], kind='stable') if j != i][:k] for i in range(n)]


def gini(x):
    x = np.sort(np.array(x, float)); c = np.cumsum(x); n = len(x)
    return (n + 1 - 2 * c.sum() / c[-1]) / n


def genre_sets(df):
    return [set(GENRE_MAP[g]) for g in df.genero]


def platform_sets(df):
    return [set(c.split('_', 1)[1] for c in multi_hot(pd.Series([p]), PLAT_MAP, 'p', ' / ').columns)
            for p in df.plataforma]


def final_metrics(S, df, k=5):
    n = len(df); T = topk(S, k); cnt = np.bincount(sum(T, []), minlength=n)
    g, p = genre_sets(df), platform_sets(df)
    return dict(
        GC5=float(np.mean([len(g[i] & g[j]) > 0 for i in range(n) for j in T[i]])),
        PC5=float(np.mean([len(p[i] & p[j]) > 0 for i in range(n) for j in T[i]])),
        cobertura=float((cnt > 0).mean()), max_recs=int(cnt.max()), gini=float(gini(cnt)),
        div_intralista=float(np.mean([1 - np.mean([S[a, b] for a, b in itertools.combinations(T[i], 2)])
                                      for i in range(n)])))
