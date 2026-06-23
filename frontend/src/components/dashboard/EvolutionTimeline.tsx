import type { Milestone } from '@/types/api'
import { Badge } from '@/components/ui/badge'

const TYPE_COLOR: Record<string, string> = {
  birth: '#8b5cf6',
  release: '#0ea5e9',
  feature: '#10b981',
  infra: '#f59e0b',
  devops: '#6366f1',
  perf: '#ec4899',
}

const TYPE_LABEL: Record<string, string> = {
  birth: 'Inception',
  release: 'Release',
  feature: 'Feature',
  infra: 'Infrastructure',
  devops: 'DevOps',
  perf: 'Performance',
}

interface EvolutionTimelineProps {
  milestones: Milestone[]
}

export function EvolutionTimeline({ milestones }: EvolutionTimelineProps) {
  if (milestones.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No clear milestones detected yet. Try analyzing a repository with more history.
      </p>
    )
  }

  return (
    <div className="relative pl-8">
      <div className="absolute left-[10px] top-0 bottom-0 w-0.5 rounded bg-gradient-to-b from-violet-600 to-sky-500" />
      {milestones.map((m, i) => {
        const color = TYPE_COLOR[m.type] || '#7c3aed'
        return (
          <div key={i} className={i < milestones.length - 1 ? 'relative mb-7' : 'relative'}>
            <div
              className="absolute -left-[27px] top-1 h-3 w-3 rounded-full border-2 border-background"
              style={{ backgroundColor: color }}
            />
            <div
              className="rounded-lg border p-3.5"
              style={{ borderColor: `${color}44`, backgroundColor: 'hsl(var(--card))' }}
            >
              <div className="mb-1 flex items-center gap-2">
                <span className="text-sm font-extrabold" style={{ color }}>
                  {m.year}
                </span>
                <Badge style={{ color, borderColor: `${color}44`, backgroundColor: `${color}1a` }}>
                  {TYPE_LABEL[m.type] || m.type}
                </Badge>
              </div>
              <div className="text-sm text-foreground">{m.event}</div>
              {m.commit_sha && (
                <div className="mt-1 font-mono text-[10px] text-muted-foreground">
                  {m.commit_sha}
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
