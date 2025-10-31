import { useState } from "react";
import { Link, useLocation, Outlet, Navigate, useNavigate } from "react-router-dom";
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
  ArrowLeft,
  GitBranch,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

const navItems = [
  { path: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { path: "/admin/users", label: "Users", icon: Users },
  { path: "/admin/payments", label: "Payments", icon: CreditCard },
  { path: "/admin/content", label: "Content", icon: BookOpen },
  { path: "/admin/versioning", label: "Versioning", icon: History },
  { path: "/admin/workflows", label: "Workflows", icon: GitBranch },
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
  const navigate = useNavigate();
  const { user, isLoading: isAuthLoading, logout: mainLogout } = useAuth();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  if (isAuthLoading) {
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
  if (!user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogout = () => {
    mainLogout();
  };

  return (
    <div className="min-h-screen flex bg-background">
      <aside className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-gradient-sidebar flex flex-col transition-all duration-300`}>
        <div className="p-6 relative bg-gradient-to-r from-primary/5 to-accent/5">
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="absolute -right-3 top-6 bg-card rounded-full p-1.5 text-muted-foreground hover:text-foreground hover:bg-primary/20 transition-all z-10 shadow-lg hover:shadow-xl shadow-primary/20"
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
          {navItems.map((item, idx) => {
            const Icon = item.icon;
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/admin" && location.pathname.startsWith(item.path));

            // Rotate colors for variety
            const colorVariants = ['primary', 'accent', 'secondary'] as const;
            const colorVariant = colorVariants[idx % colorVariants.length];
            
            const activeStyles = {
              primary: "bg-gradient-primary text-primary-foreground shadow-lg shadow-primary/30 border-2 border-primary/40",
              accent: "bg-gradient-accent text-accent-foreground shadow-lg shadow-accent/30 border-2 border-accent/40",
              secondary: "bg-gradient-secondary text-secondary-foreground shadow-lg shadow-secondary/20 border-2 border-secondary/40"
            }[colorVariant];
            
            const hoverStyles = {
              primary: "hover:bg-primary/15 hover:border-primary/30 hover:text-primary",
              accent: "hover:bg-accent/15 hover:border-accent/30 hover:text-accent",
              secondary: "hover:bg-secondary/15 hover:border-secondary/30 hover:text-foreground"
            }[colorVariant];

            return (
              <Link key={item.path} to={item.path}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} rounded-xl transition-all relative border-2 ${
                    isActive
                      ? activeStyles
                      : `text-muted-foreground border-transparent ${hoverStyles}`
                  }`}
                  title={isSidebarCollapsed ? item.label : undefined}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'icon-gradient' : ''} ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
                  {!isSidebarCollapsed && <span className="font-medium">{item.label}</span>}
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 bg-gradient-to-r from-destructive/5 to-muted/5">
          <Button
            variant="ghost"
            className={`w-full ${isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'} text-destructive hover:text-destructive hover:bg-destructive/20 hover:border-destructive/30 border-2 border-transparent rounded-xl transition-all`}
            onClick={handleLogout}
            title={isSidebarCollapsed ? "Logout" : undefined}
          >
            <LogOut className={`h-4 w-4 ${!isSidebarCollapsed ? 'mr-3' : ''}`} />
            {!isSidebarCollapsed && <span className="font-medium">Logout</span>}
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-background">
        <div className="p-6">
          <div className="mb-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate("/dashboard")}
              className="text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to User Dashboard
            </Button>
          </div>
          <Outlet />
        </div>
      </main>
    </div>
  );
};
