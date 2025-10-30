import React, { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, LucideIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface SidebarNavItem {
  id: string;
  label: string;
  icon: ReactNode | LucideIcon;
  path?: string; // If provided, uses Link navigation
  onClick?: () => void; // If provided, uses button with onClick
}

interface SidebarProps {
  navItems: SidebarNavItem[];
  activeItemId?: string;
  activePath?: string; // For route-based active state
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  brand?: {
    logo?: ReactNode;
    title: string;
    subtitle?: string;
    collapsedLogo?: ReactNode;
  };
  footer?: ReactNode;
  className?: string;
}

/**
 * Unified Sidebar component using token-based styling.
 * Supports both route-based (Link) and callback-based navigation.
 */
export const Sidebar: React.FC<SidebarProps> = ({
  navItems,
  activeItemId,
  activePath,
  isCollapsed,
  onToggleCollapse,
  brand,
  footer,
  className = '',
}) => {
  const isItemActive = (item: SidebarNavItem) => {
    if (activeItemId) {
      return item.id === activeItemId;
    }
    if (activePath && item.path) {
      return activePath === item.path || (item.path !== '/' && activePath.startsWith(item.path));
    }
    return false;
  };

  return (
    <aside
      className={`${isCollapsed ? 'w-20' : 'w-64'} bg-card h-screen flex flex-col transition-all duration-300 ${className}`}
    >
      {/* Brand Header */}
      <div className="p-6 relative">
        <button
          onClick={onToggleCollapse}
          className="absolute -right-3 top-6 bg-background rounded-full p-1 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors z-10"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'}`}>
          {isCollapsed ? (
            brand?.collapsedLogo || brand?.logo || (
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center text-xs font-bold text-primary-foreground">
                CA
              </div>
            )
          ) : (
            <>
              {brand?.logo && <div className="flex-shrink-0">{brand.logo}</div>}
              <div>
                <div className="font-semibold text-foreground">{brand?.title}</div>
                {brand?.subtitle && (
                  <div className="text-xs text-muted-foreground">{brand.subtitle}</div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = isItemActive(item);
          const activeClasses = isActive
            ? 'bg-accent text-accent-foreground shadow-lg'
            : 'text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground';

          // Use Link if path provided, otherwise use button with onClick
          if (item.path) {
            return (
              <Link key={item.id} to={item.path}>
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={`w-full ${isCollapsed ? 'justify-center px-2' : 'justify-start'} ${activeClasses}`}
                  title={isCollapsed ? item.label : undefined}
                >
                  {typeof Icon === 'function' ? (
                    <Icon className={`h-4 w-4 ${!isCollapsed ? 'mr-3' : ''}`} />
                  ) : (
                    <span className={!isCollapsed ? 'mr-3' : ''}>{Icon}</span>
                  )}
                  {!isCollapsed && item.label}
                </Button>
              </Link>
            );
          }

          return (
            <button
              key={item.id}
              onClick={item.onClick}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'gap-3'} px-4 py-3 rounded-lg transition-all ${activeClasses}`}
              title={isCollapsed ? item.label : undefined}
            >
              {typeof Icon === 'function' ? (
                <Icon className="h-4 w-4" />
              ) : (
                Icon
              )}
              {!isCollapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      {footer && <div className="p-4">{footer}</div>}
    </aside>
  );
};

