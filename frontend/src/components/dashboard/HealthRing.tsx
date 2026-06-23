import { gradeColor } from '@/lib/utils'

interface HealthRingProps {
  score: number
  grade: string
  size?: number
}

export function HealthRing({ score, grade, size = 120 }: HealthRingProps) {
  const radius = size * 0.4
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - score / 100)
  const color = gradeColor(grade)
  const center = size / 2

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="hsl(var(--secondary))"
          strokeWidth={size * 0.083}
        />
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={size * 0.083}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-[26px] font-extrabold" style={{ color }}>
          {Math.round(score)}
        </span>
        <span className="-mt-1 text-[9px] text-muted-foreground">/ 100</span>
      </div>
    </div>
  )
}
