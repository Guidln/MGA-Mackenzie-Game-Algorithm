import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import type { Config } from '../types'

const RED = '#8B1A14', GOLD = '#D4A017', GRAY = '#3a3a3a'
const rot = (c: string) => c.split(' ')[0] === 'Baseline' ? 'Base' : c.split(' ')[0] === 'F' ? 'Final' : c.split(' ')[0]
const cor = (c: string) => c.startsWith('Baseline') ? GRAY : c.startsWith('F ') ? RED : c.startsWith('V') ? '#6b6b6b' : GOLD

function Chart({ title, text, data, k, pct, dom }: { title: string; text: string; data: Config[]; k: keyof Config; pct?: boolean; dom?: [number, number] }) {
  const d = data.map(c => ({ n: rot(c.configuracao), full: c.configuracao, v: Number(c[k]), c: c.configuracao }))
  return (
    <div className="card p-4">
      <h3 className="font-medium">{title}</h3><p className="muted mb-3 mt-1 text-sm">{text}</p>
      <div className="h-52"><ResponsiveContainer>
        <BarChart data={d} margin={{ left: -10, right: 4 }}><CartesianGrid stroke="#2a2a2a" vertical={false} />
          <XAxis dataKey="n" tick={{ fill: '#aaa', fontSize: 11 }} /><YAxis tick={{ fill: '#aaa', fontSize: 11 }} domain={dom ?? [0, 'auto']} tickFormatter={x => pct ? `${x * 100}%` : x} />
          <Tooltip contentStyle={{ background: '#171717', border: '1px solid #2a2a2a', fontSize: 12 }} labelFormatter={(_: unknown, p: any) => p?.[0]?.payload?.full ?? ''}
            formatter={(x: unknown) => [pct ? `${(Number(x) * 100).toFixed(1)}%` : Number(x).toFixed(3), title]} />
          <Bar dataKey="v" radius={[4, 4, 0, 0]}>{d.map((e, i) => <Cell key={i} fill={cor(e.c)} />)}</Bar>
        </BarChart></ResponsiveContainer></div>
    </div>
  )
}

const num = (x: number) => x.toFixed(3).replace('.', ',')

