import { Star } from 'lucide-react'

export default function Stars({ value, onChange, size = 18, label }: { value: number; onChange: (n: number) => void; size?: number; label: string }) {
  return (
    <div role="radiogroup" aria-label={label} className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map(n => (
        <button key={n} type="button" role="radio" aria-checked={value === n} aria-label={`${n} de 5`} onClick={() => onChange(n)}
          className="rounded p-0.5 transition-transform hover:scale-110 focus-visible:ring-2 focus-visible:ring-gold">
          <Star size={size} className={n <= value ? 'fill-gold text-gold' : 'text-paper/30'} />
        </button>
      ))}
    </div>
  )
}
