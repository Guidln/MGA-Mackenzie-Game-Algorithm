# Canvas do Projeto – MGA (Mackenzie Game Algorithm)

> Estrutura de Canvas proposta pelo grupo. Nenhum modelo institucional de Canvas foi anexado ao projeto; se a disciplina fornecer um, os campos abaixo podem ser transferidos para ele.

| Campo | Conteúdo |
|---|---|
| **Nome do projeto** | MGA – Mackenzie Game Algorithm (plataforma de demonstração: MGA Discovery) |
| **Equipe** | Bruna Graciano; Guilherme Marques Gomes dos Santos; Guilherme Barros Toledo Batista; Lincoln Cavalcanti Bertoldo Alves. Universidade Presbiteriana Mackenzie, Projeto Aplicado III. |
| **Problema identificado** | O volume de jogos disponíveis dificulta a escolha de novos títulos apenas por listas genéricas, rankings ou popularidade. |
| **Justificativa** | Sistemas de recomendação fazem parte de serviços digitais atuais, e entender seus princípios contribui para a formação em análise de dados. O projeto permite discutir qualidade dos dados, escolha de atributos, escalas, concentração das recomendações e ausência de dados de preferência. |
| **Objetivo geral** | Desenvolver um sistema de recomendação de jogos digitais baseado em conteúdo que identifique e ordene títulos semelhantes a partir dos atributos da base do projeto. |
| **Objetivos específicos** | Organizar e padronizar os dados; analisar exploratoriamente as variáveis; representar os jogos por atributos; aplicar normalização, ponderação e similaridade de cosseno; gerar recomendações item a item com explicação; reavaliar o modelo; documentar a metodologia; apresentar os resultados em interface demonstrativa. |
| **Público-alvo** | Estudantes e pessoas interessadas em jogos digitais e tecnologia (objetivo extensionista). |
| **Proposta de valor** | Recomendações de jogos acompanhadas de explicação por atributos observáveis, em linguagem acessível, que mostram como funciona um recomendador. |
| **Solução proposta** | Recomendador por Content-Based Filtering com similaridade de cosseno, exposto por uma API (FastAPI) e por uma interface web (React). |
| **Metodologia** | Pesquisa aplicada, quantitativa, experimental computacional e iterativa: baseline (Etapa 2), diagnóstico, ajustes incrementais, ablação, sensibilidade e estabilidade (Etapa 3). Ver `docs/metodologia.md`. |
| **Repositório do projeto** | <https://github.com/Guidln/MGA-Mackenzie-Game-Algorithm> |
| **Recursos necessários** | Base de jogos (planilha do projeto), computador com Python 3.11 ou superior e Node.js, repositório GitHub. |
| **Tecnologias utilizadas** | Python, pandas, NumPy, scikit-learn, OpenPyXL, FastAPI, Pydantic, Uvicorn; React, TypeScript, Vite, Tailwind CSS, Framer Motion, Recharts, Lucide React; Docker. |
| **Principais atividades** | Escolha e tratamento da base; análise exploratória; engenharia de atributos; ponderação; avaliação; desenvolvimento da API e da interface; documentação. |
| **Parceiros e envolvidos** | Não há parceiros externos documentados. |
| **Resultados esperados** | Recomendações coerentes e explicáveis; documentação reprodutível; demonstração educativa. |
| **Resultados alcançados** | Matriz 66 × 34; coerência de gênero@5 de 0,333 (baseline) para 0,503; coerência de plataforma@5 de 0,876 para 0,867; cobertura de 100%; Gini de 0,303 para 0,275; diversidade intralista de 0,501 para 0,519; validade das explicações de 27,8% para 100% (990 de 990); 54 combinações de pesos com Jaccard@5 médio de 0,62; Jaccard médio de 0,69 com ruído (σ = 0,05). São indicadores de coerência, cobertura, diversidade e estabilidade, não de acurácia ou satisfação. |
| **Aplicação na comunidade** | Demonstração educativa do MGA e conteúdo sobre sistemas de recomendação e uso responsável de dados, em formato aberto a estudantes e ao público interessado em jogos e tecnologia (objetivo extensionista descrito na seção 1.4 do relatório). |
| **Impacto educacional** | Esperado: aproximar estudantes de conceitos de recomendação, explicabilidade e uso responsável de dados. |
| **ODS relacionados** | ODS 4, Educação de Qualidade (meta 4.4). ODS 9, Indústria, Inovação e Infraestrutura (meta 9.5). |
| **Indicadores de avaliação** | Consistência técnica; coerência de gênero@5 e de plataforma@5; cobertura; Gini e máximo de listas; diversidade intralista; Jaccard@5; validade das explicações. Para a ação comunitária, a definir pelo grupo (por exemplo, número de participantes e retorno coletado). |
| **Limitações** | Base de 66 jogos com viés de seleção; um gênero por jogo; rótulos de plataforma ambíguos; sensibilidade aos pesos; ausência de julgamentos de relevância; sem personalização. |
| **Trabalhos futuros** | Ampliar o catálogo; enriquecer atributos; TF-IDF em descrições; coletar julgamentos de relevância; validar pesos; Precision@K, Recall@K e NDCG@K; avaliação com usuários; abordagens híbridas; evolução da interface. |
