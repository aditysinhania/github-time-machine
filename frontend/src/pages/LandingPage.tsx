import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Github, Telescope, Loader2, GitBranch, Users, ShieldCheck, Sparkles } from 'lucide-react'
import { repositoryApi } from '@/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const EXAMPLES = [
  'https://github.com/vercel/next.js',
  'https://github.com/facebook/react',
  'https://github.com/microsoft/vscode',
  'https://github.com/torvalds/linux',
]

const FEATURES = [
  {
    icon: GitBranch,
    title: 'Commit History',
    desc: 'Years of evolution mapped into a clear timeline in seconds.',
  },
  {
    icon: Users,
    title: 'Team Intelligence',
    desc: 'See who owns what, and identify bus-factor risk before it bites.',
  },
  {
    icon: ShieldCheck,
    title: 'Health Score',
    desc: 'AI-generated risk and technical debt analysis out of 100.',
  },
]

export function LandingPage() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleAnalyze = async (overrideUrl?: string) => {
    const target = (overrideUrl ?? url).trim()
    if (!target) return
    if (!target.includes('github.com')) {
      setError('Please enter a valid GitHub repository URL.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const res = await repositoryApi.analyze(target)
      navigate(`/dashboard/${res.repository_id}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start analysis.')
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between border-b border-border px-10 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-sky-500">
            <Github className="h-[18px] w-[18px] text-white" />
          </div>
          <span className="text-[16px] font-bold text-foreground">GitHub Time Machine</span>
        </div>
        <div className="flex gap-2">
          <Badge variant="success">AI-Powered</Badge>
          <Badge variant="info">Beta</Badge>
        </div>
      </nav>

      {/* Hero */}
      <div className="flex flex-1 flex-col items-center justify-center gap-10 px-10 py-16 text-center">
        <div className="max-w-[640px]">
          <div className="mb-6 inline-flex items-center gap-1.5 rounded-full border border-primary/40 bg-primary/10 px-3.5 py-1.5">
            <Sparkles className="h-3.5 w-3.5 text-violet-300" />
            <span className="text-xs font-semibold text-violet-300">
              AI Repository Intelligence Platform
            </span>
          </div>
          <h1 className="mb-4 text-[56px] font-extrabold leading-[1.1] tracking-tight text-foreground">
            Understand any
            <br />
            <span className="gradient-text">repo in seconds</span>
          </h1>
          <p className="mx-auto max-w-[500px] text-lg leading-relaxed text-muted-foreground">
            Turn thousands of commits into actionable insights. Identify risks, ownership,
            and milestones instantly.
          </p>
        </div>

        <div className="w-full max-w-[600px]">
          <div className="mb-4 flex gap-2 rounded-xl border border-border bg-card p-1.5">
            <Input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              placeholder="https://github.com/owner/repository"
              className="h-11 border-0 bg-transparent text-sm focus-visible:ring-0"
            />
            <Button
              variant="gradient"
              size="lg"
              className="h-11 shrink-0"
              onClick={() => handleAnalyze()}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Telescope className="h-4 w-4" />
                  Analyze
                </>
              )}
            </Button>
          </div>

          {error && <p className="mb-3 text-sm text-red-400">{error}</p>}

          <div className="flex flex-wrap justify-center gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => {
                  setUrl(ex)
                  handleAnalyze(ex)
                }}
                className="flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
              >
                <Github className="h-3.5 w-3.5" />
                {ex.split('/').slice(-1)[0]}
              </button>
            ))}
          </div>
        </div>

        <div className="grid w-full max-w-[700px] grid-cols-1 gap-4 sm:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <Card key={title} className="p-5 text-left">
              <Icon className="mb-3 h-6 w-6 text-primary" />
              <div className="mb-1 text-sm font-semibold text-foreground">{title}</div>
              <div className="text-xs leading-relaxed text-muted-foreground">{desc}</div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
