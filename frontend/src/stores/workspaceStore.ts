import { create } from 'zustand'

export type RightPanelTab = 'transcript' | 'summary' | 'key-points' | 'action-items' | 'faq'

interface WorkspaceState {
  activeTab: RightPanelTab
  setActiveTab: (tab: RightPanelTab) => void
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeTab: 'transcript',
  setActiveTab: (tab) => set({ activeTab: tab }),
}))
