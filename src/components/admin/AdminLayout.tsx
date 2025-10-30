import { useState } from "react";
import { useLocation, Outlet, Navigate } from "react-router-dom";
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
  FileCode2,
  Mic,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Sidebar, type SidebarNavItem } from "@/components/layout/Sidebar";

const navItems: SidebarNavItem[] = [
  { id: "dashboard", path: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { id: "users", path: "/admin/users", label: "Users", icon: Users },
  { id: "payments", path: "/admin/payments", label: "Payments", icon: CreditCard },
  { id: "content", path: "/admin/content", label: "Content", icon: BookOpen },
  { id: "versioning", path: "/admin/versioning", label: "Versioning", icon: History },
  { id: "agents", path: "/admin/agents", label: "Agents", icon: Activity },
  { id: "tracing", path: "/admin/tracing", label: "Job Tracing", icon: ActivityIcon },
  { id: "chonkie-test", path: "/admin/chonkie-test", label: "chonkie Test", icon: FileCode2 },
  { id: "support", path: "/admin/support", label: "Support", icon: MessageSquare },
  { id: "audit", path: "/admin/audit", label: "Audit Logs", icon: FileText },
  { id: "settings", path: "/admin/settings", label: "Settings", icon: Settings },
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

  const brandLogo = (
    <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center flex-shrink-0">
      <Mic className="text-primary-foreground" size={24} />
    </div>
  );

  const collapsedLogo = (
    <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-lg flex items-center justify-center text-xs font-bold text-primary-foreground">
      CA
    </div>
  );

  return (
    <div className="min-h-screen flex bg-background">
      <Sidebar
        navItems={navItems}
        activePath={location.pathname}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        brand={{
          logo: brandLogo,
          collapsedLogo: collapsedLogo,
          title: "Codebase Audiobook",
          subtitle: "Admin Dashboard",
        }}
        footer={
          <Button
            variant="ghost"
            className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} text-destructive hover:text-destructive/90 hover:bg-destructive/10`}
            onClick={handleLogout}
            title={isSidebarCollapsed ? "Logout" : undefined}
          >
            <LogOut className={`h-4 w-4 ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
            {!isSidebarCollapsed && "Logout"}
          </Button>
        }
      />

      <main className="flex-1 overflow-auto bg-background">
        <Outlet />
      </main>
    </div>
  );
};
