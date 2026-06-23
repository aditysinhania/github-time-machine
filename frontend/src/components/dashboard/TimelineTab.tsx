import { History } from 'lucide-react'
import type { TimelineBucket, Milestone, Granularity } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CommitTimelineChart } from './CommitTimelineChart'
import { EvolutionTimeline } from './EvolutionTimeline'

interface TimelineTabProps {
  milestones: Milestone[]
  timeline: TimelineBucket[]
  granularity: Granularity
  onGranularityChange: (g: Granularity) => void
}

export function TimelineTab({
  milestones,
  timeline,
  granularity,
  onGranularityChange,
}: TimelineTabProps) {
  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      <Card className="p-5">
        <div className="mb-4 flex items-center gap-2">
          <History className="h-[18px] w-[18px] text-primary" />
          <div>
            <h2 className="text-[15px] font-bold text-foreground">Project Evolution</h2>
            <p className="text-xs text-muted-foreground">
              Key milestones extracted from commit history
            </p>
          </div>
        </div>
        <EvolutionTimeline milestones={milestones} />
      </Card>

      <Card className="p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-[15px] font-bold text-foreground">Commit Activity — Full History</h2>
            <p className="text-xs text-muted-foreground">
              Commit frequency over the repository's lifetime
            </p>
          </div>
          <Tabs value={granularity} onValueChange={(v) => onGranularityChange(v as Granularity)}>
            <TabsList>
              <TabsTrigger value="week">Week</TabsTrigger>
              <TabsTrigger value="month">Month</TabsTrigger>
              <TabsTrigger value="year">Year</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        <CommitTimelineChart data={timeline} height={280} />
      </Card>
    </div>
  )
}
