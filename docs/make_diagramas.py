"""Gera os diagramas de arquitetura (PNG) a partir do que está implementado. Requer graphviz (dot) e matplotlib."""
import os, re, subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "diagramas"); os.makedirs(D, exist_ok=True)
RED, GOLD = "#8B1A14", "#D4A017"
BASE = 'graph [fontname="Times-Roman", dpi=200, pad=0.2]; node [fontname="Times-Roman", fontsize=11, style="filled", fillcolor="#F5E9E8", color="%s"]; edge [fontname="Times-Roman", fontsize=10, color="#444444"];' % RED


def dot(nome, src):
    p = os.path.join(D, nome + ".dot"); open(p, "w", encoding="utf-8").write(src)
    subprocess.check_call(["dot", "-Tpng", p, "-o", os.path.join(D, nome + ".png")]); os.remove(p)


dot("componentes", "digraph G { rankdir=TB; " + BASE + """
 U [label="Navegador", shape=ellipse, fillcolor="#FBF3DC", color="%s"];
 F [label="Frontend\\nReact + TypeScript", shape=box];
 B [label="FastAPI\\napp.main", shape=box];
 R [label="api/routes.py", shape=box];
 E [label="services/engine.py", shape=box];
 I [label="services/insights.py", shape=box];
 P [label="algorithm/mga_pipeline.py\\nbuild, sim_matrix,\\nrecommend, explain", shape=box, fillcolor="#FBF3DC", color="%s"];
 D [label="Base_Jogos\\n(.xlsx)", shape=cylinder]; X [label="MGA_Resultados\\n(.xlsx)", shape=cylinder];
 U -> F; F -> B [label="REST /api"]; B -> R; R -> E; R -> I; E -> P; E -> D; I -> X; }""" % (GOLD, GOLD))
dot("casos_de_uso", "digraph G { rankdir=LR; " + BASE + """
 V [label="Visitante", shape=ellipse, fillcolor="#FBF3DC", color="%s"];
 node [shape=ellipse];
 a [label="Explorar catálogo"]; b [label="Pesquisar jogo"]; c [label="Obter Top 5"]; d [label="Ver explicação"]; e [label="Comparar dois jogos"]; f [label="Consultar indicadores"];
 V -> a; V -> b; V -> c; V -> d; V -> e; V -> f;
 c -> b [label="inclui", style=dashed]; d -> c [label="estende", style=dashed]; }""" % GOLD)
dot("fluxo_algoritmo", "digraph G { rankdir=TB; " + BASE + """
 node [shape=box];
 a [label="Base_Jogos (66 × 14)"]; b [label="Tratamento e remoção de colunas sem uso"];
 c [label="Numéricos: log1p, mediana,\\nz-score, indicadores de ausência"]; d [label="Gênero: taxonomia + multi-hot"];
 e [label="Plataforma: famílias + multi-hot"]; f [label="País: one-hot"];
 g [label="Peso do bloco ÷ √(nº de colunas)", fillcolor="#FBF3DC", color="%s"]; h [label="Matriz 66 × 34"];
 i [label="Cosseno 66 × 66"]; j [label="Remove o próprio jogo, ordena, Top-N"]; k [label="explain: compartilhados + numéricos próximos"];
 a -> b; b -> c; b -> d; b -> e; b -> f; c -> g; d -> g; e -> g; f -> g; g -> h -> i -> j -> k; }""" % GOLD)
dot("modelo_dados", "digraph G { " + BASE + """
 node [shape=record, fillcolor="#F5E9E8"];
 J [label="{JOGO|id : int (posição na aba Base_Jogos)\\ljogo : texto\\lano : int\\ldiretor : texto\\lquantidade_premios : int\\lvendas_milhoes : decimal\\lpais_maior_vendas : texto\\lplataforma : texto (multivalorada)\\lgenero : texto\\ljogadores_concluiram_hltb : int\\lnota_publico_metacritic : decimal\\lnota_critica_metacritic : int\\lcover_url : texto (opcional)\\l}"]; }""")

# sequência (recomendação + explicação)
fig, ax = plt.subplots(figsize=(7.6, 5.6)); ax.axis("off")
atores = ["Usuário", "Frontend", "API", "Engine", "mga_pipeline"]; xs = [0.5, 2.3, 4.1, 5.9, 7.7]
msgs = [(0, 1, "pesquisa e escolhe um jogo"), (1, 2, "GET /api/games/search?q="), (2, 1, "jogos encontrados"), (0, 1, "Recomendar"),
        (1, 2, "POST /api/recommendations"), (2, 3, "recommend(i, 5)"), (3, 4, "recommend(S, df, nome, 5)"), (4, 3, "5 pares (jogo, cosseno)"),
        (2, 1, "Top 5 com posição e dados"), (0, 1, "Por que este jogo?"), (1, 2, "POST /api/explanations"), (2, 3, "explain(i, j)"),
        (3, 4, "explain(X, df, i, j)"), (4, 3, "atributos"), (3, 1, "compartilhados + numéricos próximos")]
for a, x in zip(atores, xs):
    ax.text(x, 10.3, a, ha="center", va="center", fontsize=9, fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#F5E9E8", ec=RED))
    ax.plot([x, x], [0, 9.9], color="#999", lw=0.8, ls="--")
for k, (a, b, t) in enumerate(msgs):
    y = 9.4 - k * 0.62
    ax.annotate("", xy=(xs[b], y), xytext=(xs[a], y), arrowprops=dict(arrowstyle="-|>", color=GOLD if a > b else RED, lw=1.2, ls="--" if a > b else "-"))
    ax.text((xs[a] + xs[b]) / 2, y + 0.12, t, ha="center", va="bottom", fontsize=7.5)
ax.set_xlim(-0.3, 8.5); ax.set_ylim(-0.2, 10.8); fig.tight_layout(); fig.savefig(os.path.join(D, "sequencia_recomendacao.png"), dpi=200); plt.close(fig)

# versão do documento de arquitetura para PDF: troca os blocos Mermaid pelas imagens
s = open(os.path.join(HERE, "arquitetura.md"), encoding="utf-8").read()
figs = [("componentes", "Figura 20 – Diagrama de componentes do MGA Discovery"), ("sequencia_recomendacao", "Figura 21 – Diagrama de sequência da recomendação com explicação"),
        ("casos_de_uso", "Figura 22 – Diagrama de casos de uso"), ("fluxo_algoritmo", "Figura 23 – Fluxograma do algoritmo"), ("modelo_dados", "Figura 24 – Modelo de dados do catálogo")]
it = iter(figs)
def troca(m):
    n, c = next(it); return f"![{c}](diagramas/{n}.png)\n\n**{c}.**"
s = re.sub(r"```mermaid.*?```", troca, s, flags=re.S)
s = s.replace("Os diagramas abaixo usam Mermaid (renderizado pelo GitHub) e descrevem o que está implementado.", "Os diagramas abaixo descrevem o que está implementado.")
open(os.path.join(HERE, "_arquitetura_doc.md"), "w", encoding="utf-8").write(s)
print(sorted(os.listdir(D)))
