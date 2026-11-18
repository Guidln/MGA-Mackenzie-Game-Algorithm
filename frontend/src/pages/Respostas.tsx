import { useEffect, useState } from 'react'
import { Download, Lock } from 'lucide-react'
import { survey } from '../services/api'
import type { SurveySummary } from '../types'

const TK = 'mga:admin'
const pct = (v: number | null) => (v == null ? '—' : `${Math.round(v * 100)}%`)
const read = () => { try { return sessionStorage.getItem(TK) ?? '' } catch { return '' } }

function Bar({ label, value, max, text }: { label: string; value: number; max: number; text: string }) {
  return (
    <li className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-3 gap-y-1 text-sm">
      <span className="truncate">{label}</span><span className="muted tabular-nums">{text}</span>
      <span className="col-span-2 h-1.5 overflow-hidden rounded-full bg-white/5"><span className="block h-full rounded-full bg-gold" style={{ width: `${max ? (value / max) * 100 : 0}%` }} /></span>
    </li>
  )
}
const Panel = ({ t, children }: { t: string; children: React.ReactNode }) => <section className="card p-5"><h2 className="mb-4 font-semibold">{t}</h2>{children}</section>
const Empty = () => <p className="muted text-sm">Ainda sem dados.</p>

export default function Respostas() {
  const [token, setToken] = useState(read); const [draft, setDraft] = useState('')
  const [d, setD] = useState<SurveySummary | null>(null); const [locked, setLocked] = useState(false); const [err, setErr] = useState('')
  useEffect(() => {
    setErr(''); setLocked(false)
    survey.summary(token).then(setD).catch(e => e.message === '401' ? (setLocked(true), setD(null)) : setErr(e.message))
  }, [token])
  const unlock = () => { try { sessionStorage.setItem(TK, draft) } catch { /* ok */ } setToken(draft) }
  const dl = async (fn: (t: string) => Promise<Blob>, nome: string) => {
    const url = URL.createObjectURL(await fn(token)); const a = document.createElement('a')
    a.href = url; a.download = nome; a.click(); URL.revokeObjectURL(url)
  }

  if (locked) return (
    <div className="mx-auto max-w-sm py-16 text-center"><Lock className="mx-auto text-gold" />
      <h1 className="mt-4 text-xl font-semibold">Área restrita</h1><p className="muted mt-1 text-sm">Informe o token de administrador (MGA_ADMIN_TOKEN).</p>
      <input type="password" className="input mt-4" value={draft} onChange={e => setDraft(e.target.value)} onKeyDown={e => e.key === 'Enter' && unlock()} aria-label="Token" />
      {token && <p className="mt-2 text-sm text-red-400">Token inválido.</p>}
      <button className="btn btn-red mt-4" onClick={unlock}>Entrar</button></div>)
  if (err) return <p className="text-red-400">{err}</p>
  if (!d) return <div className="space-y-3">{[0, 1, 2].map(i => <div key={i} className="skeleton h-28" />)}</div>

  const r = d.recomendacoes; const maxJ = Math.max(1, ...d.mais_jogados.map(x => x.citacoes))
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div><h1 className="text-2xl font-semibold">Resultados da pesquisa</h1><p className="muted text-sm">Títulos e recomendações extraídos das respostas dos usuários.</p></div>
        <div className="flex flex-wrap gap-2">
          <button className="btn btn-ghost" onClick={() => dl(survey.csv, 'respostas_mga.csv')} disabled={!d.total_respostas}><Download size={16} />CSV</button>
          <button className="btn btn-ghost" onClick={() => dl(survey.json, 'respostas_mga_completo.json')}><Download size={16} />JSON completo</button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        {[[d.total_respostas, 'respostas concluídas'], [d.rascunhos.em_andamento, 'em andamento (rascunhos salvos)'], [r.avaliadas, 'recomendações avaliadas'], [pct(r.aprovacao), 'aprovação das recomendações'], [d.sistema.nps ?? '—', `NPS (${d.sistema.nps_n} resp.)`], [d.nota_geral_media ?? '—', 'nota geral (1–5)']]
          .map(([v, l]) => <div key={l as string} className="card p-4"><p className="text-3xl font-semibold">{v}</p><p className="muted text-sm">{l}</p></div>)}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel t="Títulos mais jogados">{d.mais_jogados.length ? <ul className="space-y-3">{d.mais_jogados.map(x => <Bar key={x.game_id} label={x.jogo} value={x.citacoes} max={maxJ} text={`${x.citacoes} · ★ ${x.nota_media.toFixed(1)}`} />)}</ul> : <Empty />}</Panel>
        <Panel t="Melhor avaliados (mín. 2 notas)">{d.melhor_avaliados.length ? <ul className="space-y-3">{d.melhor_avaliados.map(x => <Bar key={x.game_id} label={x.jogo} value={x.nota_media} max={5} text={`★ ${x.nota_media.toFixed(2)} (${x.citacoes})`} />)}</ul> : <Empty />}</Panel>
        <Panel t="Aprovação por posição no ranking do MGA">{r.por_posicao.length ? <ul className="space-y-3">{r.por_posicao.map(x => <Bar key={x.posicao} label={`Posição ${x.posicao}`} value={x.aprovacao} max={1} text={`${pct(x.aprovacao)} (${x.avaliacoes})`} />)}</ul> : <Empty />}</Panel>
        <Panel t="Jogos sugeridos pelos usuários">{d.sugeridos_pelos_usuarios.length ? <ul className="space-y-3">{d.sugeridos_pelos_usuarios.map(x => <Bar key={x.titulo} label={x.titulo} value={x.votos} max={d.sugeridos_pelos_usuarios[0].votos} text={`${x.votos} voto(s)`} />)}</ul> : <Empty />}</Panel>
      </div>
      <Panel t="Pares referência → recomendado">
        {r.pares.length ? <div className="overflow-x-auto"><table className="w-full min-w-[520px] text-left text-sm"><thead className="muted text-xs"><tr><th className="pb-2 font-normal">Referência</th><th className="font-normal">Recomendado</th><th className="font-normal">Aprovação</th><th className="font-normal">Quero / Gostei / Não</th></tr></thead>
          <tbody>{r.pares.map((p, i) => <tr key={i} className="border-t border-line"><td className="py-2">{p.referencia}</td><td>{p.recomendado}</td><td>{pct(p.aprovacao)} <span className="muted">({p.avaliacoes})</span></td><td className="muted">{p.quero} / {p.gostei} / {p.nao}</td></tr>)}</tbody></table></div> : <Empty />}
      </Panel>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel t="O que pesa na escolha de um jogo (média 1–5)">{d.valores_media.length ? <ul className="space-y-3">{d.valores_media.map(x => <Bar key={x.nome} label={x.nome.replace(/_/g, ' ')} value={x.media ?? 0} max={5} text={`${x.media?.toFixed(2)} (${x.n})`} />)}</ul> : <Empty />}</Panel>
        <Panel t="Sistema: usabilidade (média 1–5)">{d.sistema.clareza || d.sistema.facilidade || d.sistema.surpresa ? <ul className="space-y-3">
          <Bar label="Explicações claras" value={d.sistema.clareza ?? 0} max={5} text={`${d.sistema.clareza ?? '—'}`} /><Bar label="Fácil de usar" value={d.sistema.facilidade ?? 0} max={5} text={`${d.sistema.facilidade ?? '—'}`} />
          <Bar label="Trouxe jogos novos" value={d.sistema.surpresa ?? 0} max={5} text={`${d.sistema.surpresa ?? '—'}`} /></ul> : <Empty />}</Panel>
        <Panel t="Mais querem jogar (lista de desejos)">{d.quero_jogar.length ? <ul className="space-y-3">{d.quero_jogar.map(x => <Bar key={x.jogo} label={x.jogo} value={x.votos} max={d.quero_jogar[0].votos} text={`${x.votos}`} />)}</ul> : <Empty />}</Panel>
        <Panel t="Jogos favoritos">{d.favoritos.length ? <ul className="space-y-3">{d.favoritos.map(x => <Bar key={x.jogo} label={x.jogo} value={x.votos} max={d.favoritos[0].votos} text={`${x.votos}`} />)}</ul> : <Empty />}</Panel>
        <Panel t="Perfil dos participantes">{([['Faixa etária', d.faixas], ['Região', d.regioes], ['Tempo jogando', d.anos_jogando], ['Horas/semana', d.horas], ['Gasto mensal', d.gasto], ['Como descobrem jogos', d.descoberta], ['Estilo', d.estilos], ['Voltaria a usar', d.voltaria]] as const).filter(([, l]) => l.length).map(([t, l]) => (
          <div key={t} className="mb-3 last:mb-0"><p className="muted mb-1.5 text-xs">{t}</p><div className="flex flex-wrap gap-2">{l.map(x => <span key={x.nome} className="chip !py-1 text-xs">{x.nome} <b className="text-gold">{x.total}</b></span>)}</div></div>))}
          {!d.faixas.length && !d.regioes.length && <Empty />}</Panel>
        <Panel t="O que gostaram e o que faltou">{d.abertas.length ? <ul className="space-y-3 text-sm">{d.abertas.map((c, i) => <li key={i} className="border-l-2 border-gold/50 pl-3">
          {c.gostou && <p><span className="text-gold">+</span> {c.gostou}</p>}{c.faltou && <p><span className="text-red-400">−</span> {c.faltou}</p>}<span className="muted block text-xs">{c.data}</span></li>)}</ul> : <Empty />}</Panel>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel t="Gêneros e plataformas">{d.generos.length || d.plataformas.length ? <div className="flex flex-wrap gap-2">{[...d.plataformas, ...d.generos].map(x => <span key={x.nome} className="chip">{x.nome} <b className="text-gold">{x.total}</b></span>)}</div> : <Empty />}</Panel>
        <Panel t="Comentários">{d.comentarios.length ? <ul className="space-y-3 text-sm">{d.comentarios.map((c, i) => <li key={i} className="border-l-2 border-gold/50 pl-3">{c.texto}<span className="muted block text-xs">{c.data}{c.nota ? ` · ★ ${c.nota}` : ''}</span></li>)}</ul> : <Empty />}</Panel>
      </div>
    </div>
  )
}
