import { apiClient } from './client'
import type { AnalyzeResponse, RepositoryFull, RepositoryStats } from '@/types/api'

export const repositoryApi = {
  /** Submit a GitHub URL for analysis. Returns immediately with status=pending. */
  analyze: async (url: string): Promise<AnalyzeResponse> => {
    const { data } = await apiClient.post<AnalyzeResponse>('/repositories/analyze', { url })
    return data
  },

  /** Poll this until status === 'complete' or 'failed'. */
  get: async (id: number): Promise<RepositoryFull> => {
    const { data } = await apiClient.get<RepositoryFull>(`/repositories/${id}`)
    return data
  },

  list: async (skip = 0, limit = 20): Promise<RepositoryStats[]> => {
    const { data } = await apiClient.get<RepositoryStats[]>('/repositories/', {
      params: { skip, limit },
    })
    return data
  },

  remove: async (id: number): Promise<void> => {
    await apiClient.delete(`/repositories/${id}`)
  },
}
