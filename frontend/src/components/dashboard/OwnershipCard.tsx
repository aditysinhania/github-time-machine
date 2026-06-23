import { Folder } from 'lucide-react'
import type { ModuleOwnership } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

const BAR_COLORS = ['#7c3aed', '#0ea5e9', '#6b7280']

interface OwnershipCardProps {
  module: ModuleOwnership
}

export function OwnershipCard({ module }: OwnershipCardProps) {
  const topOwners = module.owners.slice(0, 3)
  const othersPct = Math.max(
    0,
    100 - topOwners.reduce((sum, o) => sum + o.percentage, 0)
  )

  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="truncate text-sm font-bold text-foreground" title={module.module}>
          {module.module}
        </h3>
        <Folder className="h-4 w-4 shrink-0 text-primary" />
      </div>
      <div className="flex flex-col gap-2.5">
        {topOwners.map((owner, i) => (
          <div key={owner.email}>
            <div className="mb-1 flex items-center justify-between">
              <span className="truncate text-[11px] text-foreground">
                {owner.author}{' '}
                <span className="text-[10px] text-muted-foreground">
                  ({i === 0 ? 'Owner' : 'Contributor'})
                </span>
              </span>
              <span className="shrink-0 text-[11px] font-semibold" style={{ color: BAR_COLORS[i] }}>
                {owner.percentage}%
              </span>
            </div>
            <Progress
              value={owner.percentage}
              className="h-[5px]"
              color={BAR_COLORS[i]}
            />
          </div>
        ))}
        {othersPct > 0 && (
          <div className="flex items-center justify-between text-[10px] text-muted-foreground/70">
            <span>Others</span>
            <span>{othersPct.toFixed(1)}%</span>
          </div>
        )}
      </div>
    </Card>
  )
}
