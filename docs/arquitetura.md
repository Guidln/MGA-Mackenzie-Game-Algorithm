# Arquitetura

Os diagramas abaixo usam Mermaid (renderizado pelo GitHub) e descrevem o que está implementado.

## Componentes
```mermaid
flowchart LR
  U[Navegador] --> F[Frontend React + TypeScript]
  F -->|REST /api| B[FastAPI app.main]
  B --> R[api/routes.py]
  R --> E[services/engine.py]
  R --> I[services/insights.py]
  E --> P[algorithm/mga_pipeline.py\nbuild, sim_matrix, recommend, explain]
  E --> D[(Base_Jogos .xlsx)]
  I --> X[(MGA_Resultados_Etapa3.xlsx)]
```
A matriz X (66 × 34) e a matriz de similaridade S (66 × 66) são calculadas uma vez, na inicialização (`lifespan`). Os endpoints só consultam essas matrizes.

## Sequência: recomendação com explicação
```mermaid
sequenceDiagram
  actor Usuário
  participant F as Frontend
  participant A as API
  participant E as Engine
  participant P as mga_pipeline
  Usuário->>F: pesquisa e escolhe um jogo
  F->>A: GET /api/games/search?q=
  A-->>F: jogos encontrados
  Usuário->>F: Recomendar
  F->>A: POST /api/recommendations {game_id}
  A->>E: recommend(i, 5)
  E->>P: recommend(S, df, nome, 5)
  P-->>E: 5 pares (jogo, cosseno)
  E-->>A: lista com posição e dados
  A-->>F: Top 5
  Usuário->>F: Por que este jogo?
  F->>A: POST /api/explanations
  A->>E: explain(i, j)
  E->>P: explain(X, df, i, j)
  P-->>E: atributos
  E-->>F: compartilhados + numéricos próximos
```

## Casos de uso
```mermaid
flowchart LR
  V((Visitante)) --- C1[Explorar catálogo]
  V --- C2[Pesquisar jogo]
  V --- C3[Obter Top 5]
  V --- C4[Ver explicação]
  V --- C5[Comparar dois jogos]
  V --- C6[Consultar indicadores]
  C3 -.inclui.-> C2
  C4 -.estende.-> C3
```

## Fluxo do algoritmo
```mermaid
flowchart TD
  A[Base_Jogos] --> B[Tratamento e remoção de colunas sem uso]
  B --> C[Numéricos: log1p, mediana, z-score, indicadores de ausência]
  B --> D[Gênero: taxonomia + multi-hot]
  B --> E[Plataforma: famílias + multi-hot]
  B --> F[País: one-hot]
  C & D & E & F --> G[Peso do bloco / raiz do nº de colunas]
  G --> H[Matriz 66 × 34]
  H --> I[Cosseno 66 × 66]
  I --> J[Remove o próprio jogo, ordena, Top-N]
  J --> K[explain: compartilhados + numéricos próximos]
```

## Modelo de dados (catálogo)
```mermaid
erDiagram
  JOGO {
    int id
    string jogo
    int ano
    string diretor
    int quantidade_premios
    float vendas_milhoes
    string pais_maior_vendas
    string plataforma
    string genero
    int jogadores_concluiram_hltb
    float nota_publico_metacritic
    int nota_critica_metacritic
  }
```
O `id` é a posição da linha na aba `Base_Jogos`. A coluna `cover_url` é opcional e vem de `backend/data/covers.json`.

## Endpoints
| Método | Rota | Função |
|---|---|---|
| GET | /api/health | Estado da API e da base |
| GET | /api/games | Catálogo completo |
| GET | /api/games/search?q= | Busca por nome |
| GET | /api/games/{id} | Um jogo |
| POST | /api/recommendations | Top-k de um jogo (k de 1 a 10, padrão 5) |
| POST | /api/explanations | `explain()` para um par de jogos |
| POST | /api/compare | Comparação de dois jogos |
| GET | /api/insights | Indicadores (lidos da planilha de resultados) |
| GET | /api/insights/sensitivity | 54 combinações de pesos |

A documentação Swagger fica em `/docs`. Erros: 404 (jogo inexistente), 422 (validação), 503 (base ou planilha ausente).
