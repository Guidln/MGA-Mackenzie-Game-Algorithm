import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeft, ArrowRight, Bookmark, Check, CloudOff, Heart, Loader2, Plus, Search, Send, ThumbsDown, X } from 'lucide-react'
import Cover from '../components/Cover'
import GamePicker from '../components/GamePicker'
import Stars from '../components/Stars'
import { api, survey } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import type { Game, RecResponse, RespostaRec } from '../types'

const KEY = 'mga:pesquisa:v2', SID = 'mga:sid'
const FAIXAS = ['Menos de 18', '18–24', '25–34', '35–44', '45 ou mais']
const REGIOES = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul', 'Outro país']
const ANOS = ['Menos de 1 ano', '1–3 anos', '4–10 anos', 'Mais de 10 anos']
const HORAS = ['Menos de 3 h', '3–10 h', '10–20 h', 'Mais de 20 h']
const GASTO = ['Nada', 'Até R$ 50', 'R$ 50–150', 'Mais de R$ 150']
const PLATS = ['PC', 'PlayStation', 'Xbox', 'Nintendo Switch', 'Celular']
const DESC = ['Amigos', 'YouTube / Twitch', 'Redes sociais', 'Lojas (Steam, PSN…)', 'Sites de review', 'Premiações (The Game Awards)', 'Propagandas']
const ESTILOS = ['Sozinho(a)', 'Com amigos', 'Os dois']
const VALORES: [string, string][] = [['historia', 'História e personagens'], ['graficos', 'Gráficos e arte'], ['desafio', 'Dificuldade desafiadora'], ['multiplayer', 'Jogar online / cooperativo'],
  ['mundo_aberto', 'Mundo aberto para explorar'], ['duracao', 'Jogos longos'], ['preco', 'Preço baixo'], ['indie', 'Jogos indie / autorais']]
const STEPS = ['Perfil', 'Preferências', 'Seus jogos', 'Recomendações', 'Sua opinião']
const OPTS: [RespostaRec, string, typeof Heart][] = [['quero', 'Quero jogar', Bookmark], ['gostei', 'Já joguei e gostei', Heart], ['nao', 'Não me interessa', ThumbsDown]]

interface Form {
  nome: string; faixa: string; regiao: string; anos: string; horas: string; gasto: string
  plataformas: string[]; descoberta: string[]; generos: string[]; valores: Record<string, number>; estilo: string
  notas: Record<number, number>; wishlist: number[]; favorito: number | null; extras: string[]
  aval: Record<string, RespostaRec>; nps: number | null; clareza: number; facilidade: number; surpresa: number; voltaria: string
  gostou: string; faltou: string; notaGeral: number; comentario: string; consent: boolean
}
const EMPTY: Form = { nome: '', faixa: '', regiao: '', anos: '', horas: '', gasto: '', plataformas: [], descoberta: [], generos: [], valores: {}, estilo: '', notas: {}, wishlist: [], favorito: null,
  extras: [], aval: {}, nps: null, clareza: 0, facilidade: 0, surpresa: 0, voltaria: '', gostou: '', faltou: '', notaGeral: 0, comentario: '', consent: false }
const load = (): { f: Form; step: number } => {
  try { const d = JSON.parse(localStorage.getItem(KEY) ?? '{}'); return { f: { ...EMPTY, ...d.f, consent: false }, step: Math.min(Number(d.step) || 0, 4) } } catch { return { f: EMPTY, step: 0 } }
}
const sid = () => {
  try { let s = localStorage.getItem(SID); if (!s) { s = (crypto.randomUUID?.() ?? String(Date.now()) + Math.random().toString(16).slice(2)); localStorage.setItem(SID, s) } return s } catch { return 'anon' + Date.now() }
}
const toggle = <T,>(a: T[], v: T) => (a.includes(v) ? a.filter(x => x !== v) : [...a, v])

const Chips = ({ list, value, on }: { list: string[]; value: string | string[]; on: (v: string) => void }) => (
  <div className="flex flex-wrap gap-2">{list.map(x => { const sel = Array.isArray(value) ? value.includes(x) : value === x
      return <button key={x} type="button" aria-pressed={sel} className={`chip ${sel ? 'chip-on' : ''}`} onClick={() => on(x)}>{sel && <Check size={14} className="shrink-0" />}{x}</button> })}</div>)
