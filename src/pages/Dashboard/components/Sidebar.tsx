import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Library, Settings, CreditCard, Mic, ChevronLeft, ChevronRight } from 'lucide-react';
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
    <div className={`${isCollapsed ? 'w-20' : 'w-64'} bg-card h-screen flex flex-col transition-all duration-300`}>
      <div className="p-6 relative">
        <button
          onClick={onToggleCollapse}
          className="absolute -right-3 top-6 bg-background rounded-full p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors z-10"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center flex-shrink-0">
            <Mic className="text-primary-foreground" size={24} />
          </div>
          {!isCollapsed && (
            <div>
              <div className="font-semibold text-foreground">Codebase Audio</div>
              <div className="text-xs text-muted-foreground">Dashboard</div>
            </div>
          )}
        </div>
      </div>
      <nav className="flex-1 p-4">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleNavClick(item.id)}
            className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-lg mb-1 transition-all ${
              activeTab === item.id
                ? 'bg-accent text-accent-foreground shadow-lg'
                : 'text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground'
            }`}
            title={isCollapsed ? item.label : undefined}
          >
            {item.icon}
            {!isCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>
      {user && (
        <div className="p-4">
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-lg bg-muted`}>
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center text-sm font-medium text-primary-foreground flex-shrink-0">
              {user.name.split(' ').map(n => n[0]).join('')}
            </div>
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-foreground truncate">{user.name}</div>
                <div className="text-xs text-muted-foreground">{user.subscription_tier} Plan</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
