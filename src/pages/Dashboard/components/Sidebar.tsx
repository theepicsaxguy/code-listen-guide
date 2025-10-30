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
    <div className={`${isCollapsed ? 'w-20' : 'w-64'} bg-gradient-sidebar h-screen flex flex-col transition-all duration-300 border-r border-border/50`}>
      <div className="p-6 relative border-b border-border/30">
        <button
          onClick={onToggleCollapse}
          className="absolute -right-3 top-6 bg-card border border-border/50 rounded-full p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent/20 hover:border-primary/30 transition-all z-10 shadow-sm hover:shadow-md"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
          <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/20">
            <Mic className="text-primary-foreground" size={24} />
          </div>
          {!isCollapsed && (
            <div>
              <div className="font-bold text-foreground text-lg tracking-tight">Codebase Audio</div>
              <div className="text-xs text-muted-foreground font-medium">Dashboard</div>
            </div>
          )}
        </div>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const IconComponent = React.cloneElement(item.icon, {
            className: `${
              activeTab === item.id ? 'text-primary' : 'text-muted-foreground'
            } transition-colors ${activeTab === item.id ? 'icon-gradient' : ''}`
          });
          
          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-xl mb-1 transition-all relative group ${
                activeTab === item.id
                  ? 'bg-accent/20 text-accent-foreground shadow-md shadow-primary/10 border border-primary/20'
                  : 'text-muted-foreground hover:bg-accent/10 hover:text-foreground border border-transparent'
              }`}
              title={isCollapsed ? item.label : undefined}
            >
              {IconComponent}
              {!isCollapsed && (
                <span className={`font-medium ${activeTab === item.id ? 'text-foreground' : ''}`}>
                  {item.label}
                </span>
              )}
              {activeTab === item.id && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-gradient-primary rounded-r-full" />
              )}
            </button>
          );
        })}
      </nav>
      {user && (
        <div className="p-4 border-t border-border/30">
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-xl bg-card border border-border/50 hover:border-border transition-all hover-card`}>
            <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center text-sm font-bold text-primary-foreground flex-shrink-0 shadow-md shadow-primary/20">
              {user.name.split(' ').map(n => n[0]).join('')}
            </div>
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-foreground truncate">{user.name}</div>
                <div className="text-xs text-muted-foreground font-medium capitalize">{user.subscription_tier} Plan</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
