import { FileCode2 } from 'lucide-react'
import type { HotspotFile } from '@/types/api'
import { Badge } from '@/components/ui/badge'

const RISK_COLOR: Record<string, string> = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#22c55e',
}

const RISK_BADGE_VARIANT: Record<string, 'danger' | 'warning' | 'success'> = {
  high: 'danger',
  medium: 'warning',
  low: 'success',
}

interface HotspotRowProps {
  file: HotspotFile
  maxChanges: number
}

export function HotspotRow({ file, maxChanges }: HotspotRowProps) {
  const color = RISK_COLOR[file.risk_label]
  const widthPct = Math.max(4, (file.change_count / maxChanges) * 100)

  return (
    <div
      className="flex items-center gap-3 rounded-lg border p-3"
      style={{ borderColor: `${color}33`, backgroundColor: 'hsl(var(--secondary)/0.4)' }}
    >
      <div className="h-9 w-1 shrink-0 rounded" style={{ backgroundColor: color }} />
      <div
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
        style={{ backgroundColor: `${color}22` }}
      >
        <FileCode2 className="h-4 w-4" style={{ color }} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate font-mono text-[12.5px] font-medium text-foreground">
          {file.filepath}
        </div>
        <div className="truncate text-[11px] text-muted-foreground">{file.risk_reason}</div>
        <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full transition-all"
            style={{ width: `${widthPct}%`, backgroundColor: color }}
          />
        </div>
      </div>
      <div className="flex shrink-0 flex-col items-end gap-1">
        <span className="text-base font-bold" style={{ color }}>
          {file.change_count}
        </span>
        <Badge variant={RISK_BADGE_VARIANT[file.risk_label]} className="px-1.5 py-0 text-[9px]">
          {file.risk_label}
        </Badge>
      </div>
    </div>
  )
}
