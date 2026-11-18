import { motion } from 'framer-motion'
import type { Game } from '../types'
import Cover from './Cover'

export default function GameCard({ game, onClick, badge }: { game: Game; onClick?: () => void; badge?: string }) {
  return (
    <motion.button whileHover={{ y: -4 }} transition={{ duration: 0.15 }} onClick={onClick}
      className="card card-hover group overflow-hidden text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-gold">
      <div className="relative overflow-hidden">
        <Cover game={game} className="aspect-[3/4] w-full transition-transform duration-500 group-hover:scale-105" />
        {badge && <span className="absolute left-2 top-2 rounded-md bg-ink/85 px-2 py-0.5 text-xs font-medium text-gold backdrop-blur">{badge}</span>}
      </div>
      <div className="p-3">
        <p className="truncate text-sm font-medium">{game.jogo}</p>
        <p className="muted truncate text-xs">{game.ano} · {game.genero}</p>
        <p className="muted truncate text-xs">{game.plataforma}</p>
      </div>
    </motion.button>
  )
}
