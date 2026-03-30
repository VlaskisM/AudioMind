import { create } from 'zustand'

export type RightPanelTab = 'transcript' | 'summary' | 'key-points' | 'action-items' | 'faq'

interface WorkspaceState {
  activeTab: RightPanelTab
  setActiveTab: (tab: RightPanelTab) => void
  uploadModalOpen: boolean
  setUploadModalOpen: (open: boolean) => void
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeTab: 'transcript',
  setActiveTab: (tab) => set({ activeTab: tab }),
  uploadModalOpen: false,
  setUploadModalOpen: (open) => set({ uploadModalOpen: open }),
}))
