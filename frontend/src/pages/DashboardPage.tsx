import { useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { LayoutDashboard, Users, Flame, MapPin, History as HistoryIcon } from 'lucide-react'

import { useRepositoryPoll } from '@/hooks/useRepositoryPoll'
import { useFetch } from '@/hooks/useFetch'
import { analyticsApi } from '@/api'
import type { Granularity } from '@/types/api'

import { Navbar } from '@/components/layout/Navbar'
import { PageShell } from '@/components/layout/PageShell'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { KpiCardSkeleton } from '@/components/dashboard/KpiCard'

import { OverviewTab } from '@/components/dashboard/OverviewTab'
import { ContributorsTab } from '@/components/dashboard/ContributorsTab'
import { HotspotsTab } from '@/components/dashboard/HotspotsTab'
import { OwnershipTab } from '@/components/dashboard/OwnershipTab'
import { TimelineTab } from '@/components/dashboard/TimelineTab'

import { AnalyzingScreen } from './AnalyzingScreen'
import { FailedScreen } from './FailedScreen'

export function DashboardPage() {
  const { repoId } = useParams<{ repoId: string }>()
  const id = repoId ? Number(repoId) : null
  const [granularity, setGranularity] = useState<Granularity>('month')

  const { repository, status, isLoading: repoLoading } = useRepositoryPoll(id)

  const isComplete = status === 'complete'

  const { data: contributorsData, isLoading: contribLoading } = useFetch(
    () => analyticsApi.contributors(id!, 20),
    [id, isComplete]
  )

  const { data: timelineData, isLoading: timelineLoading } = useFetch(
    () => analyticsApi.timeline(id!, granularity),
    [id, isComplete, granularity]
  )

  const { data: milestonesData } = useFetch(
    () => analyticsApi.milestones(id!),
    [id, isComplete]
  )

  const { data: hotspotsData, isLoading: hotspotsLoading } = useFetch(
    () => analyticsApi.hotspots(id!, undefined, 50),
    [id, isComplete]
  )

  const { data: ownershipData } = useFetch(
    () => analyticsApi.ownership(id!),
    [id, isComplete]
  )

  const handleGranularityChange = useCallback((g: Granularity) => setGranularity(g), [])

  // ── Guard states ──────────────────────────────────────────
  if (!id) {
    return <FailedScreen message="Invalid repository ID." />
  }

  if (status === 'failed') {
    return <FailedScreen message={repository?.error_message ?? undefined} />
  }

  if (!isComplete || repoLoading || !repository) {
    return <AnalyzingScreen status={status ?? 'pending'} fullName={repository?.full_name} />
  }

  // ── Loaded state ──────────────────────────────────────────
  const isDataLoading = contribLoading || timelineLoading || hotspotsLoading

  return (
    <div className="min-h-screen">
      <Navbar repository={repository} activePage="dashboard" />
      <PageShell>
        <Tabs defaultValue="overview">
          <TabsList className="mb-1">
            <TabsTrigger value="overview">
              <LayoutDashboard className="h-3.5 w-3.5" /> Overview
            </TabsTrigger>
            <TabsTrigger value="contributors">
              <Users className="h-3.5 w-3.5" /> Contributors
            </TabsTrigger>
            <TabsTrigger value="hotspots">
              <Flame className="h-3.5 w-3.5" /> Hotspots
            </TabsTrigger>
            <TabsTrigger value="ownership">
              <MapPin className="h-3.5 w-3.5" /> Ownership
            </TabsTrigger>
            <TabsTrigger value="timeline">
              <HistoryIcon className="h-3.5 w-3.5" /> Timeline
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            {isDataLoading || !contributorsData || !timelineData || !hotspotsData ? (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {Array.from({ length: 4 }).map((_, i) => <KpiCardSkeleton key={i} />)}
              </div>
            ) : (
              <OverviewTab
                repo={repository}
                timeline={timelineData.buckets}
                contributors={contributorsData.contributors}
                topHotspots={(hotspotsData?.hotspots ?? []).filter((h) => h.risk_label === 'high')}
              />
            )}
          </TabsContent>

          <TabsContent value="contributors">
            {!contributorsData ? (
              <p className="text-sm text-muted-foreground">Loading contributors…</p>
            ) : (
              <ContributorsTab
                contributors={contributorsData.contributors}
                total={contributorsData.total}
                busFactorScore={contributorsData.bus_factor_score}
              />
            )}
          </TabsContent>

          <TabsContent value="hotspots">
            {!hotspotsData ? (
              <p className="text-sm text-muted-foreground">Loading hotspots…</p>
            ) : (
              <HotspotsTab
                hotspots={hotspotsData.hotspots}
                highRiskCount={hotspotsData.high_risk_count}
                mediumRiskCount={hotspotsData.medium_risk_count}
              />
            )}
          </TabsContent>

          <TabsContent value="ownership">
            {!ownershipData ? (
              <p className="text-sm text-muted-foreground">Loading ownership data…</p>
            ) : (
              <OwnershipTab modules={ownershipData?.modules ?? []} />
            )}
          </TabsContent>

          <TabsContent value="timeline">
            {!timelineData ? (
              <p className="text-sm text-muted-foreground">Loading timeline…</p>
            ) : (
              <TimelineTab
                milestones={milestonesData?.milestones ?? []}
                timeline={timelineData.buckets}
                granularity={granularity}
                onGranularityChange={handleGranularityChange}
              />
            )}
          </TabsContent>
        </Tabs>
      </PageShell>
    </div>
  )
}