export default function Insights() {
  const ins = useAsync(api.insights); const sen = useAsync(api.sensitivity)
  if (ins.error) return <p className="text-sm text-red-400">{ins.error}</p>
  if (!ins.data) return <p className="muted text-sm">Carregando…</p>
  const { baseline: b, final: f, ablacao, consistencia, resumo_sensibilidade: rs } = ins.data
  const hist = (() => {
    if (!sen.data) return []
    const bins = Array.from({ length: 12 }, (_, i) => ({ de: 0.3 + i * 0.06, n: 0 }))
    sen.data.configuracoes.forEach(c => { const i = Math.min(11, Math.max(0, Math.floor((c.jaccard - 0.3) / 0.06))); bins[i].n++ })
    return bins.map(x => ({ faixa: x.de.toFixed(2), n: x.n }))
  })()
  const comp: [string, string, number, number][] = [
    ['Coerência de gênero@5', 'Proporção de itens recomendados que compartilham ao menos um gênero com o jogo de referência.', b.coerencia_genero, f.coerencia_genero],
    ['Coerência de plataforma@5', 'Proporção de itens que compartilham ao menos uma família de plataforma.', b.coerencia_plataforma, f.coerencia_plataforma],
    ['Cobertura', 'Parcela do catálogo que aparece em ao menos uma lista Top-5.', b.cobertura, f.cobertura],
    ['Gini', 'Concentração das recomendações em poucos jogos. Menor é melhor.', b.gini, f.gini],
    ['Diversidade intralista', '1 menos a similaridade média dentro de cada lista. Maior significa listas menos redundantes.', b.diversidade, f.diversidade],
  ]
  return (
    <div className="space-y-10">
      <div><h1 className="text-2xl font-semibold">MGA Insights</h1>
        <p className="muted mt-1 text-sm">Resultados da Etapa 3 (66 consultas, N = 5). São indicadores de coerência, cobertura, diversidade e estabilidade; não comprovam acurácia preditiva nem satisfação de usuários.</p></div>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[[ins.data.total_jogos ?? 66, 'jogos'], [ins.data.total_atributos ?? 34, 'atributos'], [(ins.data.matriz ?? [66, 34]).join(' × '), 'dimensão da matriz'],
          [`${(consistencia['Validade das explicações — final'] as number) * 100}%`, 'validade das explicações']].map(([v, l]) =>
          <div key={l as string} className="card p-4"><p className="text-2xl font-semibold">{v}</p><p className="muted text-sm">{l}</p></div>)}
      </section>

      <section><h2 className="mb-3 text-lg font-semibold">Baseline versus modelo final</h2>
        <div className="card overflow-x-auto p-4"><table className="w-full text-left text-sm">
          <thead className="muted text-xs"><tr><th className="font-normal">Indicador</th><th className="font-normal">Baseline</th><th className="font-normal">Final</th><th className="font-normal">O que mede</th></tr></thead>
          <tbody>{comp.map(([n, t, x, y]) => <tr key={n} className="border-t border-line align-top"><td className="py-2 pr-3">{n}</td><td className="pr-3">{num(x)}</td><td className="pr-3 text-gold">{num(y)}</td><td className="muted">{t}</td></tr>)}
            <tr className="border-t border-line align-top"><td className="py-2 pr-3">Validade das explicações</td><td>{((consistencia['Validade das explicações — baseline'] as number) * 100).toFixed(1)}%</td><td className="text-gold">100%</td><td className="muted pl-3">Atributos listados que de fato são compartilhados (990 de 990 no modelo final).</td></tr></tbody></table></div></section>

      <section><h2 className="mb-3 text-lg font-semibold">Gráficos por configuração do pipeline</h2>
        <p className="muted mb-4 text-sm">Base = Etapa 2; E1 a E5 = ajustes incrementais; Final = pesos por bloco; V1 a V3 = variantes (sem HLTB, sem ano, com diretor).</p>
        <div className="grid gap-4 md:grid-cols-2">
          <Chart title="Coerência de gênero@5" text="O ganho principal aparece com a ponderação por bloco, que dá mais peso ao gênero. O indicador favorece modelos que priorizam gênero." data={ablacao} k="coerencia_genero" />
          <Chart title="Coerência de plataforma@5" text="Pequena queda do baseline (0,876) para o final (0,867)." data={ablacao} k="coerencia_plataforma" dom={[0, 1]} />
          <Chart title="Gini das recomendações" text="Quanto menor, menos o Top-5 se concentra em poucos jogos." data={ablacao} k="gini" />
          <Chart title="Cobertura do catálogo" text="O modelo final volta a recomendar todos os 66 jogos ao menos uma vez." data={ablacao} k="cobertura" pct dom={[0.9, 1]} />
          <Chart title="Diversidade intralista" text="Maior valor indica listas menos redundantes entre si." data={ablacao} k="diversidade" />
          <div className="card p-4"><h3 className="font-medium">Sensibilidade dos pesos</h3>
            <p className="muted mb-3 mt-1 text-sm">Sobreposição (Jaccard@5) entre o modelo final e {rs.n} combinações de pesos. Média {num(rs.jaccard_medio)}, mínimo {num(rs.jaccard_minimo)}; GC@5 entre {num(rs.gc5_minimo)} e {num(rs.gc5_maximo)}.</p>
            <div className="h-52"><ResponsiveContainer><BarChart data={hist} margin={{ left: -10 }}><CartesianGrid stroke="#2a2a2a" vertical={false} />
              <XAxis dataKey="faixa" tick={{ fill: '#aaa', fontSize: 11 }} /><YAxis allowDecimals={false} tick={{ fill: '#aaa', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#171717', border: '1px solid #2a2a2a', fontSize: 12 }} formatter={(x: unknown) => [String(x), 'configurações']} labelFormatter={(l: unknown) => `Jaccard a partir de ${l}`} />
              <Bar dataKey="n" fill={RED} radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div></div>
        </div>
        <p className="muted mt-3 text-xs">Fonte: {ins.data.fonte}.</p></section>

      <section><h2 className="mb-3 text-lg font-semibold">Limitações do modelo</h2>
        <ul className="card list-disc space-y-2 p-5 pl-8 text-sm">
          <li>A base tem 66 jogos indicados ao Game of the Year; não representa o mercado e limita a diversidade das listas.</li>
          <li>Cada jogo tem um único gênero na base original, e muitos gêneros aparecem uma só vez.</li>
          <li>Os rótulos de plataforma “Consoles” e “Multi” são ambíguos; o mapeamento adotado é uma hipótese documentada.</li>
          <li>Não há julgamentos de relevância; por isso não se calculam Precision@K, Recall@K nem NDCG@K.</li>
          <li>Os pesos foram definidos a priori e as listas são sensíveis a eles (Jaccard médio de {num(rs.jaccard_medio)} nas combinações testadas).</li>
          <li>Com ruído gaussiano (σ = 0,05) o Jaccard médio foi {num(Number(consistencia['Jaccard@5 com ruído (média)']))}; as últimas posições do Top-5 são as mais instáveis.</li>
        </ul></section>
    </div>
  )
}
