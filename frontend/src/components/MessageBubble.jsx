import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Copy, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';

const CodeBlock = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-6 rounded-lg overflow-hidden border border-[#333] bg-[#1e1e1e]">
      <div className="flex items-center justify-between px-4 py-2 bg-[#252526] border-b border-[#333]">
        <span className="text-[10px] uppercase tracking-widest text-gray-400 font-bold">
          {language || 'code'}
        </span>
        <button 
          onClick={handleCopy}
          className="p-1.5 hover:bg-[#333] rounded transition-all text-gray-400 border border-transparent hover:border-[#444]"
        >
          {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
      </div>
      <SyntaxHighlighter
        language={language || 'text'}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          padding: '1.5rem',
          fontSize: '0.875rem',
          lineHeight: '1.5',
          background: 'transparent',
        }}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
};

const MessageBubble = ({ message }) => {
  const isAi = message.role === 'assistant';

  return (
    <div className={`flex gap-4 ${isAi ? 'bg-[#252526]/50' : ''} p-6 rounded-2xl transition-all hover:bg-[#252526] group/bubble mb-2`}>
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg ${
        isAi ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white' : 'bg-[#3c3c3c] text-gray-400'
      }`}>
        {isAi ? <Bot size={20} /> : <User size={20} />}
      </div>
      
      <div className="flex-1 min-w-0 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500">
            {isAi ? 'Assistant Intelligence' : 'Personal Inquiry'}
          </span>
        </div>

        <div className="prose prose-invert prose-blue max-w-none text-[0.9375rem] leading-relaxed">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const lang = match ? match[1] : '';
                const codeValue = String(children).replace(/\n$/, '');

                // Force inline if there are no newlines, even if markdown parser thinks otherwise
                const isInline = inline || !codeValue.includes('\n');

                if (!isInline) {
                  return <CodeBlock language={lang} value={codeValue} />;
                }

                return (
                  <code className="bg-[#3c3c3c]/60 px-1.5 py-0.5 rounded text-blue-400 font-mono text-[0.85em] font-medium" {...props}>
                    {children}
                  </code>
                );
              },
              p: ({children}) => <p className="mb-4 last:mb-0 text-gray-300 leading-relaxed">{children}</p>,
              ul: ({children}) => <ul className="list-disc ml-4 mb-4 space-y-2 text-gray-300">{children}</ul>,
              ol: ({children}) => <ol className="list-decimal ml-4 mb-4 space-y-2 text-gray-300">{children}</ol>,
              li: ({children}) => <li className="marker:text-blue-500">{children}</li>,
              h1: ({children}) => <h1 className="text-2xl font-bold mb-4 mt-6 text-white border-b border-[#333] pb-2">{children}</h1>,
              h2: ({children}) => <h2 className="text-xl font-bold mb-3 mt-5 text-white">{children}</h2>,
              h3: ({children}) => <h3 className="text-lg font-bold mb-2 mt-4 text-white">{children}</h3>,
              blockquote: ({children}) => (
                <blockquote className="border-l-4 border-blue-600 bg-blue-600/5 px-4 py-2 my-4 rounded-r italic text-gray-400">
                  {children}
                </blockquote>
              ),
              table: ({children}) => (
                <div className="overflow-x-auto my-6 rounded-lg border border-[#333]">
                  <table className="w-full text-left border-collapse">{children}</table>
                </div>
              ),
              th: ({children}) => <th className="bg-[#252526] p-3 text-xs font-bold uppercase tracking-wider border-b border-[#333]">{children}</th>,
              td: ({children}) => <td className="p-3 border-b border-[#333] text-sm text-gray-400">{children}</td>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
