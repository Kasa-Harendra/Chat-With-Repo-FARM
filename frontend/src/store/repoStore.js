import { create } from 'zustand'

export const useRepoStore = create((set) => ({
  repoUrl: '',
  branch: 'main',
  fileTree: [],
  isLoading: false,
  isProcessing: false,
  processingStatus: 'idle',
  selectedCategories: ["Programming", "Documentation"],
  
  setRepoUrl: (url) => set({ repoUrl: url }),
  setBranch: (branch) => set({ branch }),
  setFileTree: (tree) => set({ fileTree: tree }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setIsProcessing: (processing) => set({ isProcessing: processing }),
  setProcessingStatus: (status) => set({ processingStatus: status }),
  setSelectedCategories: (categories) => set({ selectedCategories: categories }),
  resetStore: () => set({
    repoUrl: '',
    branch: 'main',
    fileTree: [],
    isLoading: false,
    isProcessing: false,
    processingStatus: 'idle'
  }),
}))
