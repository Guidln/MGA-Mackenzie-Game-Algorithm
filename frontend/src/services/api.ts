import type { CommunityInfo, Compare, SurveyPayload, SurveySummary, Explanation, Game, Insights, RecResponse, Sensitivity } from '../types'

const BASE = import.meta.env.VITE_API_URL ?? '/api'

async function req<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(BASE + path, body === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error(typeof d.detail === 'string' ? d.detail : `Erro ${r.status}`)
  }
  return r.json()
}

export const api = {
  games: () => req<Game[]>('/games'),
  search: (q: string) => req<Game[]>(`/games/search?q=${encodeURIComponent(q)}`),
  recommend: (game_id: number, modo: 'mga' | 'hibrido' = 'hibrido') => req<RecResponse>('/recommendations', { game_id, k: 5, modo }),
  community: () => req<CommunityInfo>('/community'),
  explain: (reference_id: number, recommended_id: number) => req<Explanation>('/explanations', { reference_id, recommended_id }),
  compare: (game_a: number, game_b: number) => req<Compare>('/compare', { game_a, game_b }),
  insights: () => req<Insights>('/insights'),
  sensitivity: () => req<Sensitivity>('/insights/sensitivity'),
}

const adminHeaders = (token: string): Record<string, string> => (token ? { 'X-Admin-Token': token } : {})
export const survey = {
  submit: (body: SurveyPayload) => req<{ id: number; mensagem: string }>('/survey', body),
  summary: async (token: string): Promise<SurveySummary> => {
    const r = await fetch(BASE + '/survey/summary', { headers: adminHeaders(token) })
    if (r.status === 401) throw new Error('401')
    if (!r.ok) throw new Error(`Erro ${r.status}`)
    return r.json()
  },
  draft: (sid: string, payload: unknown) => fetch(BASE + '/survey/draft/' + sid, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ payload }) }).then(r => { if (!r.ok) throw new Error(String(r.status)) }),
  csv: async (token: string) => {
    const r = await fetch(BASE + '/survey/export.csv', { headers: adminHeaders(token) })
    if (!r.ok) throw new Error(`Erro ${r.status}`)
    return r.blob()
  },
  json: async (token: string) => {
    const r = await fetch(BASE + '/survey/export.json', { headers: adminHeaders(token) })
    if (!r.ok) throw new Error(`Erro ${r.status}`)
    return r.blob()
  },
}
