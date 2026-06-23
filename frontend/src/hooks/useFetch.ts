import { useEffect, useState, useCallback, useRef } from 'react'

interface UseFetchResult<T> {
  data: T | null
  isLoading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Generic fetch hook. Pass a function that returns a promise;
 * it re-runs whenever `deps` changes.
 */
export function useFetch<T>(
  fetchFn: () => Promise<T>,
  deps: React.DependencyList = []
): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const fetchFnRef = useRef(fetchFn)
  fetchFnRef.current = fetchFn

  const load = useCallback(() => {
    setIsLoading(true)
    setError(null)
    fetchFnRef
      .current()
      .then((result) => {
        setData(result)
        setIsLoading(false)
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : 'Something went wrong')
        setIsLoading(false)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [load])

  return { data, isLoading, error, refetch: load }
}
