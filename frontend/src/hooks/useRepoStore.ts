import { create } from 'zustand'
import type { RepositoryFull } from '@/types/api'

interface RepoStore {
  currentRepoId: number | null
  currentRepo: RepositoryFull | null
  setCurrentRepoId: (id: number | null) => void
  setCurrentRepo: (repo: RepositoryFull | null) => void
  reset: () => void
}

export const useRepoStore = create<RepoStore>((set) => ({
  currentRepoId: null,
  currentRepo: null,
  setCurrentRepoId: (id) => set({ currentRepoId: id }),
  setCurrentRepo: (repo) => set({ currentRepo: repo }),
  reset: () => set({ currentRepoId: null, currentRepo: null }),
}))
