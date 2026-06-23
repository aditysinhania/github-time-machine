import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { TimelineBucket } from '@/types/api'

interface CommitTimelineChartProps {
  data: TimelineBucket[]
  height?: number
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as TimelineBucket
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <div className="mb-1 font-semibold text-foreground">{d.label}</div>
      <div className="text-muted-foreground">
        <span className="text-primary font-medium">{d.commits}</span> commits ·{' '}
        <span className="text-emerald-400">+{d.insertions}</span>{' '}
        <span className="text-red-400">-{d.deletions}</span>
      </div>
      <div className="text-muted-foreground">{d.unique_authors} contributors</div>
    </div>
  )
}

export function CommitTimelineChart({ data, height = 240 }: CommitTimelineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
          axisLine={{ stroke: 'hsl(var(--border))' }}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'hsl(var(--secondary))', opacity: 0.4 }} />
        <Bar dataKey="commits" fill="#7c3aed" radius={[3, 3, 0, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  )
}
