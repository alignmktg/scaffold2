'use client'

import { X, MessageSquare, FileText, Settings, Database } from 'lucide-react'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-50 h-full w-64 bg-background border-r lg:static lg:translate-x-0">
        <div className="flex h-14 items-center border-b px-4">
          <h2 className="text-lg font-semibold">Menu</h2>
          <button
            onClick={onClose}
            className="ml-auto h-8 w-8 rounded-md border p-1 hover:bg-accent lg:hidden"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <nav className="p-4 space-y-2">
          <a
            href="#"
            className="flex items-center space-x-2 rounded-md px-3 py-2 text-sm hover:bg-accent"
          >
            <MessageSquare className="h-4 w-4" />
            <span>Chat</span>
          </a>

          <a
            href="#"
            className="flex items-center space-x-2 rounded-md px-3 py-2 text-sm hover:bg-accent"
          >
            <FileText className="h-4 w-4" />
            <span>Documents</span>
          </a>

          <a
            href="#"
            className="flex items-center space-x-2 rounded-md px-3 py-2 text-sm hover:bg-accent"
          >
            <Database className="h-4 w-4" />
            <span>RAG</span>
          </a>

          <a
            href="#"
            className="flex items-center space-x-2 rounded-md px-3 py-2 text-sm hover:bg-accent"
          >
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </a>
        </nav>
      </aside>
    </>
  )
}
