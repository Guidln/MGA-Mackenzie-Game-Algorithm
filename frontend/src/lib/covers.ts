// Capas dos jogos (fallback no navegador). Ordem: cover_url do servidor (covers.json) → página exata na Wikipédia
// (coverPages.json) → busca na Wikipédia → capa tipográfica. Para deixar TODAS as capas fixas e offline: python scripts/fetch_covers.py
import pages from './coverPages.json'

const KEY = 'mga:covers:v2'
let cache: Record<string, string> = {}
try { cache = JSON.parse(localStorage.getItem(KEY) ?? '{}') } catch { cache = {} }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(cache)) } catch { /* sem storage: ok */ } }
const PAGE = pages as Record<string, string>
const API = 'https://en.wikipedia.org/w/api.php?action=query&format=json&origin=*&prop=pageimages&piprop=thumbnail&pithumbsize=500&redirects=1'

let running = 0
const queue: (() => void)[] = []
const run = <T,>(fn: () => Promise<T>) => new Promise<T>((res, rej) => {
  const go = () => { running++; fn().then(res, rej).finally(() => { running--; queue.shift()?.() }) }
  if (running < 4) go(); else queue.push(go)
})

type Pages = { thumbnail?: { source: string } }
async function thumb(url: string): Promise<string | null> {
  const j = await (await fetch(url)).json()
  const p = Object.values(j?.query?.pages ?? {})[0] as Pages | undefined
  return p?.thumbnail?.source ?? null
}

async function lookup(title: string): Promise<string | null> {
  const t = title.replace(/[’‘]/g, "'")
  return (await thumb(`${API}&titles=${encodeURIComponent(PAGE[title] ?? t)}`))
    ?? (await thumb(`${API}&generator=search&gsrlimit=1&gsrsearch=${encodeURIComponent(t + ' video game')}`))
}

const pending = new Map<string, Promise<string | null>>()
export function coverFor(title: string): Promise<string | null> {
  if (title in cache) return Promise.resolve(cache[title] || null)
  const hit = pending.get(title); if (hit) return hit
  const p = run(() => lookup(title)).then(u => { cache[title] = u ?? ''; save(); return u }).catch(() => null).finally(() => pending.delete(title))
  pending.set(title, p)
  return p
}
