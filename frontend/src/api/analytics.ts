import { apiClient } from './client'
import type {
  ContributorsResponse,
  TimelineResponse,
  MilestonesResponse,
  HotspotsResponse,
  OwnershipResponse,
  HealthResponse,
  Granularity,
  RiskLabel,
} from '@/types/api'

export const analyticsApi = {
  contributors: async (repoId: number, limit = 20): Promise<ContributorsResponse> => {
    const { data } = await apiClient.get<ContributorsResponse>(
      `/repositories/${repoId}/contributors`,
      { params: { limit } }
    )
    return data
  },

  timeline: async (repoId: number, granularity: Granularity = 'month'): Promise<TimelineResponse> => {
    const { data } = await apiClient.get<TimelineResponse>(
      `/repositories/${repoId}/timeline`,
      { params: { granularity } }
    )
    return data
  },

  milestones: async (repoId: number): Promise<MilestonesResponse> => {
    const { data } = await apiClient.get<MilestonesResponse>(
      `/repositories/${repoId}/milestones`
    )
    return data
  },

  hotspots: async (repoId: number, risk?: RiskLabel, limit = 50): Promise<HotspotsResponse> => {
    const { data } = await apiClient.get<HotspotsResponse>(
      `/repositories/${repoId}/hotspots`,
      { params: { risk, limit } }
    )
    return data
  },

  ownership: async (repoId: number): Promise<OwnershipResponse> => {
    const { data } = await apiClient.get<OwnershipResponse>(
      `/repositories/${repoId}/ownership`
    )
    return data
  },

  health: async (repoId: number): Promise<HealthResponse> => {
    const { data } = await apiClient.get<HealthResponse>(
      `/repositories/${repoId}/health`
    )
    return data
  },
}
