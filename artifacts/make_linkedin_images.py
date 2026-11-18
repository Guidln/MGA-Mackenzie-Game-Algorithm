"""Imagens 1200x627 (formato LinkedIn) com resultados reais da Etapa 3, lidos de backend/data/MGA_Resultados_Etapa3.xlsx.
Não são capturas de tela da aplicação: são visualizações dos resultados na identidade visual do MGA Discovery."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "linkedin"); os.makedirs(OUT, exist_ok=True)
XLS = os.path.join(HERE, "..", "backend", "data", "MGA_Resultados_Etapa3.xlsx")
INK, PANEL, LINE, RED, GOLD, PAPER, MUTED = "#101010", "#171717", "#2a2a2a", "#8B1A14", "#D4A017", "#F5F5F5", "#9a9a9a"
NOTA = "Visualização com resultados reais da Etapa 3 (mga_etapa3.py, 29/10/2026) • github.com/Guidln/MGA-Mackenzie-Game-Algorithm"
vc = lambda x: f"{x:.4f}".replace(".", ",")


def tela(titulo=None, sub=None):
    fig = plt.figure(figsize=(12, 6.27), dpi=100, facecolor=INK); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1200); ax.set_ylim(0, 627); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 12, 627, boxstyle="square,pad=0", fc=RED, ec="none"))
    ax.text(48, 585, "MGA", color=PAPER, fontsize=13, fontweight="bold", va="center", bbox=dict(boxstyle="round,pad=0.35", fc=RED, ec="none"))
    ax.text(112, 585, "Discovery", color=PAPER, fontsize=14, fontweight="bold", va="center")
    if titulo: ax.text(48, 520, titulo, color=PAPER, fontsize=24, fontweight="bold", va="center")
    if sub: ax.text(48, 482, sub, color=MUTED, fontsize=12, va="center")
    ax.text(48, 24, NOTA, color="#6b6b6b", fontsize=8.5, va="center")
    return fig, ax


def caixa(ax, x, y, w, h, fc=PANEL, ec=LINE, r=14, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))


def salvar(fig, nome):
    fig.savefig(os.path.join(OUT, nome), dpi=100, facecolor=INK); plt.close(fig)


ab = pd.read_excel(XLS, sheet_name="Ablacao", header=None); h = ab.index[ab[0] == "Configuração"][0]
ab.columns = ab.iloc[h]; ab = ab.iloc[h + 1:].reset_index(drop=True); b, f = ab.iloc[0], ab[ab["Configuração"].str.startswith("F ")].iloc[0]
cons = pd.read_excel(XLS, sheet_name="Consultas_Top5"); el = cons[cons["Jogo de referência"] == "Elden Ring"].sort_values("Posição")

# 1) capa
fig, ax = tela("Descubra seu próximo jogo", "Recomendação de jogos digitais baseada em conteúdo, com explicação de cada indicação")
tiles = [("66", "jogos do catálogo\n(The Game Awards, 2014–2024)"), ("34", "atributos por jogo"), (f"{b['Coerência gênero@5']:.3f}".replace(".", ",") + " → " + f"{f['Coerência gênero@5']:.3f}".replace(".", ","), "coerência de gênero@5\nbaseline → modelo final"), ("100%", "das explicações com atributos\nrealmente compartilhados")]
for k, (v, t) in enumerate(tiles):
    x = 48 + k * 285; caixa(ax, x, 190, 265, 200)
    ax.text(x + 22, 330, v, color=GOLD, fontsize=26 if len(v) < 8 else 19, fontweight="bold", va="center"); ax.text(x + 22, 255, t, color=PAPER, fontsize=11, va="top", linespacing=1.4)
ax.text(48, 120, "Projeto Aplicado III • Universidade Presbiteriana Mackenzie", color=PAPER, fontsize=13, va="center")
ax.text(48, 85, "Indicadores de coerência, cobertura e estabilidade; não medem acurácia nem satisfação de usuários.", color=MUTED, fontsize=10.5, va="center")
salvar(fig, "01_capa.png")

# 2) top 5
fig, ax = tela("Elden Ring → 5 jogos recomendados", "Similaridade de cosseno entre os vetores de atributos (modelo final)")
for k, (_, r) in enumerate(el.iterrows()):
    y = 395 - k * 72; caixa(ax, 48, y, 1104, 60)
    ax.text(78, y + 30, str(int(r["Posição"])), color=GOLD, fontsize=20, fontweight="bold", va="center", ha="center")
    ax.text(115, y + 40, r["Jogo recomendado"], color=PAPER, fontsize=14, fontweight="bold", va="center")
    ax.text(115, y + 17, f"{int(r['Ano'])} • {r['Gênero']} • {r['Plataforma']}", color=MUTED, fontsize=10.5, va="center")
    w = 330 * float(r["Escore de cosseno"]); ax.add_patch(FancyBboxPatch((700, y + 22), 330, 16, boxstyle="round,pad=0,rounding_size=8", fc=LINE, ec="none"))
    ax.add_patch(FancyBboxPatch((700, y + 22), w, 16, boxstyle="round,pad=0,rounding_size=8", fc=RED, ec="none"))
    ax.text(1125, y + 30, vc(float(r["Escore de cosseno"])), color=PAPER, fontsize=14, fontweight="bold", va="center", ha="right")
salvar(fig, "02_top5_elden_ring.png")

# 3) por que este jogo
fig, ax = tela("Por que Baldur’s Gate 3?", "Atributos que Elden Ring e Baldur’s Gate 3 compartilham ou têm próximos")
caixa(ax, 48, 300, 440, 130); caixa(ax, 712, 300, 440, 130)
ax.text(72, 395, "Elden Ring", color=PAPER, fontsize=18, fontweight="bold", va="center"); ax.text(72, 350, "referência", color=MUTED, fontsize=11, va="center")
ax.text(736, 395, "Baldur’s Gate 3", color=PAPER, fontsize=18, fontweight="bold", va="center"); ax.text(736, 350, "posição 1 • 2023 • RPG", color=MUTED, fontsize=11, va="center")
ax.text(600, 385, vc(float(el.iloc[0]["Escore de cosseno"])), color=GOLD, fontsize=26, fontweight="bold", va="center", ha="center"); ax.text(600, 340, "similaridade MGA", color=MUTED, fontsize=10.5, va="center", ha="center")
chips = [("Gênero: RPG", True), ("Plataforma: PC", True), ("Plataforma: PlayStation", True), ("Nota crítica (Metacritic)", False), ("Nota pública (Metacritic)", False)]
x = 48
for t, cat in chips:
    wch = 14 + len(t) * 9.2; ax.add_patch(FancyBboxPatch((x, 215), wch, 40, boxstyle="round,pad=0,rounding_size=20", fc=RED if cat else "none", ec=RED if cat else GOLD, lw=1.6))
    ax.text(x + wch / 2, 235, t, color=PAPER if cat else GOLD, fontsize=11, va="center", ha="center"); x += wch + 14
ax.add_patch(FancyBboxPatch((48, 130), 22, 14, boxstyle="round,pad=0,rounding_size=7", fc=RED, ec="none")); ax.text(80, 137, "atributo categórico efetivamente compartilhado", color=PAPER, fontsize=10.5, va="center")
ax.add_patch(FancyBboxPatch((48, 100), 22, 14, boxstyle="round,pad=0,rounding_size=7", fc="none", ec=GOLD, lw=1.6)); ax.text(80, 107, "atributo numérico próximo (mesmo sinal, diferença < 0,5 desvio-padrão)", color=PAPER, fontsize=10.5, va="center")
ax.text(48, 62, "O algoritmo não calcula a contribuição individual de cada atributo ao escore.", color=MUTED, fontsize=10, va="center")
salvar(fig, "03_por_que_baldurs_gate_3.png")

# 4) baseline x final
fig, ax = tela("Baseline versus modelo final", "Resultados da Etapa 3 (66 consultas, Top 5 por jogo)")
cols = [("Coerência gênero@5", "Coerência\ngênero@5"), ("Coerência plataforma@5", "Coerência\nplataforma@5"), ("Cobertura", "Cobertura"), ("Diversidade intralista", "Diversidade\nintralista"), ("Gini", "Gini\n(menor é melhor)")]
ox, oy, W, Hh = 70, 110, 1060, 300
for i in range(6):
    yy = oy + Hh * i / 5; ax.plot([ox, ox + W], [yy, yy], color=LINE, lw=0.8); ax.text(ox - 12, yy, f"{i/5:.1f}", color=MUTED, fontsize=9, ha="right", va="center")
for k, (c, lab) in enumerate(cols):
    cx = ox + 90 + k * 205
    for j, (v, col) in enumerate(((float(b[c]), "#5a5a5a"), (float(f[c]), RED))):
        x0 = cx + j * 62 - 62; ax.add_patch(FancyBboxPatch((x0, oy), 56, Hh * v, boxstyle="round,pad=0,rounding_size=4", fc=col, ec="none"))
        ax.text(x0 + 28, oy + Hh * v + 12, f"{v:.3f}".replace(".", ","), color=PAPER, fontsize=10.5, ha="center", va="center")
    ax.text(cx, oy - 28, lab, color=PAPER, fontsize=10.5, ha="center", va="center", linespacing=1.3)
ax.add_patch(FancyBboxPatch((870, 545), 16, 12, boxstyle="round,pad=0,rounding_size=4", fc="#5a5a5a", ec="none")); ax.text(894, 551, "Baseline (Etapa 2)", color=PAPER, fontsize=10.5, va="center")
ax.add_patch(FancyBboxPatch((1030, 545), 16, 12, boxstyle="round,pad=0,rounding_size=4", fc=RED, ec="none")); ax.text(1054, 551, "Modelo final", color=PAPER, fontsize=10.5, va="center")
salvar(fig, "04_baseline_vs_final.png")

# 5) pipeline
fig, ax = tela("Como o MGA recomenda", "Do catálogo ao Top 5, em cinco passos")
passos = [("Catálogo", "66 jogos\n14 colunas"), ("Atributos", "gênero, plataforma,\npaís e numéricos\n→ 34 por jogo"), ("Pesos por bloco", "gênero 2,0\nnumérico 1,0\nplataforma 0,5 • país 0,5"), ("Cosseno", "matriz 66 × 66\nsem o próprio jogo"), ("Top 5 + explicação", "atributos\ncompartilhados e\nnuméricos próximos")]
for k, (t, d) in enumerate(passos):
    x = 48 + k * 224; caixa(ax, x, 200, 200, 190, ec=RED if k % 2 == 0 else GOLD, lw=1.6)
    ax.text(x + 100, 355, f"{k+1}", color=GOLD, fontsize=18, fontweight="bold", ha="center", va="center"); ax.text(x + 100, 318, t, color=PAPER, fontsize=13, fontweight="bold", ha="center", va="center")
    ax.text(x + 100, 255, d, color=MUTED, fontsize=10.5, ha="center", va="center", linespacing=1.4)
    if k < 4: ax.annotate("", xy=(x + 222, 295), xytext=(x + 202, 295), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4))
ax.text(48, 130, "Recomendação item a item baseada em conteúdo: o usuário escolhe um jogo e o sistema busca os mais parecidos.", color=PAPER, fontsize=11.5, va="center")
ax.text(48, 98, "Não há personalização por perfil de usuário nesta versão.", color=MUTED, fontsize=10.5, va="center")
salvar(fig, "05_como_funciona.png")
print(sorted(os.listdir(OUT)))
