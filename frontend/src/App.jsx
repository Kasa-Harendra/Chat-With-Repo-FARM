import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import RightPanel from './components/RightPanel'
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <div className="flex h-screen w-full bg-[#1a1a1a] text-white overflow-hidden font-sans">
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#333',
            color: '#fff',
            fontSize: '14px',
            border: '1px solid #444',
          },
          success: {
            iconTheme: {
              primary: '#3b82f6',
              secondary: '#fff',
            },
          },
        }}
      />
      <Sidebar />
      <main className="flex-1 flex flex-col items-center overflow-hidden border-r border-[#333]">
        <ChatWindow />
      </main>
      <RightPanel />
    </div>
  )
}

export default App
