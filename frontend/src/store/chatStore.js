import { create } from 'zustand'

export const useChatStore = create((set) => ({
  messages: [],
  isStreaming: false,
  
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  
  updateLastMessage: (content) => set((state) => {
    const newMessages = [...state.messages]
    if (newMessages.length > 0) {
      newMessages[newMessages.length - 1].content += content
    }
    return { messages: newMessages }
  }),
  
  setIsStreaming: (streaming) => set({ isStreaming: streaming }),
  clearChat: () => set({ messages: [] }),
}))
