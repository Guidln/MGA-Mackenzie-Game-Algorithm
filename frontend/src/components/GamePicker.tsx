import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import { api } from '../services/api'
import type { Game } from '../types'

export default function GamePicker({ label, value, onPick }: { label: string; value: Game | null; onPick: (g: Game) => void }) {
  const [q, setQ] = useState(''); const [res, setRes] = useState<Game[]>([]); const [open, setOpen] = useState(false)
  useEffect(() => {
    if (!q.trim()) { setRes([]); return }
    const t = setTimeout(() => api.search(q).then(setRes).catch(() => setRes([])), 200)
    return () => clearTimeout(t)
  }, [q])
  return (
    <div className="relative">
      <label className="muted mb-1 block text-xs">{label}</label>
      <div className="relative">
        <Search size={16} className="absolute left-3 top-2.5 text-paper/40" />
        <input className="input pl-9" placeholder="Pesquisar jogo pelo nome" value={open ? q : value?.jogo ?? q}
          onFocus={() => { setOpen(true); setQ('') }} onChange={e => setQ(e.target.value)} onBlur={() => setTimeout(() => setOpen(false), 150)} />
      </div>
      {open && res.length > 0 && (
        <ul className="card absolute z-20 mt-1 max-h-64 w-full overflow-auto py-1 shadow-xl">
          {res.map(g => (
            <li key={g.id}><button className="flex w-full justify-between px-3 py-2 text-left text-sm hover:bg-white/5"
              onMouseDown={() => { onPick(g); setOpen(false) }}><span>{g.jogo}</span><span className="muted">{g.ano}</span></button></li>
          ))}
        </ul>
      )}
    </div>
  )
}
