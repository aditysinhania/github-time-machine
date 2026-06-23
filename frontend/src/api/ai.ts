import { apiClient } from './client'
import type { AISummaryResponse, ChatRequest, ChatResponse } from '@/types/api'

export const aiApi = {
  summary: async (repoId: number, refresh = false): Promise<AISummaryResponse> => {
    const { data } = await apiClient.get<AISummaryResponse>(
      `/repositories/${repoId}/ai/summary`,
      { params: { refresh } }
    )
    return data
  },

  chat: async (repoId: number, body: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>(
      `/repositories/${repoId}/ai/chat`,
      body
    )
    return data
  },
}
