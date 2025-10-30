import React, { ReactNode } from 'react';

interface AppShellProps {
  children: ReactNode;
  sidebar?: ReactNode;
  header?: ReactNode;
  className?: string;
}

/**
 * AppShell provides a consistent layout structure for dashboard pages.
 * Uses token-based styling to match the landing page theme.
 */
export const AppShell: React.FC<AppShellProps> = ({
  children,
  sidebar,
  header,
  className = '',
}) => {
  return (
    <div className={`flex h-screen bg-background ${className}`}>
      {sidebar && sidebar}
      <div className="flex-1 flex flex-col overflow-hidden">
        {header && (
          <header className="bg-card sticky top-0 z-10 backdrop-blur-sm bg-card/95">
            {header}
          </header>
        )}
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
};

