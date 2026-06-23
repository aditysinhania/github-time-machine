import type { LucideIcon } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface KpiCardProps {
  label: string
  value: string | number
  sub?: string
  icon: LucideIcon
  color?: string
}

export function KpiCard({ label, value, sub, icon: Icon, color = '#7c3aed' }: KpiCardProps) {
  return (
    <Card className="flex flex-col gap-2 p-5">
      <div className="flex items-center gap-2">
        <div
          className="flex h-8 w-8 items-center justify-center rounded-lg"
          style={{ backgroundColor: `${color}22` }}
        >
          <Icon className="h-4 w-4" style={{ color }} />
        </div>
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
      </div>
      <div className="text-[26px] font-bold tracking-tight text-foreground">{value}</div>
      {sub && <div className="text-[11px] text-muted-foreground/70">{sub}</div>}
    </Card>
  )
}

export function KpiCardSkeleton() {
  return (
    <Card className={cn('flex flex-col gap-3 p-5')}>
      <div className="h-8 w-8 rounded-lg skeleton-pulse" />
      <div className="h-7 w-20 rounded skeleton-pulse" />
      <div className="h-3 w-24 rounded skeleton-pulse" />
    </Card>
  )
}
