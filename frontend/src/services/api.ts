import type { Compare, Explanation, Game, Insights, RecResponse, Sensitivity } from '../types'

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
  recommend: (game_id: number) => req<RecResponse>('/recommendations', { game_id, k: 5 }),
  explain: (reference_id: number, recommended_id: number) => req<Explanation>('/explanations', { reference_id, recommended_id }),
  compare: (game_a: number, game_b: number) => req<Compare>('/compare', { game_a, game_b }),
  insights: () => req<Insights>('/insights'),
  sensitivity: () => req<Sensitivity>('/insights/sensitivity'),
}
