import React, { useState } from 'react';
import { useRepoStore } from '../store/repoStore';
import { Github, Settings, Play, CheckCircle, Trash2 } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import ConfirmationModal from './ConfirmationModal';

const categories = [
  "Programming", "Data", "Documentation", "Configuration", "Build", "Additional"
];

const Sidebar = () => {
  const { 
    repoUrl, setRepoUrl, 
    branch, setBranch, 
    fileTree, setFileTree,
    isLoading, setIsLoading,
    isProcessing, setIsProcessing,
    processingStatus, setProcessingStatus,
    selectedCategories, setSelectedCategories,
    resetStore
  } = useRepoStore();

  const [isResetModalOpen, setIsResetModalOpen] = useState(false);

  const handleLoad = async () => {
    setIsLoading(true);
    setProcessingStatus('idle'); // Reset status on load
    try {
      const response = await axios.post('/api/repo/load', { url: repoUrl, branch });
      setFileTree(response.data.file_tree);
      toast.success('Repository loaded successfully!');
    } catch (error) {
      console.error("Failed to load repo", error);
      toast.error('Failed to load repository. Check the URL or branch.');
    } finally {
      setIsLoading(false);
    }
  };

  const confirmReset = async () => {
    try {
      await axios.delete('/api/repo/reset');
      resetStore();
      toast.success('Session reset successfully');
    } catch (error) {
      console.error("Failed to reset session", error);
      toast.error("Failed to reset session. Local data may still exist.");
    }
  };

  const handleProcess = async () => {
    setIsProcessing(true);
    setProcessingStatus('processing');
    toast.promise(
      axios.post('/api/repo/process', { selected_extensions: [".py", ".js", ".md", ".ipynb", ".ts", ".tsx", ".jsx"] }),
      {
        loading: 'Starting RAG pipeline...',
        success: 'Processing started!',
        error: 'Failed to start processing.',
      }
    ).catch(error => {
      console.error("Failed to process repo", error);
      setProcessingStatus('failed');
    });
    setIsProcessing(false);
  };

  const toggleCategory = (cat) => {
    if (selectedCategories.includes(cat)) {
      setSelectedCategories(selectedCategories.filter(c => c !== cat));
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  return (
    <div className="w-80 bg-[#252526] h-full flex flex-col border-r border-[#333] selection:bg-[#264f78]">
      <div className="p-4 space-y-4">
        <div className="flex items-center gap-2 text-xl font-bold mb-4">
          <Github size={24} />
          <span>ChatWithRepo</span>
        </div>

        <div className="space-y-2">
          <label className="text-xs uppercase text-gray-400 font-semibold">Repository URL</label>
          <input 
            type="text"
            className="w-full bg-[#3c3c3c] rounded px-3 py-2 outline-none focus:ring-1 focus:ring-blue-500 text-sm"
            placeholder="https://github.com/user/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs uppercase text-gray-400 font-semibold">Branch</label>
          <input 
            type="text"
            className="w-full bg-[#3c3c3c] rounded px-3 py-2 outline-none focus:ring-1 focus:ring-blue-500 text-sm"
            placeholder="main"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
          />
        </div>

        <button 
          onClick={handleLoad}
          disabled={isLoading || !repoUrl}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 rounded py-2 transition-colors text-sm font-medium flex items-center justify-center gap-2"
        >
          {isLoading ? "Loading..." : "Load Repository"}
        </button>

        <div className="border-t border-[#333] pt-4">
          <label className="text-xs uppercase text-gray-400 font-semibold mb-2 block">Filters</label>
          <div className="grid grid-cols-2 gap-2">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => toggleCategory(cat)}
                className={`text-[10px] px-2 py-1 rounded border ${
                  selectedCategories.includes(cat) 
                  ? 'bg-blue-600/20 border-blue-500 text-blue-400' 
                  : 'bg-transparent border-[#444] text-gray-400'
                } transition-all`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <button 
          onClick={handleProcess}
          disabled={isProcessing || !fileTree.length}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-800 rounded py-2 transition-colors text-sm font-medium flex items-center justify-center gap-2"
        >
          <Play size={16} />
          {isProcessing ? "Processing..." : "Start RAG Pipeline"}
        </button>

        <button 
          onClick={() => setIsResetModalOpen(true)}
          className="w-full border border-red-500/50 text-red-500 hover:bg-red-500/10 rounded py-2 transition-all text-sm font-medium flex items-center justify-center gap-2 mt-4"
        >
          <Trash2 size={16} />
          Reset Session
        </button>
      </div>

      <ConfirmationModal 
        isOpen={isResetModalOpen}
        onClose={() => setIsResetModalOpen(false)}
        onConfirm={confirmReset}
        title="Clear Session Data?"
        message="This will delete the currently cloned repository and clear the vector database. You will need to reload the repository to start over."
      />
    </div>
  );
};

export default Sidebar;
