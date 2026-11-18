import { useEffect, useState } from 'react'
import type { Game } from '../types'
import { coverFor } from '../lib/covers'

// Ordem: cover_url (covers.json) → capa da Wikipédia → capa tipográfica (sempre visível por baixo enquanto a imagem carrega).
const TONES = ['#8B1A14', '#6d1510', '#3a3a3a', '#5a4a12', '#2c2c2c', '#7a2a24']
const hash = (s: string) => [...s].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7)

export default function Cover({ game, className = '' }: { game: Game; className?: string }) {
  const [src, setSrc] = useState<string | null>(game.cover_url)
  const [ok, setOk] = useState(false)
  useEffect(() => {
    let alive = true
    setOk(false); setSrc(game.cover_url)
    if (!game.cover_url) coverFor(game.jogo).then(u => alive && setSrc(u))
    return () => { alive = false }
  }, [game.jogo, game.cover_url])
  const compact = /w-\[|h-\d\b/.test(className) // miniaturas: texto menor e sem rótulo, para nada vazar
  const tone = TONES[hash(game.jogo) % TONES.length]
  return (
    <div className={`relative flex flex-col justify-between overflow-hidden p-2 ${className}`} style={{ background: `linear-gradient(160deg, ${tone}, #151515)` }}
      role="img" aria-label={`Capa de ${game.jogo}`}>
      {!compact && <span className="truncate text-[10px] uppercase tracking-widest text-paper/60">{game.genero}</span>}
      <span className={`line-clamp-4 break-words font-semibold leading-tight ${compact ? 'mt-auto text-[9px]' : 'text-sm'}`}>{game.jogo}</span>
      {src && <img src={src} alt="" loading="lazy" referrerPolicy="no-referrer" onLoad={() => setOk(true)} onError={() => setSrc(null)}
        className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-500 ${ok ? 'opacity-100' : 'opacity-0'}`} />}
    </div>
  )
}
