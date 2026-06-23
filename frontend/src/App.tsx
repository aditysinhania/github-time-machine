import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { InsightsPage } from '@/pages/InsightsPage'

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard/:repoId" element={<DashboardPage />} />
        <Route path="/insights/:repoId" element={<InsightsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
