import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format large numbers: 1234 -> "1.2k", 1234567 -> "1.2M" */
export function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'k'
  return String(n)
}

/** Format days into "Xy Ym" */
export function formatAge(days: number): string {
  const years = Math.floor(days / 365)
  const months = Math.floor((days % 365) / 30)
  if (years === 0) return `${months}m`
  return `${years}y ${months}m`
}

/** Format ISO date string to "Jan 2024" */
export function formatMonthYear(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

/** Risk label -> Tailwind color class */
export function riskColor(label: string): string {
  switch (label) {
    case 'high': return 'text-risk-high border-risk-high/40 bg-risk-high/10'
    case 'medium': return 'text-risk-medium border-risk-medium/40 bg-risk-medium/10'
    default: return 'text-risk-low border-risk-low/40 bg-risk-low/10'
  }
}

/** Health grade -> color */
export function gradeColor(grade: string): string {
  switch (grade) {
    case 'A': return '#22c55e'
    case 'B': return '#84cc16'
    case 'C': return '#f59e0b'
    case 'D': return '#f97316'
    default: return '#ef4444'
  }
}

/** Generate initials from a name string */
export function getInitials(name: string): string {
  const parts = name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return name.slice(0, 2).toUpperCase()
}

/** Deterministic color from a string (for avatars) */
export function stringToColor(str: string): string {
  const colors = ['#7c3aed', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}
