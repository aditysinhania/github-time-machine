import { useEffect, useRef, useState, useCallback } from 'react'
import { repositoryApi } from '@/api'
import type { RepositoryFull, AnalysisStatus } from '@/types/api'

interface UseRepositoryPollResult {
  repository: RepositoryFull | null
  status: AnalysisStatus | null
  error: string | null
  isLoading: boolean
}

/**
 * Polls GET /repositories/{id} every `intervalMs` until status is
 * 'complete' or 'failed'. Stops polling automatically.
 */
export function useRepositoryPoll(
  repoId: number | null,
  intervalMs = 2000
): UseRepositoryPollResult {
  const [repository, setRepository] = useState<RepositoryFull | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchOnce = useCallback(async () => {
    if (repoId === null) return
    try {
      const data = await repositoryApi.get(repoId)
      setRepository(data)
      setError(null)

      if (data.status === 'complete' || data.status === 'failed') {
        setIsLoading(false)
        if (timerRef.current) {
          clearInterval(timerRef.current)
          timerRef.current = null
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch repository')
      setIsLoading(false)
    }
  }, [repoId])

  useEffect(() => {
    if (repoId === null) return
    setIsLoading(true)
    fetchOnce()

    timerRef.current = setInterval(fetchOnce, intervalMs)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repoId, intervalMs])

  return {
    repository,
    status: repository?.status ?? null,
    error,
    isLoading,
  }
}
