import { Sparkles, AlertTriangle, CheckCircle2, Lightbulb } from 'lucide-react'
import type { AISummaryResponse } from '@/types/api'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface AISummaryCardProps {
  summary: AISummaryResponse | null
  isLoading: boolean
}

export function AISummaryCard({ summary, isLoading }: AISummaryCardProps) {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/20">
          <Sparkles className="h-4 w-4 text-primary" />
        </div>
        <div>
          <h2 className="text-[15px] font-bold text-foreground">AI Repository Summary</h2>
          <p className="text-[11px] text-muted-foreground">Generated insights</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-2.5">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-[80%]" />
          <Skeleton className="h-4 w-[90%]" />
          <Skeleton className="h-4 w-[60%]" />
        </div>
      ) : !summary ? (
        <p className="text-sm text-muted-foreground">No summary available yet.</p>
      ) : (
        <div className="flex flex-col gap-4 text-[13px] leading-relaxed">
          <p className="text-foreground/90">{summary.summary}</p>

          <div>
            <h4 className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
              Purpose
            </h4>
            <p className="text-foreground/80">{summary.purpose}</p>
          </div>

          {summary.risks.length > 0 && (
            <div>
              <h4 className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-red-400">
                <AlertTriangle className="h-3 w-3" /> Risks
              </h4>
              <ul className="space-y-1">
                {summary.risks.map((r, i) => (
                  <li key={i} className="flex gap-1.5 text-foreground/80">
                    <span className="text-red-400">•</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {summary.strengths.length > 0 && (
            <div>
              <h4 className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-emerald-400">
                <CheckCircle2 className="h-3 w-3" /> Strengths
              </h4>
              <ul className="space-y-1">
                {summary.strengths.map((s, i) => (
                  <li key={i} className="flex gap-1.5 text-foreground/80">
                    <span className="text-emerald-400">•</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {summary.recommendations.length > 0 && (
            <div>
              <h4 className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-sky-400">
                <Lightbulb className="h-3 w-3" /> Recommendations
              </h4>
              <ul className="space-y-1">
                {summary.recommendations.map((r, i) => (
                  <li key={i} className="flex gap-1.5 text-foreground/80">
                    <span className="text-sky-400">•</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
