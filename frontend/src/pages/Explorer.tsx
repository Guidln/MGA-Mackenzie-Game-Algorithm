import { Fragment, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'
import GameCard from '../components/GameCard'
import Cover from '../components/Cover'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import type { Game } from '../types'

const fmt = (v: number | null, d = 0) => (v == null ? 'não informado' : v.toLocaleString('pt-BR', { maximumFractionDigits: d }))

export default function Explorer() {
  const nav = useNavigate(); const { data, error, loading } = useAsync(api.games)
  const [q, setQ] = useState(''); const [gen, setGen] = useState(''); const [plat, setPlat] = useState(''); const [ano, setAno] = useState('')
  const [ord, setOrd] = useState('nome'); const [sel, setSel] = useState<Game | null>(null)
  const games = data ?? []
  const opt = useMemo(() => ({
    gen: [...new Set(games.map(g => g.genero))].sort(),
    plat: [...new Set(games.flatMap(g => g.plataforma.split(' / ')))].sort(),
    ano: [...new Set(games.map(g => g.ano))].sort(),
  }), [games])
  const list = useMemo(() => {
    const r = games.filter(g => g.jogo.toLowerCase().includes(q.toLowerCase()) && (!gen || g.genero === gen)
      && (!plat || g.plataforma.split(' / ').includes(plat)) && (!ano || g.ano === Number(ano)))
    const key: Record<string, (a: Game, b: Game) => number> = {
      nome: (a, b) => a.jogo.localeCompare(b.jogo), ano: (a, b) => b.ano - a.ano,
      critica: (a, b) => (b.nota_critica_metacritic ?? 0) - (a.nota_critica_metacritic ?? 0),
      vendas: (a, b) => (b.vendas_milhoes ?? 0) - (a.vendas_milhoes ?? 0),
    }
    return r.sort(key[ord])
  }, [games, q, gen, plat, ano, ord])
  return (
    <div>
      <h1 className="text-2xl font-semibold">Catálogo</h1>
      <p className="muted mt-1 text-sm">{loading ? 'Carregando…' : `${list.length} de ${games.length} jogos`}</p>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <input className="input" placeholder="Nome do jogo" value={q} onChange={e => setQ(e.target.value)} />
        <select className="input" value={gen} onChange={e => setGen(e.target.value)}><option value="">Todos os gêneros</option>{opt.gen.map(x => <option key={x}>{x}</option>)}</select>
        <select className="input" value={plat} onChange={e => setPlat(e.target.value)}><option value="">Todas as plataformas</option>{opt.plat.map(x => <option key={x}>{x}</option>)}</select>
        <select className="input" value={ano} onChange={e => setAno(e.target.value)}><option value="">Todos os anos</option>{opt.ano.map(x => <option key={x}>{x}</option>)}</select>
        <select className="input" value={ord} onChange={e => setOrd(e.target.value)}>
          <option value="nome">Ordenar: nome</option><option value="ano">Ordenar: ano (recente)</option>
          <option value="critica">Ordenar: nota da crítica</option><option value="vendas">Ordenar: vendas</option></select>
      </div>
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {list.map(g => <GameCard key={g.id} game={g} onClick={() => setSel(g)} />)}
      </div>
      {!loading && list.length === 0 && <p className="muted mt-10 text-center text-sm">Nenhum jogo encontrado com esses filtros.</p>}
      {sel && (
        <div className="fixed inset-0 z-40 grid place-items-center bg-black/70 p-4" onClick={() => setSel(null)}>
          <div className="card relative grid max-h-[90vh] w-full max-w-2xl gap-5 overflow-auto p-5 sm:grid-cols-[180px_1fr]" onClick={e => e.stopPropagation()}>
            <button className="absolute right-3 top-3" aria-label="Fechar" onClick={() => setSel(null)}><X size={18} /></button>
            <Cover game={sel} className="aspect-[3/4] w-full rounded-xl" />
            <div>
              <h2 className="text-xl font-semibold">{sel.jogo}</h2>
              <dl className="mt-3 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
                {([['Ano', sel.ano], ['Gênero', sel.genero], ['Plataforma', sel.plataforma], ['Diretor', sel.diretor ?? 'não informado'],
                  ['Prêmios', fmt(sel.quantidade_premios)], ['Vendas (milhões)', fmt(sel.vendas_milhoes, 1)], ['País de maior venda', sel.pais_maior_vendas ?? '—'],
                  ['Concluíram (HLTB)', fmt(sel.jogadores_concluiram_hltb)], ['Metacritic crítica', fmt(sel.nota_critica_metacritic)], ['Metacritic público', fmt(sel.nota_publico_metacritic, 1)]] as [string, string | number][])
                  .map(([k, v]) => <Fragment key={k}><dt className="muted">{k}</dt><dd>{v}</dd></Fragment>)}
              </dl>
              <button className="btn btn-red mt-5" onClick={() => nav(`/recomendacoes?id=${sel.id}`)}>Ver recomendações</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
