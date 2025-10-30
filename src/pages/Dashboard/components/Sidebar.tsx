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
    <div className={`${isCollapsed ? 'w-20' : 'w-64'} bg-gradient-sidebar h-screen flex flex-col transition-all duration-300`}>
      <div className="p-6 relative bg-gradient-to-r from-primary/5 to-accent/5">
        <button
          onClick={onToggleCollapse}
          className="absolute -right-3 top-6 bg-card rounded-full p-1.5 text-muted-foreground hover:text-foreground hover:bg-primary/20 transition-all z-10 shadow-lg hover:shadow-xl shadow-primary/20"
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
        {navItems.map((item, idx) => {
          // Rotate colors for variety
          const colorVariants = ['primary', 'accent', 'secondary'] as const;
          const colorVariant = colorVariants[idx % colorVariants.length];
          
          const IconComponent = React.cloneElement(item.icon, {
            className: `${
              activeTab === item.id 
                ? colorVariant === 'primary' ? 'text-primary' : colorVariant === 'accent' ? 'text-accent' : 'text-foreground'
                : 'text-muted-foreground'
            } transition-colors ${activeTab === item.id ? 'icon-gradient' : ''}`
          });
          
          const activeStyles = {
            primary: 'bg-gradient-primary text-primary-foreground shadow-lg shadow-primary/30 border-2 border-primary/40',
            accent: 'bg-gradient-accent text-accent-foreground shadow-lg shadow-accent/30 border-2 border-accent/40',
            secondary: 'bg-gradient-secondary text-secondary-foreground shadow-lg shadow-secondary/20 border-2 border-secondary/40'
          }[colorVariant];
          
          const hoverStyles = {
            primary: 'hover:bg-primary/15 hover:border-primary/30 hover:text-primary',
            accent: 'hover:bg-accent/15 hover:border-accent/30 hover:text-accent',
            secondary: 'hover:bg-secondary/15 hover:border-secondary/30 hover:text-foreground'
          }[colorVariant];
          
          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-xl mb-1 transition-all relative group border-2 ${
                activeTab === item.id
                  ? activeStyles
                  : `text-muted-foreground border-transparent ${hoverStyles}`
              }`}
              title={isCollapsed ? item.label : undefined}
            >
              {IconComponent}
              {!isCollapsed && (
                <span className={`font-medium ${activeTab === item.id ? 'text-foreground' : ''}`}>
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>
      {user && (
        <div className="p-4 bg-gradient-to-r from-secondary/10 to-muted/10">
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-xl bg-secondary/30 hover:bg-secondary/50 transition-all hover-card`}>
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
