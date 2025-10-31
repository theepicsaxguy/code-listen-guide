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
      isCollapsed ? 'w-20 hidden md:flex' : 'w-64',
 'flex h-screen flex-col bg-black text-zinc-300 transition-[width] duration-300',
 )}
 >
 <div className="relative flex items-center bg-zinc-950 px-3 py-4">
 <button
 onClick={onToggleCollapse}
 className="absolute -right-3 top-1/2 -translate-y-1/2 rounded-full bg-zinc-900 p-1.5 text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/50"
 aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
 >
 {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
 </button>
 <div className={cn('flex items-center', isCollapsed ? 'justify-center w-full' : 'gap-3')}>
 <div className="flex h-8 w-8 items-center justify-center bg-zinc-900">
 <Mic className="h-4 w-4 text-zinc-400" />
 </div>
  {!isCollapsed && (
 <div className="min-w-0">
 <p className="text-sm font-semibold text-zinc-50">Codebase Audio</p>
 <p className="text-xs text-zinc-400">Dashboard</p>
 </div>
 )}
 </div>
 </div>
 <nav className="flex-1 space-y-1 px-3 py-4">
 {navItems.map((item) => {
 const isActive = activeTab === item.id;
 const itemClasses = cn(
 'group relative flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors',
 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/50',
 isCollapsed && 'justify-center gap-0 px-0',
 isActive
 ? 'bg-zinc-900 text-zinc-50'
 : 'text-zinc-400 hover:bg-zinc-900/50 hover:text-zinc-100',
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
 <div className="bg-zinc-950 px-3 py-4">
 <div className={cn('flex items-center rounded-lg bg-zinc-900/50 px-3 py-3', isCollapsed ? 'justify-center' : 'gap-3')}>
 <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 text-xs font-semibold text-zinc-300">
 {user.name
 .split(' ')
 .map((n) => n[0])
 .join('')}
 </div>
  {!isCollapsed && (
 <div className="min-w-0">
 <p className="truncate text-sm font-semibold text-zinc-50">{user.name}</p>
 <p className="text-xs text-zinc-400 capitalize">{user.subscription_tier} plan</p>
 </div>
 )}
 </div>
 </div>
 )}
 </aside>
 );
};
