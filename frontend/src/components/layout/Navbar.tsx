import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Github, LayoutDashboard, Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { RepositoryFull } from '@/types/api'

interface NavbarProps {
  repository?: RepositoryFull | null
  activePage?: 'dashboard' | 'insights'
}

export function Navbar({ repository, activePage = 'dashboard' }: NavbarProps) {
  const navigate = useNavigate()

  return (
    <nav className="sticky top-0 z-20 flex items-center justify-between border-b border-border bg-background/95 px-6 py-3 backdrop-blur">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/')}>
          <ArrowLeft className="h-3.5 w-3.5" />
          Back
        </Button>

        {repository && (
          <div className="flex items-center gap-2">
            <Github className="h-[18px] w-[18px] text-foreground" />
            <span className="text-[15px] font-bold text-foreground">{repository.full_name}</span>
            {repository.primary_language && (
              <Badge variant="info">{repository.primary_language}</Badge>
            )}
          </div>
        )}
      </div>

      {repository && (
        <div className="flex items-center gap-1">
          <Link to={`/dashboard/${repository.id}`}>
            <Button variant={activePage === 'dashboard' ? 'secondary' : 'ghost'} size="sm">
              <LayoutDashboard className="h-3.5 w-3.5" />
              Dashboard
            </Button>
          </Link>
          <Link to={`/insights/${repository.id}`}>
            <Button variant={activePage === 'insights' ? 'secondary' : 'ghost'} size="sm">
              <Sparkles className="h-3.5 w-3.5" />
              AI Insights
            </Button>
          </Link>
        </div>
      )}
    </nav>
  )
}
