# Plano e registro de testes

Repositório do projeto: <https://github.com/Guidln/MGA-Mackenzie-Game-Algorithm>

## Objetivo e escopo
Garantir que a API use o pipeline original sem alterar seus resultados e que a aplicação apresente corretamente recomendações, explicações, comparações e indicadores. Os testes automatizados ficam em `tests/` e usam `pytest`.

## Casos de teste
| Requisito | Teste |
|---|---|
| Inicialização da API | `test_health_inicializa` |
| Carregamento do dataset | `test_dataset_carregado` (66 × 14, nomes únicos) |
| Matriz de atributos | `test_matriz_de_atributos` (66 × 34, quatro blocos) |
| Jogo existente e inexistente | `test_catalogo_e_busca`, `test_jogo_inexistente_retorna_404`, `test_jogo_inexistente` |
| Top 5 | `test_top5_exclui_o_proprio_jogo` (5 itens, ordem decrescente, sem o próprio jogo, nas 66 consultas) |
| Escores em [−1, 1] | `test_intervalo_dos_escores` |
| Explicações com atributos compartilhados | `test_explicacoes_so_com_atributos_compartilhados` |
| Comparação entre jogos | `test_comparacao`, `test_fluxo_recomendacao_explicacao_comparacao` |
| Indicadores | `test_insights_usam_planilha_de_resultados`, `tests/test_insights.py` |
| Validação de entrada | `test_validacao_de_entrada` |
| Reprodução das 15 consultas do relatório (nome e escore, tolerância de 1e-4) | `test_reproduz_consultas_do_relatorio` |
| Reprodução de GC@5, PC@5, cobertura, máximo de listas, Gini e diversidade do modelo final | `test_reproduz_indicadores_do_modelo_final` |

Os testes de reprodução usam a base original do projeto (66 jogos, aba `Base_Jogos`) em `backend/data/`. Sem ela, são ignorados automaticamente.

## Verificações realizadas durante o desenvolvimento
| Verificação | Resultado |
|---|---|
| Compilação sintática dos arquivos Python do backend e dos testes | Sem erros |
| Leitura da planilha de resultados (`insights.py`, `tests/test_insights.py`) | 10 configurações, 54 combinações de pesos, Jaccard médio de 0,6228 e mínimo de 0,3546, GC@5 de 0,2121 a 0,7788, validade das explicações de 100% (iguais ao relatório) |
| Motor de recomendação (matriz, Top 5, `explain`, `compare`) sobre uma base de teste com o mesmo formato (66 registros, 14 colunas) | Funcionamento correto; verificação de código, sem relação com os resultados do relatório |
| Geração das figuras e dos diagramas | Concluída |

## Ajustes feitos na revisão
- Correção do caminho de importação do algoritmo no backend.
- Correção da leitura da aba Ablacao, cujo cabeçalho era lido como dado e afetaria as telas Início e Insights.
- Localização automática da base: qualquer `.xlsx` em `backend/data/` que tenha a aba `Base_Jogos`.
- Aviso na interface quando a base não é carregada, e script de diagnóstico `scripts/check_setup.py`.

## Como executar
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
pytest -v
uvicorn app.main:app --reload --app-dir backend
cd frontend && npm install && npm run build
```
O arquivo `.github/workflows/ci.yml` executa os testes do backend e a compilação do frontend a cada push.
