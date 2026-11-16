"""Gera as figuras do relatório a partir de backend/data/MGA_Resultados_Etapa3.xlsx (valores originais, sem alteração)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
XLS = os.path.join(HERE, "..", "backend", "data", "MGA_Resultados_Etapa3.xlsx")
OUT = os.path.join(HERE, "figures"); os.makedirs(OUT, exist_ok=True)
RED, GOLD, DARK = "#8B1A14", "#D4A017", "#262626"
FONTE = "Fonte: elaboração própria a partir de mga_etapa3.py (execução de 29/10/2026); 66 consultas, N = 5."
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

raw = pd.read_excel(XLS, sheet_name="Ablacao", header=None)
hdr = raw.index[raw[0] == "Configuração"][0]
ab = raw.iloc[hdr + 1:].copy(); ab.columns = raw.iloc[hdr]; ab = ab.dropna(subset=["Nº atributos"]).reset_index(drop=True)
ab["rot"] = ["Baseline", "E1", "E2", "E3", "E4", "E5", "F (final)", "V1", "V2", "V3"][: len(ab)]
sens = pd.read_excel(XLS, sheet_name="Sensibilidade", usecols=range(8)).dropna()
cor = [DARK] + [GOLD] * 5 + [RED] + ["#8a8a8a"] * 3


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=200); plt.close(fig)


def por_config(col, titulo, ylabel, fname, pct=False, dec=3):
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    v = ab[col].astype(float).values
    b = ax.bar(ab.rot, v, color=cor)
    for r, x in zip(b, v):
        ax.text(r.get_x() + r.get_width() / 2, x + max(v) * 0.01, f"{x*100:.1f}%" if pct else f"{x:.{dec}f}", ha="center", fontsize=7.5)
    ax.set_title(titulo, fontweight="bold", fontsize=10); ax.set_ylabel(ylabel); ax.set_xlabel("Configuração do pipeline")
    ax.set_ylim(0, max(v) * 1.15); save(fig, fname)


por_config("Coerência gênero@5", "Coerência de gênero@5 por configuração", "Proporção de itens (0 a 1)", "fig_coerencia_genero.png")
por_config("Coerência plataforma@5", "Coerência de plataforma@5 por configuração", "Proporção de itens (0 a 1)", "fig_coerencia_plataforma.png")
por_config("Diversidade intralista", "Diversidade intralista por configuração", "1 − similaridade média da lista", "fig_diversidade.png")
por_config("Gini", "Concentração das recomendações (Gini) por configuração", "Coeficiente de Gini (menor = menos concentrado)", "fig_gini.png")
por_config("Cobertura", "Cobertura do catálogo por configuração", "Jogos presentes em ao menos um Top-5", "fig_cobertura.png", pct=True)

# baseline x final
b, f = ab.iloc[0], ab[ab.rot == "F (final)"].iloc[0]
cols = [("Coerência gênero@5", "Coerência\ngênero@5"), ("Coerência plataforma@5", "Coerência\nplataforma@5"),
        ("Cobertura", "Cobertura"), ("Diversidade intralista", "Diversidade\nintralista"), ("Gini", "Gini")]
x = np.arange(len(cols)); fig, ax = plt.subplots(figsize=(7.4, 3.6))
vb = [b[c] for c, _ in cols]; vf = [f[c] for c, _ in cols]
r1 = ax.bar(x - .2, vb, .4, color=DARK, label="Baseline (Etapa 2)"); r2 = ax.bar(x + .2, vf, .4, color=RED, label="Modelo final")
for rs in (r1, r2):
    for r in rs: ax.text(r.get_x() + r.get_width() / 2, r.get_height() + .012, f"{r.get_height():.3f}", ha="center", fontsize=7.5)
ax.set_xticks(x); ax.set_xticklabels([l for _, l in cols]); ax.set_ylim(0, 1.15); ax.set_ylabel("Valor do indicador")
ax.set_title("Baseline versus modelo final", fontweight="bold", fontsize=10); ax.legend(frameon=False, ncol=2, loc="upper left")
save(fig, "fig_baseline_vs_final.png")

# sensibilidade
fig, ax = plt.subplots(figsize=(6.4, 3.3)); ax.hist(sens["Jaccard@5 vs final"], bins=12, color=RED, edgecolor="white")
m = sens["Jaccard@5 vs final"].mean(); ax.axvline(m, color=GOLD, ls="--", label=f"Média = {m:.2f}")
ax.set_xlabel("Jaccard@5 em relação ao modelo final"); ax.set_ylabel("Configurações de pesos (n = 54)"); ax.legend(frameon=False)
ax.set_title("Sensibilidade aos pesos dos blocos", fontweight="bold", fontsize=10); save(fig, "fig_sensibilidade.png")

# recomendação e atributos explicativos (Elden Ring -> Baldur's Gate 3; valores da aba Consultas_Top5)
fig, ax = plt.subplots(figsize=(7.4, 3.2)); ax.axis("off")
rows = [["Gênero", "RPG", "RPG", "categórico compartilhado"], ["Plataforma", "PC, PlayStation (PS5)", "PC, PlayStation (PS5)", "categórico compartilhado"],
        ["Nota crítica Metacritic", "valor padronizado próximo", "valor padronizado próximo", "numérico próximo"],
        ["Nota pública Metacritic", "valor padronizado próximo", "valor padronizado próximo", "numérico próximo"]]
t = ax.table(cellText=rows, colLabels=["Atributo", "Elden Ring (referência)", "Baldur’s Gate 3 (posição 1)", "Tipo na explain()"], loc="center", cellLoc="left")
t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.7)
for (r, c), cell in t.get_celld().items():
    cell.set_edgecolor("#bbb")
    if r == 0: cell.set_facecolor(RED); cell.get_text().set_color("white")
ax.set_title("Elden Ring → Baldur’s Gate 3: similaridade de cosseno = 0,8351", fontweight="bold", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_explicacao_elden_bg3.png"), dpi=200); plt.close(fig)

# fluxograma (mesmo conteúdo do relatório, com a descrição fiel à explain())
fig, ax = plt.subplots(figsize=(7.4, 8.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(3.2, 19.6)
steps = [("1. Base de dados", "Base_Jogos (66 jogos × 14 colunas, 2014–2024)"),
 ("2. Análise exploratória e qualidade", "tipos, ausentes, duplicidades, cardinalidade, escalas"),
 ("3. Tratamento", "unificação \"EUA\"; N/D → vazio; colunas sem uso removidas do vetor"),
 ("4. Engenharia de atributos", "taxonomia de gênero • famílias de plataforma • país (one-hot)\nlog1p + z-score nas numéricas • mediana + indicador de ausência"),
 ("5. Ponderação por bloco", "cada bloco ÷ √(nº de colunas) × peso a priori (gênero 2; numérico 1; plataforma 0,5; país 0,5)"),
 ("6. Representação vetorial", "matriz 66 × 34 (um vetor por jogo)"),
 ("7. Similaridade de cosseno", "matriz 66 × 66 • remoção do item consultado • ranking Top-N"),
 ("8. Explicabilidade", "atributos categóricos compartilhados + numéricos próximos (explain)"),
 ("9. Avaliação", "consistência • coerência@5 • cobertura/concentração • estabilidade")]
h, y = 1.65, 19.2
for k, (tt, s) in enumerate(steps):
    ax.add_patch(plt.Rectangle((0.6, y - h + 0.25), 8.8, h - 0.55, fc="#F5E9E8" if k % 2 == 0 else "#FBF3DC", ec=RED if k % 2 == 0 else GOLD, lw=1.5))
    ax.text(5, y - 0.68, tt, ha="center", va="center", fontweight="bold", fontsize=10.5); ax.text(5, y - 1.12, s, ha="center", va="center", fontsize=8)
    if k < len(steps) - 1: ax.annotate("", xy=(5, y - h + 0.05), xytext=(5, y - h + 0.27), arrowprops=dict(arrowstyle="-|>", color=DARK))
    y -= h + 0.1
ax.set_title("Fluxograma da metodologia do MGA", fontweight="bold"); save(fig, "fig_fluxograma.png")
print(sorted(os.listdir(OUT)))
