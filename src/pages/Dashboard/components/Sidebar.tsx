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
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, user, isCollapsed, onToggleCollapse }) => {
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
      isCollapsed ? 'w-20' : 'w-sidebar-expanded',
 'flex h-screen flex-col bg-sidebar-surface text-sidebar-foreground shadow-lg transition-[width] duration-300',
 )}
 >
 <div className="relative flex items-center bg-sidebar-surface-secondary px-4 py-5 shadow-sm">
 <button
 onClick={onToggleCollapse}
 className="absolute -right-3 top-1/2 -translate-y-1/2 rounded-full bg-surface-secondary shadow-md p-1 text-muted-foreground transition-standard hover:bg-accent hover:text-accent-foreground hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
 aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
 >
 {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
 </button>
 <div className={cn('flex items-center', isCollapsed ? 'justify-center w-full' : 'gap-3')}>
 <div className="flex h-10 w-10 items-center justify-center rounded-card bg-primary/15 text-primary">
 <Mic className="h-5 w-5" />
 </div>
  {!isCollapsed && (
 <div className="min-w-0">
 <p className="text-body-sm font-semibold text-sidebar-foreground">Codebase Audio</p>
 <p className="text-caption text-muted-foreground">Dashboard</p>
 </div>
 )}
 </div>
 </div>
 <nav className="flex-1 space-y-1 px-3 py-4">
 {navItems.map((item) => {
 const isActive = activeTab === item.id;
 const itemClasses = cn(
 'group relative flex w-full items-center gap-3 rounded-control px-3 py-3 text-sm font-medium transition-colors',
 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar',
 isCollapsed && 'justify-center gap-0 px-0',
 isActive
 ? 'bg-sidebar-accent text-sidebar-accent-foreground before:absolute before:left-0 before:top-2 before:bottom-2 before:w-0.5 before:rounded-full before:bg-primary'
 : 'text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground',
 );

 return (
 <button
 key={item.id}
 onClick={() => handleNavClick(item.id)}
 className={itemClasses}
 title={isCollapsed ? item.label : undefined}
 >
 {React.cloneElement(item.icon, {
 className: cn('h-5 w-5', !isCollapsed && 'shrink-0'),
 })}
 {!isCollapsed && <span className="truncate">{item.label}</span>}
 </button>
 );
 })}
 </nav>
 {user && (
 <div className="bg-sidebar-surface-secondary px-4 py-4 shadow-sm">
 <div className={cn('flex items-center rounded-control bg-sidebar-accent/40 px-3 py-3', isCollapsed ? 'justify-center' : 'gap-3')}>
 <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
 {user.name
 .split(' ')
 .map((n) => n[0])
 .join('')}
 </div>
  {!isCollapsed && (
 <div className="min-w-0">
 <p className="truncate text-body-sm font-semibold text-sidebar-foreground">{user.name}</p>
 <p className="text-caption text-muted-foreground capitalize">{user.subscription_tier} plan</p>
 </div>
 )}
 </div>
 </div>
 )}
 </aside>
 );
};
