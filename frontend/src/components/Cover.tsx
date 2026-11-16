import type { Game } from '../types'

// Sem imagens no projeto: usa cover_url quando existir; caso contrário, capa tipográfica.
const TONES = ['#8B1A14', '#6d1510', '#3a3a3a', '#5a4a12', '#2c2c2c', '#7a2a24']
const hash = (s: string) => [...s].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7)

export default function Cover({ game, className = '' }: { game: Game; className?: string }) {
  if (game.cover_url) return <img src={game.cover_url} alt={`Capa de ${game.jogo}`} className={`object-cover ${className}`} />
  const tone = TONES[hash(game.jogo) % TONES.length]
  return (
    <div className={`flex flex-col justify-between p-3 ${className}`} style={{ background: `linear-gradient(160deg, ${tone}, #151515)` }} aria-label={`Capa de ${game.jogo}`}>
      <span className="text-[10px] uppercase tracking-widest text-paper/60">{game.genero}</span>
      <span className="text-sm font-semibold leading-tight">{game.jogo}</span>
    </div>
  )
}
