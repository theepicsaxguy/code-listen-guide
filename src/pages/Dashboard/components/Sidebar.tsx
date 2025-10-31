import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Library, Settings, CreditCard, Mic, ChevronLeft, ChevronRight } from 'lucide-react';

import { cn } from '@/lib/utils';

import type { User } from '../../../lib/types';

interface SidebarProps {
 activeTab: string;
 setActiveTab: (tab: string) => void;
 user: User | null;
 isCollapsed: boolean;
 onToggleCollapse: () => void;
 isMobileMenuOpen?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, user, isCollapsed, onToggleCollapse, isMobileMenuOpen = false }) => {
 const navigate = useNavigate();

 const navItems = [
 { id: 'home', label: 'Overview', icon: <Home size={20} /> },
 { id: 'audiobooks', label: 'Audiobooks', icon: <Library size={20} /> },
 { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
 { id: 'billing', label: 'Billing', icon: <CreditCard size={20} /> },
 ...(user?.is_admin ? [{ id: 'admin', label: 'Admin', icon: <Settings size={20} /> }] : [])
 ];

 const handleNavClick = (itemId: string) => {
 if (itemId === 'admin') {
 navigate('/admin');
 } else {
 setActiveTab(itemId);
 }
 };

  return (
    <aside
      className={cn(
        isCollapsed ? 'w-20' : 'w-64',
        'flex h-full flex-col flex-shrink-0 bg-sidebar-surface text-sidebar-foreground border-r border-sidebar-border transition-all duration-300',
        // Mobile: overlay sidebar
        'fixed md:relative inset-y-0 left-0 z-40 md:z-auto',
        // Mobile: show/hide based on menu state, hide collapsed sidebar on mobile
        isCollapsed && !isMobileMenuOpen ? 'hidden md:flex' : '',
        !isMobileMenuOpen && !isCollapsed ? '-translate-x-full md:translate-x-0' : '',
        isMobileMenuOpen ? 'translate-x-0' : '',
      )}
    >
    <div className="relative flex items-center px-4 py-5 border-b border-sidebar-border">
      <button
        onClick={onToggleCollapse}
        className="absolute -right-3 top-1/2 -translate-y-1/2 rounded-full bg-surface-secondary p-2 text-zinc-500 transition-fast hover:bg-sidebar-accent-hover hover:text-zinc-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar-surface"
        aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
      <div className={cn('flex items-center', isCollapsed ? 'justify-center w-full' : 'gap-3')}>
        <div className="flex h-8 w-8 items-center justify-center">
          <Mic className="h-4 w-4 text-zinc-500" />
        </div>
        {!isCollapsed && (
          <div className="min-w-0">
            <p className="text-sm font-semibold text-sidebar-foreground">Codebase Audio</p>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Dashboard</p>
          </div>
        )}
      </div>
    </div>
    <nav className="flex-1 space-y-1 px-3 py-4">
      {navItems.map((item) => {
        const isActive = activeTab === item.id;
        const itemClasses = cn(
          'group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-fast',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar-surface',
          isCollapsed && 'justify-center gap-0 px-0',
          isActive
            ? 'bg-sidebar-accent text-sidebar-accent-foreground'
            : 'text-zinc-500 hover:bg-sidebar-accent/60 hover:text-zinc-200',
        );

        return (
          <button
            key={item.id}
            onClick={() => handleNavClick(item.id)}
            className={itemClasses}
            title={isCollapsed ? item.label : undefined}
          >
            {isActive ? (
              <>
                {/* Active indicator bar - thin vertical line */}
                <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary" />
                {React.cloneElement(item.icon, {
                  className: cn('h-4 w-4 text-zinc-200 stroke-[1.5] transition-fast', !isCollapsed && 'shrink-0'),
                })}
              </>
            ) : (
              React.cloneElement(item.icon, {
                className: cn('h-4 w-4 text-zinc-500 stroke-[1.5] transition-fast', !isCollapsed && 'shrink-0'),
              })
            )}
            {!isCollapsed && <span className="truncate">{item.label}</span>}
          </button>
        );
      })}
    </nav>
    {user && (
      <div className="px-4 py-4 border-t border-sidebar-border">
        <div className={cn('flex items-center rounded-lg px-3 py-2.5', isCollapsed ? 'justify-center' : 'gap-3')}>
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-surface-secondary text-xs font-semibold text-zinc-300">
            {user.name
              .split(' ')
              .map((n) => n[0])
              .join('')}
          </div>
          {!isCollapsed && (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-sidebar-foreground">{user.name}</p>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">{user.subscription_tier} plan</p>
            </div>
          )}
        </div>
      </div>
    )}
 </aside>
 );
};
