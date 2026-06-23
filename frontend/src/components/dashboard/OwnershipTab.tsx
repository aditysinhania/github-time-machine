import { Box, MapPin, Ghost } from 'lucide-react'
import type { ModuleOwnership } from '@/types/api'
import { KpiCard } from './KpiCard'
import { OwnershipCard } from './OwnershipCard'

interface OwnershipTabProps {
  modules?: ModuleOwnership[]
}

export function OwnershipTab({ modules = []}: OwnershipTabProps) {
  const avgOwnership =
    modules.length > 0
      ? Math.round(
          modules.reduce((sum, m) => sum + (m.owners[0]?.percentage ?? 0), 0) / modules.length
        )
      : 0
  const orphaned = modules.filter((m) => !m.owners[0] || m.owners[0].percentage < 30).length

  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <KpiCard label="Modules Tracked" value={modules.length} sub="Code areas" icon={Box} color="#7c3aed" />
        <KpiCard label="Avg Ownership" value={`${avgOwnership}%`} sub="Primary owner %" icon={MapPin} color="#0ea5e9" />
        <KpiCard label="Orphaned Modules" value={orphaned} sub="No clear owner" icon={Ghost} color="#10b981" />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {modules.length === 0 ? (
          <p className="col-span-full py-8 text-center text-sm text-muted-foreground">
            No module ownership data available yet.
          </p>
        ) : (
          modules.map((m) => <OwnershipCard key={m.module} module={m} />)
        )}
      </div>
    </div>
  )
}
