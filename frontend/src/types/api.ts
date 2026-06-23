// ── Repository ──────────────────────────────────────────────────────────────

export type AnalysisStatus = 'pending' | 'cloning' | 'analyzing' | 'complete' | 'failed'

export interface RepositoryStats {
  id: number
  url: string
  owner: string
  name: string
  full_name: string
  description: string | null
  primary_language: string | null
  status: AnalysisStatus
  total_commits: number
  total_contributors: number
  total_files: number
  first_commit_at: string | null
  last_commit_at: string | null
  age_days: number
  analyzed_at: string | null
}

export interface RepositoryFull extends RepositoryStats {
  health_score: number | null
  bus_factor_score: number | null
  consistency_score: number | null
  diversity_score: number | null
  hotspot_score: number | null
  ai_summary: string | null
  error_message?: string | null
}

export interface AnalyzeResponse {
  message: string
  repository_id: number
  status: AnalysisStatus
}

// ── Contributors ────────────────────────────────────────────────────────────

export interface Contributor {
  id: number
  name: string
  email: string
  avatar_initials: string
  commit_count: number
  commit_percentage: number
  total_insertions: number
  total_deletions: number
  files_touched: number
  first_commit_at: string | null
  last_commit_at: string | null
  active_days: number
  is_bus_risk: boolean
  rank: number
}

export interface ContributorsResponse {
  repository_id: number
  total: number
  bus_factor_score: number
  contributors: Contributor[]
}

// ── Timeline ────────────────────────────────────────────────────────────────

export type Granularity = 'week' | 'month' | 'year'

export interface TimelineBucket {
  period: string
  label: string
  commits: number
  insertions: number
  deletions: number
  unique_authors: number
}

export interface TimelineResponse {
  repository_id: number
  granularity: Granularity
  buckets: TimelineBucket[]
}

export interface Milestone {
  year: number
  month: number | null
  event: string
  type: 'birth' | 'release' | 'feature' | 'infra' | 'devops' | 'perf'
  commit_sha: string | null
  commit_message: string | null
}

export interface MilestonesResponse {
  repository_id: number
  milestones: Milestone[]
}

// ── Hotspots ────────────────────────────────────────────────────────────────

export type RiskLabel = 'high' | 'medium' | 'low'

export interface HotspotFile {
  filepath: string
  filename: string
  extension: string
  directory: string
  change_count: number
  insertions: number
  deletions: number
  unique_authors: number
  risk_score: number
  risk_label: RiskLabel
  risk_reason: string
  top_author: string
  top_author_pct: number
}

export interface HotspotsResponse {
  repository_id: number
  total_files: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  hotspots: HotspotFile[]
}

// ── Ownership ───────────────────────────────────────────────────────────────

export interface OwnerEntry {
  author: string
  email: string
  commit_count: number
  percentage: number
}

export interface ModuleOwnership {
  module: string
  total_commits: number
  owners: OwnerEntry[]
}

export interface OwnershipResponse {
  repository_id: number
  modules: ModuleOwnership[]
}

// ── Health ──────────────────────────────────────────────────────────────────

export interface HealthScoreBreakdown {
  label: string
  score: number
  weight: number
  description: string
}

export interface HealthResponse {
  repository_id: number
  health_score: number
  grade: 'A' | 'B' | 'C' | 'D' | 'F'
  breakdown: HealthScoreBreakdown[]
  summary: string
}

// ── AI ──────────────────────────────────────────────────────────────────────

export interface AISummaryResponse {
  repository_id: number
  summary: string
  purpose: string
  risks: string[]
  strengths: string[]
  recommendations: string[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  message: string
  history?: ChatMessage[]
}

export interface ChatResponse {
  repository_id: number
  answer: string
  history: ChatMessage[]
}

// ── API error shape ─────────────────────────────────────────────────────────

export interface ApiError {
  detail: string
}
