import React, { useState } from 'react';
import { ChevronRight, ChevronDown, FileCode, Folder, FileJson, FileText, FileSearch } from 'lucide-react';

const FileIcon = ({ name, isDir }) => {
  if (isDir) return <Folder size={16} className="text-blue-400" />;
  
  const ext = name.split('.').pop();
  switch (ext) {
    case 'py': return <FileCode size={16} className="text-yellow-400" />;
    case 'js':
    case 'jsx':
    case 'ts':
    case 'tsx': return <FileCode size={16} className="text-blue-300" />;
    case 'json': return <FileJson size={16} className="text-orange-400" />;
    case 'md': return <FileText size={16} className="text-gray-400" />;
    default: return <FileText size={16} className="text-gray-500" />;
  }
};

const TreeNode = ({ node, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="select-none">
      <div 
        className={`flex items-center gap-1 py-1 px-2 hover:bg-[#2a2d2e] cursor-pointer rounded text-sm transition-colors`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {node.isDir && (
          <span>{isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}</span>
        )}
        {!node.isDir && <span className="w-3.5" />}
        <FileIcon name={node.name} isDir={node.isDir} />
        <span className="truncate text-gray-300">{node.name}</span>
      </div>
      
      {node.isDir && isOpen && node.children && (
        <div>
          {node.children.map((child, i) => (
            <TreeNode key={i} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

const FileTree = ({ tree }) => {
  if (!tree || tree.length === 0) {
    return <div className="text-xs text-gray-500 italic p-4">No repository loaded</div>;
  }

  return (
    <div className="py-2">
      {tree.map((node, i) => (
        <TreeNode key={i} node={node} />
      ))}
    </div>
  );
};

export default FileTree;
