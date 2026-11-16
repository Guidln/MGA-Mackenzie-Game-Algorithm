import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import GamePicker from '../components/GamePicker'
import GameCard from '../components/GameCard'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import type { Game } from '../types'

const steps = [
  ['Atributos', 'Gênero, plataforma, país e indicadores numéricos de cada jogo viram um vetor de 34 posições.'],
  ['Pesos', 'Cada bloco recebe um peso definido antes da avaliação: gênero 2,0; numérico 1,0; plataforma e país 0,5.'],
  ['Cosseno', 'A similaridade de cosseno compara o vetor do jogo escolhido com o dos demais títulos.'],
  ['Explicação', 'Cada recomendação lista os atributos que os dois jogos de fato compartilham ou têm próximos.'],
]

export default function Home() {
  const nav = useNavigate(); const [sel, setSel] = useState<Game | null>(null)
  const games = useAsync(api.games); const ins = useAsync(api.insights)
  const featured = [...(games.data ?? [])].sort((a, b) => (b.nota_critica_metacritic ?? 0) - (a.nota_critica_metacritic ?? 0)).slice(0, 6)
  const go = () => nav(sel ? `/recomendacoes?id=${sel.id}` : '/recomendacoes')
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-16">
      <section className="py-10">
        <p className="mb-3 text-sm text-gold">Sistema de recomendação baseado em conteúdo</p>
        <h1 className="max-w-2xl text-4xl font-bold leading-tight md:text-5xl">Descubra seu próximo jogo</h1>
        <p className="muted mt-4 max-w-xl">Escolha um título do catálogo do The Game Awards (2014–2024) e veja cinco jogos parecidos, com a explicação de cada escolha.</p>
        <div className="mt-8 flex max-w-xl flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1"><GamePicker label="Jogo de referência" value={sel} onPick={setSel} /></div>
          <button className="btn btn-red h-10" onClick={go}>Começar descoberta <ArrowRight size={16} /></button>
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Jogos em destaque</h2>
        <p className="muted mb-4 text-sm">Seis títulos com as maiores notas da crítica no Metacritic, segundo a base.</p>
        {games.error && <p className="text-sm text-red-400">{games.error}</p>}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {featured.map(g => <GameCard key={g.id} game={g} badge={g.nota_critica_metacritic ? String(g.nota_critica_metacritic) : undefined}
            onClick={() => nav(`/recomendacoes?id=${g.id}`)} />)}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Como o MGA funciona</h2>
        <div className="grid gap-4 md:grid-cols-4">
          {steps.map(([t, d], i) => (
            <div key={t} className="card p-4"><span className="text-xs text-gold">{i + 1}</span><h3 className="mt-1 font-medium">{t}</h3><p className="muted mt-2 text-sm">{d}</p></div>
          ))}
        </div>
      </section>

      {ins.data && (
        <section>
          <h2 className="mb-4 text-xl font-semibold">Indicadores gerais</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[[ins.data.total_jogos ?? '—', 'jogos no catálogo'], [ins.data.total_atributos ?? '—', 'atributos por jogo'],
              [ins.data.final.coerencia_genero.toFixed(3), 'coerência de gênero@5'], [(ins.data.final.cobertura * 100).toFixed(0) + '%', 'cobertura do catálogo']]
              .map(([v, l]) => <div key={l as string} className="card p-4"><p className="text-2xl font-semibold">{v}</p><p className="muted text-sm">{l}</p></div>)}
          </div>
          <p className="muted mt-3 text-xs">Indicadores de coerência, cobertura e estabilidade. Não medem acurácia preditiva nem satisfação de usuários.</p>
        </section>
      )}
    </motion.div>
  )
}
