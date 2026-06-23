import { Users, Bus, Award } from 'lucide-react'
import type { Contributor } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Avatar } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { KpiCard } from './KpiCard'
import { ContributorDonutChart } from './ContributorDonutChart'
import { BusFactorCard } from './BusFactorCard'
import { formatNumber } from '@/lib/utils'

const COLORS = ['#7c3aed', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

interface ContributorsTabProps {
  contributors: Contributor[]
  total: number
  busFactorScore: number
}

export function ContributorsTab({ contributors, total, busFactorScore }: ContributorsTabProps) {
  const top = contributors[0]

  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <KpiCard label="Total Contributors" value={total} sub="All time" icon={Users} color="#0ea5e9" />
        <KpiCard
          label="Bus Factor"
          value={busFactorScore < 50 ? '⚠️ Low' : '✓ OK'}
          sub={`Score: ${busFactorScore}/100`}
          icon={Bus}
          color={busFactorScore < 50 ? '#ef4444' : '#10b981'}
        />
        <KpiCard
          label="Top Contributor"
          value={`${top?.commit_percentage ?? 0}%`}
          sub={top?.name ?? 'N/A'}
          icon={Award}
          color="#f59e0b"
        />
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-4 text-[15px] font-bold text-foreground">Contribution Distribution</h2>
          <ContributorDonutChart contributors={contributors} />
        </Card>
        <BusFactorCard contributors={contributors} busFactorScore={busFactorScore} />
      </div>

      <Card className="p-5">
        <h2 className="mb-4 text-[15px] font-bold text-foreground">All Contributors</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {contributors.map((c, i) => (
            <div
              key={c.email}
              className="flex items-center gap-3 rounded-xl border border-border bg-secondary/30 p-3"
            >
              <Avatar initials={c.avatar_initials} seed={c.email} size={40} />
              <div className="min-w-0 flex-1">
                <div className="text-sm font-semibold text-foreground">{c.name}</div>
                <div className="mb-1.5 truncate text-[11px] text-muted-foreground">{c.email}</div>
                <Progress
                  value={c.commit_percentage}
                  color={COLORS[i % COLORS.length]}
                  className="h-[3px]"
                />
              </div>
              <div className="shrink-0 text-right">
                <div className="text-sm font-bold" style={{ color: COLORS[i % COLORS.length] }}>
                  {c.commit_percentage}%
                </div>
                <div className="text-[11px] text-muted-foreground">{formatNumber(c.commit_count)}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
