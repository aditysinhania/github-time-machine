import { GitCommit, Users, Clock, Files } from 'lucide-react'
import type { RepositoryFull, TimelineBucket, Contributor, HotspotFile } from '@/types/api'
import { Card } from '@/components/ui/card'
import { KpiCard } from './KpiCard'
import { HealthRing } from './HealthRing'
import { CommitTimelineChart } from './CommitTimelineChart'
import { ContributorDonutChart } from './ContributorDonutChart'
import { HotspotRow } from './HotspotRow'
import { Progress } from '@/components/ui/progress'
import { formatNumber, formatAge } from '@/lib/utils'

interface OverviewTabProps {
  repo: RepositoryFull
  timeline: TimelineBucket[]
  contributors: Contributor[]
  topHotspots: HotspotFile[]
}

const SUB_SCORES = (repo: RepositoryFull) => [
  { label: 'Bus Factor', value: repo.bus_factor_score ?? 0, color: '#ef4444' },
  { label: 'Consistency', value: repo.consistency_score ?? 0, color: '#7c3aed' },
  { label: 'Diversity', value: repo.diversity_score ?? 0, color: '#0ea5e9' },
  { label: 'Hotspots', value: repo.hotspot_score ?? 0, color: '#f59e0b' },
]

export function OverviewTab({ repo, timeline, contributors, topHotspots }: OverviewTabProps) {
  const grade = scoreToGrade(repo.health_score ?? 0)
  const maxChanges = Math.max(...topHotspots.map((h) => h.change_count), 1)

  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <KpiCard label="Total Commits" value={formatNumber(repo.total_commits)} sub="All time" icon={GitCommit} color="#7c3aed" />
        <KpiCard label="Contributors" value={repo.total_contributors} sub="Unique authors" icon={Users} color="#0ea5e9" />
        <KpiCard label="Repository Age" value={formatAge(repo.age_days)} sub="Since first commit" icon={Clock} color="#10b981" />
        <KpiCard label="Total Files" value={formatNumber(repo.total_files)} sub="Tracked files" icon={Files} color="#f59e0b" />
      </div>

      {/* Commit chart + health */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[2fr_1fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-[15px] font-bold text-foreground">Commit Activity</h2>
              <p className="text-xs text-muted-foreground">Monthly commit frequency</p>
            </div>
          </div>
          <CommitTimelineChart data={timeline} />
        </Card>

        <Card className="p-5">
          <div className="mb-4">
            <h2 className="text-[15px] font-bold text-foreground">Health Score</h2>
            <p className="text-xs text-muted-foreground">AI-computed quality index</p>
          </div>
          <div className="mb-4 flex justify-center">
            <HealthRing score={repo.health_score ?? 0} grade={grade} />
          </div>
          <div className="flex flex-col gap-2.5">
            {SUB_SCORES(repo).map((s) => (
              <div key={s.label}>
                <div className="mb-1 flex justify-between">
                  <span className="text-[11px] text-muted-foreground">{s.label}</span>
                  <span className="text-[11px] font-semibold" style={{ color: s.color }}>
                    {s.value}
                  </span>
                </div>
                <Progress value={s.value} color={s.color} className="h-1" />
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Contributors + hotspots */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-4 text-[15px] font-bold text-foreground">Top Contributors</h2>
          <ContributorDonutChart contributors={contributors} />
        </Card>

        <Card className="p-5">
          <h2 className="mb-4 text-[15px] font-bold text-foreground">High-Risk Files</h2>
          <div className="flex flex-col gap-2.5">
            {topHotspots.length === 0 ? (
              <p className="text-sm text-muted-foreground">No high-risk files detected.</p>
            ) : (
              topHotspots.slice(0, 4).map((h) => (
                <HotspotRow key={h.filepath} file={h} maxChanges={maxChanges} />
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

function scoreToGrade(score: number): string {
  if (score >= 90) return 'A'
  if (score >= 80) return 'B'
  if (score >= 65) return 'C'
  if (score >= 50) return 'D'
  return 'F'
}
