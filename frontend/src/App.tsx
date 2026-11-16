import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Explorer from './pages/Explorer'
import Recommendations from './pages/Recommendations'
import Versus from './pages/Versus'
import Insights from './pages/Insights'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="catalogo" element={<Explorer />} />
        <Route path="recomendacoes" element={<Recommendations />} />
        <Route path="versus" element={<Versus />} />
        <Route path="insights" element={<Insights />} />
      </Route>
    </Routes>
  )
}
