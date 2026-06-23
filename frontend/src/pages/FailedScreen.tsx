import { useNavigate } from 'react-router-dom'
import { XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface FailedScreenProps {
  message?: string
}

export function FailedScreen({ message }: FailedScreenProps) {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 px-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-500/15">
        <XCircle className="h-8 w-8 text-red-400" />
      </div>
      <h1 className="text-2xl font-bold text-foreground">Analysis Failed</h1>
      <p className="max-w-md text-sm text-muted-foreground">
        {message || 'Something went wrong while analyzing this repository. It may be private, deleted, or too large.'}
      </p>
      <Button variant="outline" onClick={() => navigate('/')}>
        Try another repository
      </Button>
    </div>
  )
}
