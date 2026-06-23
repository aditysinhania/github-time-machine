import { useParams } from 'react-router-dom'
import { CheckCircle2, XCircle } from 'lucide-react'

import { useRepositoryPoll } from '@/hooks/useRepositoryPoll'
import { useFetch } from '@/hooks/useFetch'
import { aiApi, analyticsApi } from '@/api'

import { Navbar } from '@/components/layout/Navbar'
import { PageShell } from '@/components/layout/PageShell'
import { Card } from '@/components/ui/card'
import { AISummaryCard } from '@/components/dashboard/AISummaryCard'
import { ChatPanel } from '@/components/dashboard/ChatPanel'

import { AnalyzingScreen } from './AnalyzingScreen'
import { FailedScreen } from './FailedScreen'

export function InsightsPage() {
  const { repoId } = useParams<{ repoId: string }>()
  const id = repoId ? Number(repoId) : null

  const { repository, status, isLoading: repoLoading } = useRepositoryPoll(id)
  const isComplete = status === 'complete'

  const { data: summary, isLoading: summaryLoading } = useFetch(
    () => aiApi.summary(id!),
    [id, isComplete]
  )

  const { data: hotspotsData } = useFetch(
    () => analyticsApi.hotspots(id!, 'high', 10),
    [id, isComplete]
  )

  if (!id) return <FailedScreen message="Invalid repository ID." />
  if (status === 'failed') return <FailedScreen message={repository?.error_message ?? undefined} />
  if (!isComplete || repoLoading || !repository) {
    return <AnalyzingScreen status={status ?? 'pending'} fullName={repository?.full_name} />
  }

  const riskChecks = [
    {
      name: 'Critical Bus Factor',
      isRisk: (repository.bus_factor_score ?? 100) < 50,
      desc: 'Concentrated knowledge in 1-2 people',
    },
    {
      name: 'High-risk Hotspots',
      isRisk: (hotspotsData?.high_risk_count ?? 0) > 3,
      desc: 'Multiple volatile files detected',
    },
    {
      name: 'Consistency',
      isRisk: (repository.consistency_score ?? 100) < 60,
      desc: 'Irregular commit patterns',
    },
    {
      name: 'Contributor Diversity',
      isRisk: (repository.diversity_score ?? 100) < 50,
      desc: 'Limited team diversity',
    },
  ]

  return (
    <div className="min-h-screen">
      <Navbar repository={repository} activePage="insights" />
      <PageShell>
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <div className="flex flex-col gap-5">
            <AISummaryCard summary={summary} isLoading={summaryLoading} />

            <Card className="p-5">
              <h2 className="mb-4 text-[15px] font-bold text-foreground">Risk Summary</h2>
              <div className="flex flex-col gap-2.5">
                {riskChecks.map((check) => (
                  <div key={check.name} className="flex gap-3 rounded-lg bg-secondary/40 p-2.5">
                    <div
                      className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                        check.isRisk
                          ? 'border-red-500/40 bg-red-500/15'
                          : 'border-emerald-500/40 bg-emerald-500/15'
                      }`}
                    >
                      {check.isRisk ? (
                        <XCircle className="h-3 w-3 text-red-400" />
                      ) : (
                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      )}
                    </div>
                    <div>
                      <div className="text-[13px] font-medium text-foreground">{check.name}</div>
                      <div className="text-[11px] text-muted-foreground">{check.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card className="flex flex-col p-5">
            <div className="mb-4">
              <h2 className="text-[15px] font-bold text-foreground">Ask AI</h2>
              <p className="text-[11px] text-muted-foreground">Natural language queries</p>
            </div>
            <div className="flex-1">
              <ChatPanel repoId={id} repoName={repository.full_name} />
            </div>
          </Card>
        </div>
      </PageShell>
    </div>
  )
}
