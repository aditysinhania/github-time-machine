import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import type { Contributor } from '@/types/api'
import { Avatar } from '@/components/ui/avatar'

const COLORS = ['#7c3aed', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

interface ContributorDonutChartProps {
  contributors: Contributor[]
  maxSlices?: number
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as Contributor
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold text-foreground">{d.name}</div>
      <div className="text-muted-foreground">
        {d.commit_count} commits ({d.commit_percentage}%)
      </div>
    </div>
  )
}

export function ContributorDonutChart({ contributors, maxSlices = 5 }: ContributorDonutChartProps) {
  const top = contributors.slice(0, maxSlices)

  return (
    <div className="flex items-center gap-5">
      <div className="h-[160px] w-[160px] shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={top}
              dataKey="commit_count"
              nameKey="name"
              innerRadius="68%"
              outerRadius="100%"
              paddingAngle={2}
              strokeWidth={0}
            >
              {top.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex flex-1 flex-col gap-2.5">
        {top.map((c) => (
          <div key={c.email} className="flex items-center gap-2">
            <Avatar initials={c.avatar_initials} seed={c.email} size={22} />
            <span className="flex-1 truncate text-[12px] text-foreground">{c.name}</span>
            <span className="text-[11px] font-medium text-muted-foreground">
              {c.commit_percentage}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
