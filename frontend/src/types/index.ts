export interface Game {
  id: number; jogo: string; ano: number; diretor: string | null
  quantidade_premios: number | null; vendas_milhoes: number | null; pais_maior_vendas: string | null
  plataforma: string; genero: string; jogadores_concluiram_hltb: number | null
  nota_publico_metacritic: number | null; nota_critica_metacritic: number | null; cover_url: string | null
}
export interface Comunidade { aprovacao: number | null; avaliacoes_par: number; nota_media: number | null; n_notas: number; jogadores_em_comum: number }
export interface Recommendation { posicao: number; similaridade: number; score_final: number; comunidade: Comunidade | null; jogo: Game }
export interface RecResponse { referencia: Game; k: number; modo: 'mga' | 'hibrido'; peso_comunidade: number; respostas: number; recomendacoes: Recommendation[]; aviso: string }
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

export type RespostaRec = 'quero' | 'gostei' | 'nao'
export interface SurveyPayload {
  nome: string | null; faixa_etaria: string | null; horas_semana: string | null; regiao: string | null; anos_jogando: string | null; gasto_mensal: string | null
  plataformas: string[]; descoberta: string[]; generos: string[]; valores: Record<string, number>; estilo: string | null
  jogos: { game_id: number; nota: number }[]; wishlist: number[]; favorito_id: number | null; extras: string[]
  referencia_id: number | null
  avaliacoes: { referencia_id: number; game_id: number; posicao: number; similaridade: number; resposta: RespostaRec }[]
  nota_geral: number | null; comentario: string | null; sistema: Record<string, string | number | null>; sid: string; consentimento: boolean
}
type Cnt = { nome: string; total: number }[]
export interface SurveySummary {
  total_respostas: number; nota_geral_media: number | null; rascunhos: { total: number; concluidos: number; em_andamento: number }
  mais_jogados: { game_id: number; jogo: string; citacoes: number; nota_media: number }[]
  melhor_avaliados: { game_id: number; jogo: string; citacoes: number; nota_media: number }[]
  recomendacoes: {
    avaliadas: number; aprovacao: number | null
    por_posicao: { posicao: number; avaliacoes: number; aprovacao: number }[]
    pares: { referencia: string; recomendado: string; avaliacoes: number; aprovacao: number; quero: number; gostei: number; nao: number }[]
  }
  sugeridos_pelos_usuarios: { titulo: string; votos: number }[]
  quero_jogar: { jogo: string; votos: number }[]; favoritos: { jogo: string; votos: number }[]
  generos: Cnt; plataformas: Cnt; descoberta: Cnt; regioes: Cnt; gasto: Cnt; anos_jogando: Cnt; faixas: Cnt; horas: Cnt; estilos: Cnt; voltaria: Cnt
  valores_media: { nome: string; media: number | null; n: number }[]
  sistema: { nps: number | null; nps_n: number; clareza: number | null; facilidade: number | null; surpresa: number | null }
  abertas: { data: string; gostou: string; faltou: string }[]
  comentarios: { data: string; nota: number | null; texto: string }[]
}
export interface CommunityInfo {
  respostas: number; peso: number; sugeridos: { titulo: string; votos: number }[]
  populares: { jogo: Game; nota_media: number; notas: number }[]
}
