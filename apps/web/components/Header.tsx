'use client'

import { Menu, Settings, User } from 'lucide-react'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center px-4">
        <button
          onClick={onMenuClick}
          className="mr-2 h-8 w-8 rounded-md border p-1 hover:bg-accent"
        >
          <Menu className="h-4 w-4" />
        </button>

        <div className="flex-1">
          <h1 className="text-lg font-semibold">
            {process.env.NEXT_PUBLIC_APP_NAME || 'AI App Bootstrap'}
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <button className="h-8 w-8 rounded-md border p-1 hover:bg-accent">
            <Settings className="h-4 w-4" />
          </button>
          <button className="h-8 w-8 rounded-md border p-1 hover:bg-accent">
            <User className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  )
}
