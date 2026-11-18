import { useState } from 'react'
import GamePicker from '../components/GamePicker'
import Cover from '../components/Cover'
import { api } from '../services/api'
import type { Compare, Game } from '../types'

const nome = (a: string) => a.replace(/_/g, ' ')
const v = (x: number | null) => (x == null ? '—' : x.toLocaleString('pt-BR', { maximumFractionDigits: 2 }))
const lista = (l: string[]) => (l.length ? l.join(', ') : 'nenhum')

export default function Versus() {
  const [a, setA] = useState<Game | null>(null); const [b, setB] = useState<Game | null>(null)
  const [c, setC] = useState<Compare | null>(null); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const go = async () => {
    if (!a || !b) return
    setBusy(true); setErr('')
    try { setC(await api.compare(a.id, b.id)) } catch (e) { setErr((e as Error).message); setC(null) } finally { setBusy(false) }
  }
  return (
    <div>
      <h1 className="text-2xl font-semibold">MGA Versus</h1>
      <p className="muted mt-1 text-sm">Compare dois jogos pelos atributos usados no modelo e veja a similaridade calculada pelo MGA.</p>
      <div className="mt-5 grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-end">
        <GamePicker label="Jogo A" value={a} onPick={setA} /><GamePicker label="Jogo B" value={b} onPick={setB} />
        <button className="btn btn-red h-10" disabled={!a || !b || busy} onClick={go}>Comparar</button>
      </div>
      {err && <p className="mt-4 text-sm text-red-400">{err}</p>}
      {c && (
        <div className="mt-8 space-y-6">
          <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
            {[c.jogo_a, c.jogo_b].map((g, i) => (
              <div key={g.id} className={`card flex items-center gap-3 p-3 ${i ? 'order-3' : ''}`}>
                <Cover game={g} className="h-24 w-[72px] shrink-0 rounded-lg" />
                <div><p className="font-semibold">{g.jogo}</p><p className="muted text-sm">{g.ano} · {g.genero}</p><p className="muted text-sm">{g.plataforma}</p></div>
              </div>))}
            <div className="order-2 text-center"><p className="text-2xl font-semibold text-gold">{c.similaridade.toFixed(4).replace('.', ',')}</p>
              <p className="muted text-xs">similaridade de cosseno<br />B é o {c.posicao_de_b_no_ranking_de_a}º no ranking de A</p></div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="card p-4 text-sm"><h3 className="mb-2 font-medium">Em comum</h3>
              <p>Gêneros: {lista(c.generos_em_comum)}</p><p>Plataformas: {lista(c.plataformas_em_comum)}</p>
              <p>País de maior venda: {c.mesmo_pais ? c.pais_a : 'diferente'}</p></div>
            <div className="card p-4 text-sm"><h3 className="mb-2 font-medium">Diferenças</h3>
              <p>Gêneros só em A: {lista(c.generos_so_a)} · só em B: {lista(c.generos_so_b)}</p>
              <p>Plataformas só em A: {lista(c.plataformas_so_a)} · só em B: {lista(c.plataformas_so_b)}</p>
              {!c.mesmo_pais && <p>País: {c.pais_a} × {c.pais_b}</p>}</div>
          </div>
          <div className="card overflow-x-auto p-4 text-sm"><h3 className="mb-2 font-medium">Atributos numéricos</h3>
            <table className="w-full text-left"><thead className="muted text-xs"><tr><th className="font-normal">Atributo</th><th className="font-normal">{c.jogo_a.jogo}</th><th className="font-normal">{c.jogo_b.jogo}</th></tr></thead>
              <tbody>{c.numericos.map(n => <tr key={n.atributo} className="border-t border-line"><td className="py-1">{nome(n.atributo)}</td><td>{v(n.jogo_a)}</td><td>{v(n.jogo_b)}</td></tr>)}</tbody></table>
            <p className="muted mt-2 text-xs">“—” indica valor ausente na base (não é zero).</p></div>
          <div className="card p-4 text-sm"><h3 className="mb-2 font-medium">Atributos apontados pela explain()</h3>
            <p>{[...c.explicacao.compartilhados.map(x => `${x.bloco}: ${x.valor}`), ...c.explicacao.numericos_proximos.map(x => nome(x.atributo))].join(' · ') || 'Nenhum atributo apontado.'}</p>
            <p className="muted mt-2 text-xs">{c.explicacao.nota}</p></div>
        </div>
      )}
    </div>
  )
}
