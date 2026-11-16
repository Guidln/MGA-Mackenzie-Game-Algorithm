export interface Game {
  id: number; jogo: string; ano: number; diretor: string | null
  quantidade_premios: number | null; vendas_milhoes: number | null; pais_maior_vendas: string | null
  plataforma: string; genero: string; jogadores_concluiram_hltb: number | null
  nota_publico_metacritic: number | null; nota_critica_metacritic: number | null; cover_url: string | null
}
export interface Recommendation { posicao: number; similaridade: number; jogo: Game }
export interface RecResponse { referencia: Game; k: number; recomendacoes: Recommendation[]; aviso: string }
export interface Explanation {
  referencia: Game; recomendado: Game; similaridade: number
  compartilhados: { atributo: string; bloco: string; valor: string }[]
  numericos_proximos: { atributo: string; valor_referencia: number | null; valor_recomendado: number | null }[]
  nota: string
}
export interface Compare {
  jogo_a: Game; jogo_b: Game; similaridade: number; posicao_de_b_no_ranking_de_a: number
  generos_em_comum: string[]; generos_so_a: string[]; generos_so_b: string[]
  plataformas_em_comum: string[]; plataformas_so_a: string[]; plataformas_so_b: string[]
  mesmo_pais: boolean; pais_a: string; pais_b: string
  numericos: { atributo: string; jogo_a: number | null; jogo_b: number | null }[]
  explicacao: Explanation
}
export interface Config {
  configuracao: string; n_atributos: number; coerencia_genero: number; coerencia_plataforma: number
  cobertura: number; max_listas: number; gini: number; escore_medio: number; dif_ano: number
  diversidade: number; jaccard_vs_baseline: number
}
export interface Insights {
  total_jogos: number | null; total_atributos: number | null; matriz: number[] | null
  baseline: Config; final: Config; ablacao: Config[]; consistencia: Record<string, string | number>
  resumo_sensibilidade: { n: number; jaccard_medio: number; jaccard_minimo: number; gc5_minimo: number; gc5_maximo: number }
  fonte: string
}
export interface Sensitivity {
  resumo: Insights['resumo_sensibilidade']
  configuracoes: { peso_genero: number; peso_plataforma: number; peso_numerico: number; peso_pais: number; jaccard: number; coerencia_genero: number }[]
}
