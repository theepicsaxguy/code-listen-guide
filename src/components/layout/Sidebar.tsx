import React, { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';

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
      className={cn(
        isCollapsed ? 'w-sidebar-collapsed' : 'w-sidebar-expanded',
        'flex h-screen flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] duration-200',
        className,
      )}
    >
      <div className="relative flex items-center border-b border-sidebar-border px-4 py-5">
        <button
          onClick={onToggleCollapse}
          className="absolute -right-3 top-1/2 -translate-y-1/2 rounded-full border border-sidebar-border bg-surface p-2 text-muted transition-standard hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
        <div className={cn('flex items-center', isCollapsed ? 'justify-center w-full' : 'gap-3')}>
          {isCollapsed ? (
            brand?.collapsedLogo || brand?.logo || (
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-sm font-semibold text-primary">
                CA
              </div>
            )
          ) : (
            <>
              {brand?.logo && <div className="flex-shrink-0">{brand.logo}</div>}
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-sidebar-foreground">{brand?.title}</p>
                {brand?.subtitle && <p className="truncate text-xs text-muted-foreground">{brand.subtitle}</p>}
              </div>
            </>
          )}
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = isItemActive(item);
          const commonClasses = cn(
            'group relative flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-standard',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
            isCollapsed && 'justify-center gap-0 px-0',
            isActive
              ? 'bg-sidebar-accent text-sidebar-accent-foreground'
              : 'text-muted hover:bg-sidebar-accent/70 hover:text-sidebar-accent-foreground',
          );

          if (item.path) {
            return (
              <Link key={item.id} to={item.path} title={isCollapsed ? item.label : undefined} className="block">
                <div className={commonClasses}>
                  {typeof Icon === 'function' ? (
                    <Icon className={cn('h-4 w-4', !isCollapsed && 'shrink-0')} />
                  ) : (
                    <span className={cn(!isCollapsed && 'shrink-0')}>{Icon}</span>
                  )}
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </div>
              </Link>
            );
          }

          return (
            <button
              key={item.id}
              onClick={item.onClick}
              className={commonClasses}
              title={isCollapsed ? item.label : undefined}
            >
              {typeof Icon === 'function' ? (
                <Icon className={cn('h-4 w-4', !isCollapsed && 'shrink-0')} />
              ) : (
                <span className={cn(!isCollapsed && 'shrink-0')}>{Icon}</span>
              )}
              {!isCollapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {footer && <div className="border-t border-sidebar-border px-4 py-4 text-muted">{footer}</div>}
    </aside>
  );
};

