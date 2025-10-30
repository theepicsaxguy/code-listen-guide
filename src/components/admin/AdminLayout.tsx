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
      <aside className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-card border-r border-border flex flex-col transition-all duration-300`}>
        <div className="p-6 relative">
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="absolute -right-3 top-6 bg-secondary rounded-full p-1 text-muted-foreground hover:text-foreground hover:bg-secondary/80 transition-colors z-10 border border-border"
            aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isSidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
          {!isSidebarCollapsed ? (
            <>
              <h1 className="text-xl font-bold text-foreground">
                Codebase Audiobook
              </h1>
              <p className="text-xs text-muted-foreground mt-1">Admin Dashboard</p>
            </>
          ) : (
            <div className="flex items-center justify-center">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center text-xs font-bold text-primary-foreground">
                CA
              </div>
            </div>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/admin" && location.pathname.startsWith(item.path));

            return (
              <Link key={item.path} to={item.path}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} ${
                    isActive
                      ? "bg-secondary text-secondary-foreground shadow-lg hover:bg-secondary/90"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                  title={isSidebarCollapsed ? item.label : undefined}
                >
                  <Icon className={`h-4 w-4 ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
                  {!isSidebarCollapsed && item.label}
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="p-4">
          <Button
            variant="ghost"
            className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} text-destructive hover:text-destructive hover:bg-destructive/10`}
            onClick={handleLogout}
            title={isSidebarCollapsed ? "Logout" : undefined}
          >
            <LogOut className={`h-4 w-4 ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
            {!isSidebarCollapsed && "Logout"}
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-background">
        <Outlet />
      </main>
    </div>
  );
};
