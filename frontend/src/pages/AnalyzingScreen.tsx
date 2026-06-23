import { Loader2, GitBranch, Users, FileSearch, CheckCircle2 } from 'lucide-react'
import type { AnalysisStatus } from '@/types/api'

interface AnalyzingScreenProps {
  status: AnalysisStatus
  fullName?: string
}

const STAGES: { key: AnalysisStatus; label: string; icon: typeof GitBranch }[] = [
  { key: 'pending', label: 'Queued for analysis', icon: Loader2 },
  { key: 'cloning', label: 'Cloning repository', icon: GitBranch },
  { key: 'analyzing', label: 'Extracting commits & contributors', icon: Users },
  { key: 'complete', label: 'Analysis complete', icon: CheckCircle2 },
]

export function AnalyzingScreen({ status, fullName }: AnalyzingScreenProps) {
  const currentIndex = STAGES.findIndex((s) => s.key === status)

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 px-6">
      <div className="flex flex-col items-center gap-3">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15">
          <FileSearch className="h-8 w-8 animate-pulse text-primary" />
        </div>
        <h1 className="text-2xl font-bold text-foreground">
          Analyzing {fullName || 'repository'}…
        </h1>
        <p className="text-sm text-muted-foreground">
          This usually takes 10–60 seconds depending on repository size.
        </p>
      </div>

      <div className="flex w-full max-w-md flex-col gap-3">
        {STAGES.map((stage, i) => {
          const isDone = currentIndex > i || status === 'complete'
          const isActive = currentIndex === i && status !== 'complete'
          const Icon = stage.icon

          return (
            <div
              key={stage.key}
              className={`flex items-center gap-3 rounded-lg border p-3 transition-colors ${
                isDone
                  ? 'border-emerald-500/30 bg-emerald-500/5'
                  : isActive
                  ? 'border-primary/40 bg-primary/5'
                  : 'border-border bg-card/50'
              }`}
            >
              <Icon
                className={`h-4 w-4 ${
                  isDone
                    ? 'text-emerald-400'
                    : isActive
                    ? 'animate-spin text-primary'
                    : 'text-muted-foreground/40'
                }`}
              />
              <span
                className={`text-sm ${
                  isDone || isActive ? 'text-foreground' : 'text-muted-foreground/50'
                }`}
              >
                {stage.label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