const Field = ({ t, hint: h, children }: { t: string; hint?: string; children: React.ReactNode }) =>
    <fieldset className="min-w-0"><legend className="mb-2 text-sm font-medium">{t} {h && <span className="muted font-normal">({h})</span>}</legend>{children}</fieldset>


export default function Pesquisa() {
  const games = useAsync(api.games)
  const init = useMemo(load, [])
  const [step, setStep] = useState(init.step); const [f, setF] = useState<Form>(init.f)
  const [q, setQ] = useState(''); const [extra, setExtra] = useState('')
  const [recs, setRecs] = useState<Record<number, RecResponse>>({}); const [ref, setRef] = useState<number | null>(null); const [busy, setBusy] = useState(false)
  const [preview, setPreview] = useState<RecResponse | null>(null)
  const [save, setSave] = useState<{ s: 'idle' | 'saving' | 'saved' | 'error'; at?: string }>({ s: 'idle' })
  const [sending, setSending] = useState(false); const [err, setErr] = useState(''); const [done, setDone] = useState(false)
  const [toast, setToast] = useState(''); const sidRef = useRef(sid()); const tt = useRef<number>()
  const set = (p: Partial<Form>) => setF(s => ({ ...s, ...p }))
  const say = (m: string) => { setToast(m); window.clearTimeout(tt.current); tt.current = window.setTimeout(() => setToast(''), 1800) }
  const all = games.data ?? []
  const byId = (id: number | null) => all.find(g => g.id === id) ?? null

  const ids = Object.keys(f.notas).map(Number)
  const unrated = ids.filter(i => !f.notas[i]).length
  const generos = useMemo(() => [...new Set(all.map(g => g.genero))].sort(), [all])
  const shown = all.filter(g => g.jogo.toLowerCase().includes(q.toLowerCase()))
  const ranked = [...ids].sort((a, b) => f.notas[b] - f.notas[a]).map(byId).filter(Boolean) as Game[]
  const top = byId(f.favorito) ?? ranked[0] ?? null

  // Progresso em tempo real: fração de itens respondidos.
  const checks = [f.faixa, f.regiao, f.anos, f.horas, f.gasto, f.plataformas.length, f.descoberta.length, f.generos.length,
    Object.keys(f.valores).length >= VALORES.length, f.estilo, ids.length && !unrated, f.favorito !== null, Object.keys(f.aval).length,
    f.nps !== null, f.clareza, f.facilidade, f.surpresa, f.voltaria, f.notaGeral, f.consent]
  const pct = Math.round(100 * checks.filter(Boolean).length / checks.length)

  // Autosave: localStorage na hora; servidor 800 ms depois da última alteração (guarda mesmo quem não conclui).
  useEffect(() => {
    try { localStorage.setItem(KEY, JSON.stringify({ f: { ...f, consent: false }, step })) } catch { /* ok */ }
    setSave(s => ({ ...s, s: 'saving' }))
    const t = window.setTimeout(() => survey.draft(sidRef.current, { ...f, consent: false, etapa: step, progresso: pct })
      .then(() => setSave({ s: 'saved', at: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) })).catch(() => setSave({ s: 'error' })), 800)
    return () => window.clearTimeout(t)
  }, [f, step]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { window.scrollTo({ top: 0 }) }, [step, done])

  // Prévia ao vivo: recomendações do MGA (já com a comunidade) para o jogo que a pessoa mais gostou.
  useEffect(() => {
    if (!top) { setPreview(null); return }
    const t = window.setTimeout(() => api.recommend(top.id).then(setPreview).catch(() => setPreview(null)), 500)
    return () => window.clearTimeout(t)
  }, [top?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const pick = (g: Game) => setF(s => { const n = { ...s.notas }; if (g.id in n) { delete n[g.id] } else n[g.id] = 0; return { ...s, notas: n, favorito: g.id in n ? s.favorito : s.favorito === g.id ? null : s.favorito } })
  const addExtra = () => {
    const t = extra.trim()
    if (!t) return
    if (f.extras.some(e => e.toLowerCase() === t.toLowerCase())) return say('Você já adicionou esse jogo')
    if (f.extras.length >= 10) return say('Limite de 10 sugestões')
    set({ extras: [...f.extras, t.slice(0, 80)] }); setExtra(''); say(`“${t}” adicionado`)
  }
  const gen = async (id: number) => {
    setRef(id)
    if (recs[id]) return
    setBusy(true); setErr('')
    try { const r = await api.recommend(id); setRecs(s => ({ ...s, [id]: r })) } catch (e) { setErr((e as Error).message) } finally { setBusy(false) }
  }
  useEffect(() => { if (step === 3 && ref === null && games.data && top) gen(top.id) }, [step, games.data]) // eslint-disable-line react-hooks/exhaustive-deps

  const cur = ref !== null ? recs[ref] : undefined
  const evaluated = Object.keys(f.aval).length
  const hint = step === 2 && !(ids.length || f.extras.length) ? 'Marque ao menos um jogo ou sugira um título para continuar.' : step === 2 && unrated ? `Falta dar nota para ${unrated} jogo(s) marcado(s).` : step === 4 && !f.consent ? 'Aceite o termo para enviar.' : ''
  const canNext = !hint

  const send = async () => {
    setSending(true); setErr('')
    try {
      await survey.submit({
        nome: f.nome.trim() || null, faixa_etaria: f.faixa || null, horas_semana: f.horas || null, regiao: f.regiao || null, anos_jogando: f.anos || null, gasto_mensal: f.gasto || null,
        plataformas: f.plataformas, descoberta: f.descoberta, generos: f.generos, valores: f.valores, estilo: f.estilo || null,
        jogos: ids.map(id => ({ game_id: id, nota: f.notas[id] })), wishlist: f.wishlist, favorito_id: f.favorito, extras: f.extras,
        referencia_id: ref, sid: sidRef.current,
        avaliacoes: Object.entries(recs).flatMap(([rid, r]) => r.recomendacoes.filter(x => f.aval[`${rid}:${x.jogo.id}`])
          .map(x => ({ referencia_id: Number(rid), game_id: x.jogo.id, posicao: x.posicao, similaridade: x.similaridade, resposta: f.aval[`${rid}:${x.jogo.id}`] }))),
        nota_geral: f.notaGeral || null, comentario: f.comentario.trim() || null,
        sistema: { nps: f.nps, clareza: f.clareza || null, facilidade: f.facilidade || null, surpresa: f.surpresa || null, voltaria: f.voltaria || null, gostou: f.gostou.trim() || null, faltou: f.faltou.trim() || null },
        consentimento: f.consent,
      })
      try { localStorage.removeItem(KEY) } catch { /* ok */ }
      setDone(true)
    } catch (e) { setErr((e as Error).message) } finally { setSending(false) }
  }

  if (done) return (
    <motion.div initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} className="mx-auto max-w-lg py-16 text-center">
      <span className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-gold/15 text-gold"><Check size={32} /></span>
      <h1 className="mt-6 text-3xl font-bold">Obrigado por participar!</h1>
      <p className="muted mt-3">Suas respostas já entram no cálculo das recomendações do sistema: jogos bem avaliados e aprovados pela comunidade sobem no ranking.</p>
      <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
        <Link to={top ? `/recomendacoes?id=${top.id}` : '/recomendacoes'} className="btn btn-red justify-center">Ver recomendações atualizadas</Link>
        <button className="btn btn-ghost justify-center" onClick={() => { try { localStorage.removeItem(SID) } catch { /* ok */ } sidRef.current = sid(); setF(EMPTY); setRecs({}); setRef(null); setStep(0); setDone(false) }}>Enviar outra resposta</button>
      </div>
    </motion.div>
  )

  return (
    <div className="mx-auto max-w-4xl">
      <p className="text-sm text-gold">Pesquisa com jogadores · cerca de 5 minutos</p>
      <h1 className="mt-1 text-3xl font-bold">Conte quais jogos você curte</h1>
      <p className="muted mt-2 max-w-2xl text-sm">Tudo o que você preenche é salvo automaticamente. Suas respostas ajustam as recomendações do sistema para todo mundo.</p>

      {/* Barra de progresso em tempo real */}
      <div className="sticky top-14 z-30 -mx-4 mt-6 border-b border-line bg-ink/95 px-4 py-2.5 backdrop-blur">
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="font-medium">Etapa {step + 1} de {STEPS.length} · {STEPS[step]}</span>
          <span className="flex shrink-0 items-center gap-3">
            <span className="muted flex items-center gap-1" aria-live="polite">
              {save.s === 'saving' && <><Loader2 size={12} className="animate-spin" />Salvando…</>}
              {save.s === 'saved' && <><Check size={12} className="text-gold" />Salvo às {save.at}</>}
              {save.s === 'error' && <><CloudOff size={12} />Salvo só neste aparelho</>}
            </span>
            <b className="tabular-nums text-gold">{pct}%</b>
          </span>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Progresso do formulário">
          <div className="h-full rounded-full bg-gradient-to-r from-mga to-gold transition-all duration-500" style={{ width: `${pct}%` }} /></div>
        <ol className="mt-2 flex gap-1.5">{STEPS.map((t, i) => <li key={t} className="flex-1"><button type="button" onClick={() => setStep(i)} aria-label={`Ir para ${t}`} aria-current={i === step}
          className={`h-1 w-full rounded-full transition-colors ${i < step ? 'bg-gold/70' : i === step ? 'bg-paper' : 'bg-white/10'}`} /></li>)}</ol>
      </div>

      <AnimatePresence mode="wait">
        <motion.section key={step} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: .18 }} className="mt-6">
          {step === 0 && (
            <div className="card space-y-6 p-5 sm:p-6">
              <div><label htmlFor="nome" className="mb-1 block text-sm font-medium">Como podemos te chamar? <span className="muted font-normal">(opcional)</span></label>
                <input id="nome" className="input max-w-sm" maxLength={80} value={f.nome} onChange={e => set({ nome: e.target.value })} placeholder="Apelido ou primeiro nome" /></div>
              <Field t="Faixa etária" hint="opcional"><Chips list={FAIXAS} value={f.faixa} on={v => set({ faixa: f.faixa === v ? '' : v })} /></Field>
              <Field t="De onde você joga?" hint="opcional"><Chips list={REGIOES} value={f.regiao} on={v => set({ regiao: f.regiao === v ? '' : v })} /></Field>
              <Field t="Há quanto tempo você joga?"><Chips list={ANOS} value={f.anos} on={v => set({ anos: f.anos === v ? '' : v })} /></Field>
              <Field t="Quanto você joga por semana?"><Chips list={HORAS} value={f.horas} on={v => set({ horas: f.horas === v ? '' : v })} /></Field>
              <Field t="Quanto gasta com jogos por mês?"><Chips list={GASTO} value={f.gasto} on={v => set({ gasto: f.gasto === v ? '' : v })} /></Field>
              <Field t="Onde você joga?" hint="pode marcar vários"><Chips list={PLATS} value={f.plataformas} on={v => set({ plataformas: toggle(f.plataformas, v) })} /></Field>
              <Field t="Como você descobre jogos novos?" hint="pode marcar vários"><Chips list={DESC} value={f.descoberta} on={v => set({ descoberta: toggle(f.descoberta, v) })} /></Field>
            </div>
          )}

          {step === 1 && (
            <div className="card space-y-6 p-5 sm:p-6">
              <Field t="Gêneros favoritos" hint="pode marcar vários"><Chips list={generos} value={f.generos} on={v => set({ generos: toggle(f.generos, v) })} /></Field>
              <Field t="Você prefere jogar…"><Chips list={ESTILOS} value={f.estilo} on={v => set({ estilo: f.estilo === v ? '' : v })} /></Field>
              <Field t="O quanto cada item pesa na sua escolha de um jogo?" hint="1 = nada, 5 = muito">
                <ul className="divide-y divide-line">{VALORES.map(([k, t]) => (
                  <li key={k} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 py-2.5"><span className="min-w-0 text-sm">{t}</span>
                    <Stars value={f.valores[k] ?? 0} label={t} onChange={n => set({ valores: { ...f.valores, [k]: n } })} /></li>))}</ul></Field>
            </div>
          )}

          {step === 2 && (
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <div className="relative min-w-[200px] flex-1"><Search size={16} className="pointer-events-none absolute left-3 top-2.5 text-paper/40" />
                  <input className="input pl-9" placeholder="Buscar jogo" aria-label="Buscar jogo" value={q} onChange={e => setQ(e.target.value)} /></div>
                <p className="text-sm" aria-live="polite"><b className="text-gold">{ids.length}</b> <span className="muted">jogados · </span><b className="text-gold">{f.wishlist.length}</b> <span className="muted">na lista de desejos</span></p>
              </div>
              <p className="muted mt-3 text-sm">Toque na capa dos jogos que você <b className="text-paper">já jogou</b> e dê uma nota. Use “Quero jogar” para os que ainda estão na fila.</p>
              {games.error && <p className="mt-3 text-sm text-red-400">{games.error}</p>}

              {top && (
                <div className="card mt-4 p-4" aria-live="polite">
                  <p className="text-sm font-medium">Prévia ao vivo <span className="muted font-normal">· com base em {top.jogo}, o sistema indicaria:</span></p>
                  <ul className="mt-3 grid grid-cols-5 gap-2 sm:gap-3">
                    {preview ? preview.recomendacoes.map(r => <li key={r.jogo.id} className="min-w-0"><Cover game={r.jogo} className="aspect-[3/4] w-full rounded-lg" />
                      <p className="mt-1 truncate text-[11px]" title={r.jogo.jogo}>{r.jogo.jogo}</p></li>)
                      : Array.from({ length: 5 }, (_, i) => <li key={i} className="skeleton aspect-[3/4]" />)}
                  </ul>
                </div>)}

              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {games.loading && Array.from({ length: 10 }, (_, i) => <div key={i} className="skeleton aspect-[3/4]" />)}
                {shown.map(g => {
                  const on = g.id in f.notas, wish = f.wishlist.includes(g.id)
                  return (
                    <div key={g.id} className={`card flex min-w-0 flex-col overflow-hidden transition ${on ? 'border-gold ring-1 ring-gold/60' : 'card-hover'}`}>
                      <button type="button" aria-pressed={on} aria-label={`${on ? 'Desmarcar' : 'Marcar'} ${g.jogo} como jogado`} onClick={() => { pick(g); if (!on) say(`${g.jogo}: agora dê uma nota`) }} className="relative block w-full text-left">
                        <Cover game={g} className="aspect-[3/4] w-full" />
                        {on && <span className="absolute right-2 top-2 grid h-6 w-6 place-items-center rounded-full bg-gold text-ink shadow"><Check size={14} /></span>}
                      </button>
                      <div className="flex flex-1 flex-col gap-1.5 p-2.5">
                        <p className="truncate text-sm font-medium" title={g.jogo}>{g.jogo}</p>
                        {on ? <div className="flex flex-wrap items-center gap-x-2">
                          <Stars value={f.notas[g.id]} label={`Nota para ${g.jogo}`} size={15} onChange={n => set({ notas: { ...f.notas, [g.id]: n } })} />
                          {!f.notas[g.id] && <span className="text-[11px] text-gold">dê uma nota</span>}</div>
                          : <p className="muted truncate text-xs">{g.ano} · {g.genero}</p>}
                        <button type="button" aria-pressed={wish} onClick={() => set({ wishlist: toggle(f.wishlist, g.id) })}
                          className={`mt-auto inline-flex items-center justify-center gap-1.5 rounded-lg border px-2 py-1 text-xs transition ${wish ? 'border-gold bg-gold/10 text-gold' : 'border-line text-paper/70 hover:border-gold/50'}`}>
                          <Bookmark size={12} className={`shrink-0 ${wish ? 'fill-gold' : ''}`} />Quero jogar</button>
                      </div>
                    </div>)
                })}
              </div>
              {!games.loading && shown.length === 0 && <p className="muted mt-6 text-center text-sm">Nenhum jogo encontrado para “{q}”.</p>}

              <div className="card mt-6 space-y-5 p-5">
                <Field t="Qual é o seu jogo favorito do catálogo?" hint="entre os que você marcou">
                  {ranked.length ? <div className="flex flex-wrap gap-2">{ranked.map(g => <button key={g.id} type="button" aria-pressed={f.favorito === g.id} className={`chip ${f.favorito === g.id ? 'chip-on' : ''}`}
                    onClick={() => set({ favorito: f.favorito === g.id ? null : g.id })}><Heart size={14} className={`shrink-0 ${f.favorito === g.id ? 'fill-gold' : ''}`} />{g.jogo}</button>)}</div>
                    : <p className="muted text-sm">Marque jogos acima para escolher o favorito.</p>}</Field>
                <div><label htmlFor="extra" className="text-sm font-medium">Algum outro jogo que você recomenda? <span className="muted font-normal">(fora do catálogo)</span></label>
                  <div className="mt-2 flex max-w-md gap-2">
                    <input id="extra" className="input" value={extra} maxLength={80} placeholder="Ex.: Hollow Knight" onChange={e => setExtra(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addExtra() } }} />
                    <button type="button" className="btn btn-ghost shrink-0" onClick={addExtra} aria-label="Adicionar jogo"><Plus size={16} /></button></div>
                  {f.extras.length > 0 && <ul className="mt-3 flex flex-wrap gap-2">{f.extras.map(x => <li key={x} className="chip chip-on max-w-full"><span className="truncate">{x}</span>
                    <button type="button" aria-label={`Remover ${x}`} onClick={() => set({ extras: f.extras.filter(y => y !== x) })}><X size={14} /></button></li>)}</ul>}</div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div className="card p-5">
                <h2 className="font-semibold">Teste as recomendações do sistema</h2>
                <p className="muted mt-1 text-sm">Escolha um jogo de referência e diga o que achou dos cinco títulos sugeridos. Você pode testar mais de um jogo.</p>
                {ranked.length > 0 && <div className="mt-3 flex flex-wrap gap-2">{ranked.slice(0, 4).map(g => <button key={g.id} type="button" aria-pressed={ref === g.id} className={`chip ${ref === g.id ? 'chip-on' : ''}`} onClick={() => gen(g.id)}>{g.jogo}</button>)}</div>}
                <div className="mt-3 max-w-md"><GamePicker label="Ou escolha outro jogo" value={byId(ref)} onPick={g => gen(g.id)} /></div>
                <p className="mt-3 text-sm" aria-live="polite"><b className="text-gold">{evaluated}</b> <span className="muted">recomendação(ões) avaliada(s) · {Object.keys(recs).length} jogo(s) testado(s)</span></p>
              </div>
              {err && <p role="alert" className="text-sm text-red-400">{err}</p>}
              {busy && <div className="space-y-3">{[0, 1, 2].map(i => <div key={i} className="skeleton h-28" />)}</div>}
              {!busy && !cur && !top && <p className="muted text-sm">Você ainda não marcou jogos. Escolha um acima para testar ou pule esta etapa.</p>}
              {!busy && cur && (
                <ol className="space-y-3">
                  {cur.recomendacoes.map(r => { const k = `${cur.referencia.id}:${r.jogo.id}`
                    return (
                      <li key={r.jogo.id} className="card p-4">
                        <div className="flex items-center gap-4">
                          <Cover game={r.jogo} className="h-24 w-[72px] shrink-0 rounded-lg" />
                          <div className="min-w-0"><p className="muted text-xs">#{r.posicao} · parecido com {cur.referencia.jogo}</p>
                            <p className="truncate font-medium">{r.jogo.jogo}</p><p className="muted truncate text-sm">{r.jogo.ano} · {r.jogo.genero}</p></div>
                        </div>
                        <div className="mt-3 flex flex-wrap gap-2" role="radiogroup" aria-label={`Sua opinião sobre ${r.jogo.jogo}`}>
                          {OPTS.map(([v, t, Icon]) => <button key={v} type="button" role="radio" aria-checked={f.aval[k] === v} onClick={() => { set({ aval: { ...f.aval, [k]: v } }); say('Resposta salva') }}
                            className={`chip ${f.aval[k] === v ? 'chip-on' : ''}`}><Icon size={14} className="shrink-0" />{t}</button>)}
                        </div>
                      </li>) })}
                </ol>)}
            </div>
          )}

          {step === 4 && (
            <div className="card space-y-6 p-5 sm:p-6">
              <Field t="De 0 a 10, o quanto você indicaria este sistema a um amigo?">
                <div className="flex flex-wrap gap-1.5" role="radiogroup" aria-label="Nota de 0 a 10">{Array.from({ length: 11 }, (_, n) => <button key={n} type="button" role="radio" aria-checked={f.nps === n} onClick={() => set({ nps: n })}
                  className={`grid h-10 w-10 place-items-center rounded-lg border text-sm transition ${f.nps === n ? 'border-gold bg-gold text-ink' : 'border-line hover:border-gold/60'}`}>{n}</button>)}</div></Field>
              {([['notaGeral', 'No geral, as recomendações foram boas?'], ['clareza', 'As explicações (“Por que este jogo?”) foram claras?'], ['facilidade', 'O sistema foi fácil de usar?'], ['surpresa', 'As recomendações trouxeram jogos que você não conhecia?']] as const).map(([k, t]) => (
                <Field key={k} t={t} hint="1 a 5"><Stars value={f[k]} onChange={n => set({ [k]: n } as Partial<Form>)} label={t} size={24} /></Field>))}
              <Field t="Você usaria o sistema de novo?"><Chips list={['Sim', 'Talvez', 'Não']} value={f.voltaria} on={v => set({ voltaria: f.voltaria === v ? '' : v })} /></Field>
              <div className="grid gap-4 sm:grid-cols-2">
                <div><label htmlFor="g" className="mb-1 block text-sm font-medium">O que você mais gostou?</label><textarea id="g" className="input min-h-24" maxLength={500} value={f.gostou} onChange={e => set({ gostou: e.target.value })} /></div>
                <div><label htmlFor="fa" className="mb-1 block text-sm font-medium">O que faltou ou poderia melhorar?</label><textarea id="fa" className="input min-h-24" maxLength={500} value={f.faltou} onChange={e => set({ faltou: e.target.value })} /></div>
              </div>
              <div><label htmlFor="com" className="mb-1 block text-sm font-medium">Comentário livre <span className="muted font-normal">(opcional)</span></label>
                <textarea id="com" className="input min-h-20" maxLength={1000} value={f.comentario} onChange={e => set({ comentario: e.target.value })} /></div>
              <label className="flex cursor-pointer items-start gap-3 text-sm">
                <input type="checkbox" className="mt-0.5 h-4 w-4 shrink-0 accent-[#D4A017]" checked={f.consent} onChange={e => set({ consent: e.target.checked })} />
                <span>Concordo em usar minhas respostas, de forma anônima, em análises acadêmicas do projeto MGA e no ajuste das recomendações. Não coletamos e-mail nem dados de contato.</span>
              </label>
            </div>
          )}
        </motion.section>
      </AnimatePresence>

      {err && step !== 3 && <p role="alert" className="mt-4 text-sm text-red-400">{err}</p>}
      <div className="sticky bottom-0 z-30 -mx-4 mt-8 border-t border-line bg-ink/95 px-4 py-3 backdrop-blur">
        <div className="flex items-center justify-between gap-3">
          <button type="button" className="btn btn-ghost shrink-0" disabled={step === 0} onClick={() => setStep(step - 1)}><ArrowLeft size={16} />Voltar</button>
          <p className="min-w-0 flex-1 text-center text-xs text-gold" aria-live="polite">{hint}</p>
          {step < STEPS.length - 1
            ? <button type="button" className="btn btn-red shrink-0" disabled={!canNext} onClick={() => setStep(step + 1)}>Continuar<ArrowRight size={16} /></button>
            : <button type="button" className="btn btn-gold shrink-0" disabled={!canNext || sending} onClick={send}>{sending ? 'Enviando…' : 'Enviar'}<Send size={16} /></button>}
        </div>
      </div>
      {/* Aviso rápido: fica acima da barra de ações, nunca sobre os botões */}
      <div className="pointer-events-none fixed inset-x-0 bottom-20 z-40 flex justify-center px-4" aria-live="polite">
        <AnimatePresence>{toast && <motion.p initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="max-w-full truncate rounded-full border border-gold/40 bg-panel px-4 py-1.5 text-sm shadow-xl">{toast}</motion.p>}</AnimatePresence>
      </div>
    </div>
  )
}
