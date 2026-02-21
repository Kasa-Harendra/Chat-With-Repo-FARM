import React, { useState } from 'react';
import { useRepoStore } from '../store/repoStore';
import { FolderTree, ChevronLeft, ChevronRight, Share2 } from 'lucide-react';
import FileTree from './FileTree';

const RightPanel = () => {
  const { fileTree } = useRepoStore();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div 
      className={`relative h-full bg-[#252526] border-l border-[#333] transition-all duration-300 ease-in-out flex flex-col ${
        isCollapsed ? 'w-12' : 'w-80'
      }`}
    >
      {/* Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -left-3 top-1/2 -translate-y-1/2 w-6 h-12 bg-[#333] border border-[#444] rounded-md flex items-center justify-center hover:bg-[#444] transition-colors z-30"
      >
        {isCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      {/* Header / Collapse Icon Strip */}
      <div className={`flex items-center gap-3 p-4 border-b border-[#333] overflow-hidden whitespace-nowrap ${isCollapsed ? 'justify-center' : ''}`}>
        <FolderTree size={20} className="text-blue-400 shrink-0" />
        {!isCollapsed && <span className="font-semibold text-sm">Explorer</span>}
      </div>

      {/* Content */}
      <div className={`flex-1 overflow-y-auto custom-scrollbar ${isCollapsed ? 'hidden' : 'block'}`}>
        <div className="p-2">
          <FileTree tree={fileTree} />
        </div>
      </div>
      
      {/* Footer Info (Optional) */}
      {!isCollapsed && fileTree.length > 0 && (
        <div className="p-3 border-t border-[#333] bg-[#1e1e1e]">
          <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-tighter">
            <Share2 size={10} />
            <span>{fileTree.length} Root Items</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default RightPanel;
