import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Library, Settings, CreditCard, Mic } from 'lucide-react';
import type { User } from '../../../lib/types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: User | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, user }) => {
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
    <div className="w-64 bg-gray-900 border-r border-gray-800 h-screen flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
            <Mic className="text-white" size={24} />
          </div>
          <div>
            <div className="font-semibold text-white">Codebase Audio</div>
            <div className="text-xs text-gray-400">Dashboard</div>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleNavClick(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-all ${
              activeTab === item.id
                ? 'bg-gray-800 text-white shadow-lg'
                : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      {user && (
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800/50">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-sm font-medium text-white">
              {user.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">{user.name}</div>
              <div className="text-xs text-gray-400">{user.subscription_tier} Plan</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
