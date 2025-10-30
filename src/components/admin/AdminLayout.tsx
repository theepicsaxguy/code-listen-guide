import { useState } from "react";
import { Link, useLocation, Outlet, Navigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  CreditCard,
  BookOpen,
  Activity,
  FileText,
  Settings,
  LogOut,
  History,
  Activity as ActivityIcon,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  FileCode2,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

const navItems = [
  { path: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { path: "/admin/users", label: "Users", icon: Users },
  { path: "/admin/payments", label: "Payments", icon: CreditCard },
  { path: "/admin/content", label: "Content", icon: BookOpen },
  { path: "/admin/versioning", label: "Versioning", icon: History },
  { path: "/admin/agents", label: "Agents", icon: Activity },
  { path: "/admin/tracing", label: "Job Tracing", icon: ActivityIcon },
  { path: "/admin/chonkie-test", label: "chonkie Test", icon: FileCode2 },
  { path: "/admin/agent-test", label: "Agent Test", icon: Zap },
  { path: "/admin/support", label: "Support", icon: MessageSquare },
  { path: "/admin/audit", label: "Audit Logs", icon: FileText },
  { path: "/admin/settings", label: "Settings", icon: Settings },
];

export const AdminLayout = () => {
  const location = useLocation();
  const { user, isLoading: isAuthLoading, logout: mainLogout } = useAuth();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Fetch user data to check admin status
  const { data: userData, isLoading: isUserDataLoading } = useQuery({
    queryKey: ['user'],
    queryFn: () => apiClient.getCurrentUser(),
    enabled: !!user,
  });

  const isLoading = isAuthLoading || isUserDataLoading;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <span className="text-muted-foreground">Loading dashboard…</span>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  // Redirect to dashboard if not admin
  if (!userData?.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogout = () => {
    mainLogout();
    apiClient.clearToken();
  };

  return (
    <div className="min-h-screen flex bg-background">
      <aside className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-gradient-sidebar flex flex-col transition-all duration-300 border-r border-border/50`}>
        <div className="p-6 relative border-b border-border/30">
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="absolute -right-3 top-6 bg-card border border-border/50 rounded-full p-1.5 text-muted-foreground hover:text-foreground hover:bg-accent/20 hover:border-primary/30 transition-all z-10 shadow-sm hover:shadow-md"
            aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isSidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
          {!isSidebarCollapsed ? (
            <>
              <h1 className="text-xl font-bold text-foreground tracking-tight">
                Codebase Audiobook
              </h1>
              <p className="text-xs text-muted-foreground mt-1 font-medium">Admin Dashboard</p>
            </>
          ) : (
            <div className="flex items-center justify-center">
              <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center text-xs font-bold text-primary-foreground shadow-lg shadow-primary/20">
                CA
              </div>
            </div>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/admin" && location.pathname.startsWith(item.path));

            return (
              <Link key={item.path} to={item.path}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} rounded-xl transition-all relative ${
                    isActive
                      ? "bg-accent/20 text-accent-foreground shadow-md shadow-primary/10 border border-primary/20 hover:bg-accent/30"
                      : "text-muted-foreground hover:bg-accent/10 hover:text-foreground border border-transparent"
                  }`}
                  title={isSidebarCollapsed ? item.label : undefined}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'icon-gradient' : ''} ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
                  {!isSidebarCollapsed && <span className="font-medium">{item.label}</span>}
                  {isActive && !isSidebarCollapsed && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-gradient-primary rounded-r-full" />
                  )}
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border/30">
          <Button
            variant="ghost"
            className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} text-destructive hover:text-destructive hover:bg-destructive/10 rounded-xl transition-all`}
            onClick={handleLogout}
            title={isSidebarCollapsed ? "Logout" : undefined}
          >
            <LogOut className={`h-4 w-4 ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
            {!isSidebarCollapsed && <span className="font-medium">Logout</span>}
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-background">
        <Outlet />
      </main>
    </div>
  );
};
