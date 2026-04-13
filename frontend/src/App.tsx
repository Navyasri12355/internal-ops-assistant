import { Routes, Route, NavLink } from 'react-router-dom'
import { MessageSquare, Upload, BarChart2 } from 'lucide-react'
import ChatPage from './pages/ChatPage'
import UploadPage from './pages/UploadPage'
import StatsPage from './pages/StatsPage'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-surface-900">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 flex flex-col border-r border-surface-600 bg-surface-800 px-3 py-6">
        <div className="mb-8 px-2">
          <p className="font-display text-lg font-700 text-white leading-tight">Knowledge<br />Agent</p>
          <p className="mt-1 text-xs text-zinc-500 font-mono">v0.1.0 · RAG</p>
        </div>

        <nav className="flex flex-col gap-1">
          <NavItem to="/" icon={<MessageSquare size={16} />} label="Ask" end />
          <NavItem to="/upload" icon={<Upload size={16} />} label="Documents" />
          <NavItem to="/stats" icon={<BarChart2 size={16} />} label="Stats" />
        </nav>

        <div className="mt-auto px-2 py-3 rounded-lg bg-surface-700 border border-surface-500">
          <p className="text-xs text-zinc-500 leading-relaxed">
            Answers are grounded in your documents only. Citations shown for every response.
          </p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </main>
    </div>
  )
}

function NavItem({ to, icon, label, end }: { to: string; icon: React.ReactNode; label: string; end?: boolean }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
          isActive
            ? 'bg-brand-500/10 text-brand-500 font-medium'
            : 'text-zinc-400 hover:text-zinc-200 hover:bg-surface-700'
        }`
      }
    >
      {icon}
      {label}
    </NavLink>
  )
}