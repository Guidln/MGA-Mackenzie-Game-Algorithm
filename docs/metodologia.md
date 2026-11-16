# Metodologia

A metodologia completa está na seção 4 do relatório da Etapa 3 (`artifacts/reports/MGA_Projeto_Aplicado_III_Etapa_3.pdf`). Este arquivo resume o que o código faz, para quem for ler o repositório (<https://github.com/Guidln/MGA-Mackenzie-Game-Algorithm>).

## Dados
Planilha `the_game_awards_2014_2024_ofc.xlsx`, aba `Base_Jogos`: 66 jogos, 14 colunas. Não entram no vetor: `jogo`, `fonte_metacritic`, `fonte_hltb`, `plataforma_mais_zerada_hltb` (sem nenhum valor) e `diretor` (50 de 57 valores únicos).

## Construção da matriz (`algorithm/mga_pipeline.py`, função `build`)
1. Numéricos: `ano`, `quantidade_premios`, `vendas_milhoes`, `jogadores_concluiram_hltb`, `nota_publico_metacritic`, `nota_critica_metacritic`. `log1p` em vendas e HLTB, imputação pela mediana, z-score. Dois indicadores binários de ausência (vendas e HLTB).
2. Gênero: 21 rótulos mapeados por `GENRE_MAP` e codificados em multi-hot (17 colunas).
3. Plataforma: combinações separadas por " / " e mapeadas por `PLAT_MAP` para famílias, em multi-hot (5 colunas).
4. País de maior venda: one-hot (4 colunas).
5. Cada bloco é multiplicado por `peso / sqrt(nº de colunas)`. Pesos: gênero 2,0; numérico 1,0; plataforma 0,5; país 0,5.
6. Resultado: matriz 66 × 34.

## Recomendação e explicação
- `sim_matrix`: cosseno (scikit-learn), matriz 66 × 66.
- `recommend`: remove o próprio jogo e devolve os k mais similares (desempate estável pela ordem da base).
- `explain`: até 3 atributos categóricos com valor positivo nos dois jogos (ordem gênero, plataforma, país) e até 2 numéricos padronizados com mesmo sinal e diferença absoluta menor que 0,5. Não calcula contribuição de atributos ao escore.

## Avaliação
Definida na seção 4.7 do relatório e implementada em `algorithm/mga_etapa3.py` (script original da Etapa 3) e `algorithm/metrics.py` (mesmas definições, usadas nos testes). `python artifacts/make_figures.py` regenera as figuras a partir da planilha de resultados.

## O que a avaliação não mostra
Não há julgamentos de relevância. Os indicadores medem coerência, cobertura, diversidade e estabilidade, e não acurácia nem satisfação.
