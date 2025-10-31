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
        'flex h-screen flex-col flex-shrink-0 bg-sidebar-surface text-sidebar-foreground border-r border-sidebar-border transition-[width] duration-300',
        className,
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
          {isCollapsed ? (
            brand?.collapsedLogo || brand?.logo || (
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-secondary text-xs font-semibold text-zinc-300">
                CA
              </div>
            )
          ) : (
            <>
              {brand?.logo && <div className="flex-shrink-0">{brand.logo}</div>}
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-sidebar-foreground">{brand?.title}</p>
                {brand?.subtitle && <p className="truncate text-xs text-muted-foreground uppercase tracking-wide">{brand.subtitle}</p>}
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
            'group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-fast',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar-surface',
            isCollapsed && 'justify-center gap-0 px-0',
            isActive
              ? 'bg-sidebar-accent text-sidebar-accent-foreground'
              : 'text-zinc-500 hover:bg-sidebar-accent/60 hover:text-zinc-200',
          );

          if (item.path) {
            return (
              <Link key={item.id} to={item.path} title={isCollapsed ? item.label : undefined} className="block">
                <div className={commonClasses}>
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary" />
                  )}
                  {typeof Icon === 'function' ? (
                    <Icon className={cn('h-4 w-4', isActive ? 'text-zinc-200' : 'text-zinc-500', !isCollapsed && 'shrink-0')} />
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
              {isActive && (
                <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary" />
              )}
              {typeof Icon === 'function' ? (
                <Icon className={cn('h-4 w-4', isActive ? 'text-zinc-200' : 'text-zinc-500', !isCollapsed && 'shrink-0')} />
              ) : (
                <span className={cn(!isCollapsed && 'shrink-0')}>{Icon}</span>
              )}
              {!isCollapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {footer && <div className="px-4 py-4 border-t border-sidebar-border text-muted-foreground">{footer}</div>}
    </aside>
  );
};

