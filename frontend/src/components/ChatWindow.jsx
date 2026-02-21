import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2, Cpu, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useChatStore } from '../store/chatStore';
import { useRepoStore } from '../store/repoStore';
import MessageBubble from './MessageBubble';
import axios from 'axios';
import toast from 'react-hot-toast';

const ChatWindow = () => {
  const [input, setInput] = useState('');
  const { messages, addMessage, updateLastMessage, isStreaming, setIsStreaming, clearChat } = useChatStore();
  const { processingStatus, setProcessingStatus } = useRepoStore();
  const scrollRef = useRef(null);

  // Automatic scrolling disabled to keep viewpoint stable during streaming as per user preference

  useEffect(() => {
    let interval;
    if (processingStatus === 'processing') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get('/api/repo/status');
          if (res.data.status === 'completed') {
            setProcessingStatus('completed');
            toast.success('RAG Pipeline Ready!', { id: 'rag-status' });
            clearInterval(interval);
          } else if (res.data.status === 'failed') {
            setProcessingStatus('failed');
            toast.error('Processing failed.', { id: 'rag-status' });
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Status check failed", err);
        }
      }, 3000);
      
      // Initial loading toast
      toast.loading('Processing repository documents...', { id: 'rag-status' });
    }
    return () => clearInterval(interval);
  }, [processingStatus, setProcessingStatus]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = { role: 'user', content: input };
    addMessage(userMessage);
    setInput('');
    setIsStreaming(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });

      if (!response.ok) {
        if (response.status === 429) {
          toast.error('Too many requests. Please wait a minute.');
          throw new Error('Rate limit exceeded');
        }
        throw new Error('Chat failed');
      }

      const aiMessage = { role: 'assistant', content: '' };
      addMessage(aiMessage);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              updateLastMessage(data.content);
            } catch (e) {
              console.error("Error parsing SSE", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error", error);
      if (error.message !== 'Rate limit exceeded') {
        toast.error('Failed to get a response. Please try again.');
        addMessage({ role: 'assistant', content: 'Sorry, I encountered an error processing your request.' });
      }
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full max-w-4xl">
      <header className="flex items-center justify-between px-6 py-4 border-b border-[#333]">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600/20 rounded-lg">
            <Cpu className="text-blue-500" size={20} />
          </div>
          <div>
            <h2 className="font-semibold">Repository AI</h2>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">GPT-OSS:20B • RAG Pipeline Active</p>
          </div>
        </div>
        <button 
          onClick={clearChat}
          className="p-2 hover:bg-[#333] rounded-full transition-colors text-gray-400 flex items-center gap-2 text-sm"
        >
          <Trash2 size={16} />
        </button>
      </header>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide relative">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
            <div className="w-16 h-16 bg-blue-600/10 rounded-full flex items-center justify-center">
              <Bot size={32} className="text-blue-500" />
            </div>
            <div>
              <h3 className="text-lg font-medium">Welcome to ChatWithRepo</h3>
              <p className="text-sm max-w-xs mx-auto">Load a repository and start asking questions about the codebase.</p>
            </div>
          </div>
        ) : (
          messages.map((m, i) => <MessageBubble key={i} message={m} />)
        )}
      </div>

      <div className="p-6">
        <div className="relative group">
          <textarea
            className="w-full bg-[#2d2d2d] border border-[#444] rounded-xl px-4 py-4 pr-14 outline-none focus:ring-1 focus:ring-blue-500 transition-all resize-none shadow-lg text-sm"
            placeholder="Ask anything about the code..."
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="absolute right-3 bottom-3 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-[#3c3c3c] disabled:text-gray-500 rounded-lg transition-all shadow-md group-hover:scale-105"
          >
            <Send size={18} />
          </button>
        </div>
        <p className="text-[10px] text-center text-gray-500 mt-2">Press Enter to send • Shift + Enter for new line</p>
      </div>
    </div>
  );
};

export default ChatWindow;
