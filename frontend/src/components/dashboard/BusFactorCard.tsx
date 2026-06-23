import { AlertTriangle } from 'lucide-react'
import type { Contributor } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Avatar } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'

const COLORS = ['#7c3aed', '#0ea5e9', '#10b981']

interface BusFactorCardProps {
  contributors: Contributor[]
  busFactorScore: number
}

export function BusFactorCard({ contributors, busFactorScore }: BusFactorCardProps) {
  const top3 = contributors.slice(0, 3)
  const isRisky = busFactorScore < 50

  return (
    <Card className="p-5">
      <h3 className="text-[15px] font-bold text-foreground">Bus Factor Analysis</h3>
      <p className="mb-4 text-xs text-muted-foreground">Critical knowledge concentration</p>

      <div className="flex flex-col gap-3.5">
        {top3.map((c, i) => (
          <div key={c.email}>
            <div className="mb-1.5 flex items-center gap-2">
              <Avatar initials={c.avatar_initials} seed={c.email} size={28} />
              <span className="flex-1 text-sm font-medium text-foreground">{c.name}</span>
              <span className="text-[11px] text-muted-foreground">{c.commit_count} commits</span>
            </div>
            <Progress value={c.commit_percentage} color={COLORS[i]} className="h-1" />
          </div>
        ))}
      </div>

      {isRisky && (
        <div className="mt-3.5 flex items-start gap-2 rounded-lg border border-red-500/40 bg-red-500/10 p-2.5 text-[12px] text-red-300">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          High bus factor risk — knowledge too concentrated in too few people
        </div>
      )}
    </Card>
  )
}
