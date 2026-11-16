import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import Cover from '../components/Cover'
import GamePicker from '../components/GamePicker'
import { api } from '../services/api'
import type { Explanation, Game, RecResponse } from '../types'

const nome = (a: string) => a.replace(/_/g, ' ')
const val = (v: number | null) => (v == null ? '—' : v.toLocaleString('pt-BR', { maximumFractionDigits: 1 }))

function Why({ ex }: { ex: Explanation }) {
  const r = ex.referencia, c = ex.recomendado
  return (
    <div className="mt-4 rounded-xl border border-line bg-ink p-4 text-sm">
      <p className="font-medium">Por que {c.jogo}?</p>
      <p className="muted mt-1 text-xs">Similaridade de cosseno: {ex.similaridade.toFixed(4).replace('.', ',')}</p>
      <h4 className="mt-4 text-xs uppercase tracking-wide text-gold">Atributos categóricos compartilhados</h4>
      {ex.compartilhados.length === 0 ? <p className="muted mt-1">Nenhum atributo categórico compartilhado entre os dois jogos.</p> :
        <ul className="mt-2 flex flex-wrap gap-2">{ex.compartilhados.map(a => <li key={a.atributo} className="rounded-lg bg-mga/30 px-2 py-1">{a.bloco}: {a.valor}</li>)}</ul>}
      <h4 className="mt-4 text-xs uppercase tracking-wide text-gold">Atributos numéricos próximos</h4>
      {ex.numericos_proximos.length === 0 ? <p className="muted mt-1">Nenhum atributo numérico dentro da tolerância de 0,5 desvio-padrão.</p> :
        <table className="mt-2 w-full text-left"><thead className="muted text-xs"><tr><th className="font-normal">Atributo</th><th className="font-normal">{r.jogo}</th><th className="font-normal">{c.jogo}</th></tr></thead>
          <tbody>{ex.numericos_proximos.map(n => <tr key={n.atributo} className="border-t border-line"><td className="py-1">{nome(n.atributo)}</td><td>{val(n.valor_referencia)}</td><td>{val(n.valor_recomendado)}</td></tr>)}</tbody></table>}
      <p className="muted mt-4 text-xs">{ex.nota}</p>
    </div>
  )
}

export default function Recommendations() {
  const [params, setParams] = useSearchParams()
  const [sel, setSel] = useState<Game | null>(null); const [res, setRes] = useState<RecResponse | null>(null)
  const [busy, setBusy] = useState(false); const [err, setErr] = useState('')
  const [open, setOpen] = useState<number | null>(null); const [ex, setEx] = useState<Record<number, Explanation>>({})

  const run = async (id: number) => {
    setBusy(true); setErr(''); setOpen(null); setEx({})
    try { setRes(await api.recommend(id)) } catch (e) { setErr((e as Error).message); setRes(null) } finally { setBusy(false) }
  }
  useEffect(() => {
    const id = params.get('id')
    if (id) { api.games().then(g => { const f = g.find(x => x.id === Number(id)); if (f) { setSel(f); run(f.id) } }).catch(e => setErr(e.message)) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  const toggle = async (id: number) => {
    if (open === id) return setOpen(null)
    setOpen(id)
    if (!ex[id] && res) try { const e = await api.explain(res.referencia.id, id); setEx(p => ({ ...p, [id]: e })) } catch (e) { setErr((e as Error).message) }
  }
  return (
    <div>
      <h1 className="text-2xl font-semibold">Recomendações MGA</h1>
      <p className="muted mt-1 text-sm">Escolha um jogo de referência para receber os cinco títulos mais próximos no espaço de atributos.</p>
      <div className="mt-5 flex max-w-xl flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1"><GamePicker label="Jogo de referência" value={sel} onPick={g => { setSel(g); setParams({ id: String(g.id) }) }} /></div>
        <button className="btn btn-red h-10" disabled={!sel || busy} onClick={() => sel && run(sel.id)}>{busy ? 'Calculando…' : 'Recomendar'}</button>
      </div>
      {err && <p className="mt-4 text-sm text-red-400">{err}</p>}
      {res && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-8">
          <div className="card flex items-center gap-4 p-4">
            <Cover game={res.referencia} className="h-24 w-[72px] shrink-0 rounded-lg" />
            <div><p className="muted text-xs">Referência</p><p className="font-semibold">{res.referencia.jogo}</p>
              <p className="muted text-sm">{res.referencia.ano} · {res.referencia.genero} · {res.referencia.plataforma}</p></div>
          </div>
          <ol className="mt-5 space-y-3">
            {res.recomendacoes.map(r => (
              <li key={r.jogo.id} className="card p-4">
                <div className="flex items-center gap-4">
                  <span className="w-6 text-center text-lg font-semibold text-gold">{r.posicao}</span>
                  <Cover game={r.jogo} className="h-20 w-[60px] shrink-0 rounded-lg" />
                  <div className="min-w-0 flex-1"><p className="truncate font-medium">{r.jogo.jogo}</p>
                    <p className="muted truncate text-sm">{r.jogo.ano} · {r.jogo.genero} · {r.jogo.plataforma}</p></div>
                  <div className="text-right"><p className="text-xl font-semibold">{r.similaridade.toFixed(4).replace('.', ',')}</p><p className="muted text-xs">similaridade MGA</p></div>
                </div>
                <button className="btn btn-ghost mt-3" onClick={() => toggle(r.jogo.id)}>{open === r.jogo.id ? 'Ocultar explicação' : 'Por que este jogo?'}</button>
                {open === r.jogo.id && (ex[r.jogo.id] ? <Why ex={ex[r.jogo.id]} /> : <p className="muted mt-3 text-sm">Carregando…</p>)}
              </li>))}
          </ol>
          <p className="muted mt-4 text-xs">{res.aviso}</p>
        </motion.div>
      )}
    </div>
  )
}
