import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, message }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-md bg-[#252526] border border-[#333] rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center text-red-500">
              <AlertTriangle size={24} />
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-[#333] rounded-lg transition-colors text-gray-500 hover:text-white"
            >
              <X size={20} />
            </button>
          </div>

          <h3 className="text-xl font-bold text-white mb-2">{title || 'Are you sure?'}</h3>
          <p className="text-gray-400 text-sm leading-relaxed mb-8">
            {message || 'This action cannot be undone. Please confirm if you want to proceed.'}
          </p>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-[#3c3c3c] hover:bg-[#4c4c4c] text-white rounded-xl transition-all font-medium text-sm"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="flex-1 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl transition-all font-medium text-sm shadow-lg shadow-red-600/20"
            >
              Yes, Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
