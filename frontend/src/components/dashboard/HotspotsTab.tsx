import { Flame, AlertTriangle, GitBranch } from 'lucide-react'
import type { HotspotFile } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { KpiCard } from './KpiCard'
import { HotspotRow } from './HotspotRow'

const RISK_BADGE_VARIANT = { high: 'danger', medium: 'warning', low: 'success' } as const

interface HotspotsTabProps {
  hotspots: HotspotFile[]
  highRiskCount: number
  mediumRiskCount: number
}

export function HotspotsTab({ hotspots, highRiskCount, mediumRiskCount }: HotspotsTabProps) {
  const maxChanges = Math.max(...hotspots.map((h) => h.change_count), 1)

  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <KpiCard label="High Risk Files" value={highRiskCount} sub="Immediate attention" icon={Flame} color="#ef4444" />
        <KpiCard label="Medium Risk" value={mediumRiskCount} sub="Monitor closely" icon={AlertTriangle} color="#f59e0b" />
        <KpiCard label="Most Changed" value={hotspots[0]?.change_count ?? 0} sub="Changes on top file" icon={GitBranch} color="#7c3aed" />
      </div>

      <Card className="p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-[15px] font-bold text-foreground">File Hotspot Map</h2>
            <p className="text-xs text-muted-foreground">Files ranked by change frequency and risk</p>
          </div>
          <div className="flex gap-2">
            {(['high', 'medium', 'low'] as const).map((r) => (
              <Badge key={r} variant={RISK_BADGE_VARIANT[r]}>
                {r}
              </Badge>
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2.5">
          {hotspots.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">No file data available yet.</p>
          ) : (
            hotspots.map((h) => <HotspotRow key={h.filepath} file={h} maxChanges={maxChanges} />)
          )}
        </div>
      </Card>
    </div>
  )
}
