import { NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { useEffect } from 'react'

const links = [['/', 'Início'], ['/catalogo', 'Catálogo'], ['/recomendacoes', 'Recomendações'], ['/versus', 'Versus'], ['/insights', 'Insights']]

export default function Layout() {
  const [open, setOpen] = useState(false)
  const [aviso, setAviso] = useState('')
  useEffect(() => {
    fetch((import.meta.env.VITE_API_URL ?? '/api') + '/health').then(r => r.json())
      .then(h => setAviso(h.status === 'ok' ? '' : h.mensagem ?? 'Base de dados não carregada.'))
      .catch(() => setAviso('Não foi possível falar com a API. Confirme se o backend está rodando em http://localhost:8000.'))
  }, [])
  const cls = ({ isActive }: { isActive: boolean }) => `text-sm transition-colors ${isActive ? 'text-gold' : 'text-paper/70 hover:text-paper'}`
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-line bg-ink/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <NavLink to="/" className="flex items-center gap-2 font-semibold">
            <span className="grid h-7 w-7 place-items-center rounded-md bg-mga text-xs font-bold">MGA</span>
            <span>Discovery</span>
          </NavLink>
          <nav className="hidden gap-6 md:flex">{links.map(([to, t]) => <NavLink key={to} to={to} end={to === '/'} className={cls}>{t}</NavLink>)}</nav>
          <button className="md:hidden" aria-label="Menu" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
        </div>
        {open && <nav className="flex flex-col gap-3 border-t border-line px-4 py-3 md:hidden">
          {links.map(([to, t]) => <NavLink key={to} to={to} end={to === '/'} className={cls} onClick={() => setOpen(false)}>{t}</NavLink>)}</nav>}
      </header>
      {aviso && <div className="border-b border-gold/40 bg-gold/10 px-4 py-2 text-center text-sm text-gold">{aviso}</div>}
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8"><Outlet /></main>
      <footer className="border-t border-line py-6 text-center text-xs text-paper/50">
        MGA – Mackenzie Game Algorithm · Projeto Aplicado III · Universidade Presbiteriana Mackenzie<br />
        Recomendação baseada em conteúdo. Os escores indicam proximidade entre atributos, não preferência de usuários.
      </footer>
    </div>
  )
}
