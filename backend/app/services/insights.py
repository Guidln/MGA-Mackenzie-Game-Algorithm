"""Lê os resultados da Etapa 3 (planilha MGA_Resultados_Etapa3.xlsx) sem recalculá-los."""
import numpy as np
import openpyxl

KEYS = ["configuracao", "n_atributos", "coerencia_genero", "coerencia_plataforma", "cobertura",
        "max_listas", "gini", "escore_medio", "dif_ano", "diversidade", "jaccard_vs_baseline"]


def _rows(ws, first, ncols):
    out = []
    for r in ws.iter_rows(min_row=first, max_col=ncols, values_only=True):
        if r[0] is None:
            break
        out.append(r)
    return out


def load_results(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Ablacao"]
    hdr = next(i for i, r in enumerate(ws.iter_rows(max_col=1, values_only=True), 1) if r[0] == "Configuração")
    ablacao = [dict(zip(KEYS, r)) for r in _rows(ws, hdr + 1, 11)]
    cons = {r[0]: r[1] for r in _rows(wb["Consistencia"], 2, 2)}
    sens = [dict(peso_genero=r[0], peso_plataforma=r[1], peso_numerico=r[2], peso_pais=r[3], jaccard=r[4],
                 coerencia_genero=r[5], max_listas=r[6], cobertura=r[7])
            for r in _rows(wb["Sensibilidade"], 2, 8)]
    j = np.array([s["jaccard"] for s in sens]); g = np.array([s["coerencia_genero"] for s in sens])
    resumo = dict(n=len(sens), jaccard_medio=float(j.mean()), jaccard_minimo=float(j.min()),
                  gc5_minimo=float(g.min()), gc5_maximo=float(g.max()))
    return dict(ablacao=ablacao, consistencia=cons, sensibilidade=sens, resumo_sensibilidade=resumo)
