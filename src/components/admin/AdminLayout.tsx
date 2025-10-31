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
      <aside
        className={`${
          isSidebarCollapsed ? 'w-16' : 'w-sidebar-expanded'
        } flex flex-col flex-shrink-0 border-r border-sidebar-border bg-sidebar-surface text-sidebar-foreground transition-all duration-300`}
      >
        <div className="relative px-4 py-5 border-b border-sidebar-border">
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="absolute -right-3 top-1/2 -translate-y-1/2 rounded-full bg-surface-secondary p-2 text-zinc-500 transition-fast hover:bg-sidebar-accent-hover hover:text-zinc-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar-surface"
            aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isSidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
          {!isSidebarCollapsed ? (
            <>
              <h1 className="text-xl font-bold text-sidebar-foreground tracking-tight">
                Codebase Audiobook
              </h1>
              <p className="text-xs text-muted-foreground mt-1 uppercase tracking-wide">Admin Dashboard</p>
            </>
          ) : (
            <div className="flex items-center justify-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-secondary text-xs font-bold text-zinc-300">
                CA
              </div>
            </div>
          )}
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/admin" && location.pathname.startsWith(item.path));

            return (
              <Link key={item.path} to={item.path}>
                <Button
                  variant="ghost"
                  className={`relative w-full ${
                    isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'
                  } rounded-lg px-3 py-2.5 text-sm font-medium transition-fast focus-visible:ring-offset-sidebar-surface ${
                    isActive
                      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                      : 'text-zinc-500 hover:bg-sidebar-accent/60 hover:text-zinc-200'
                  }`}
                  title={isSidebarCollapsed ? item.label : undefined}
                >
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary" />
                  )}
                  <Icon
                    className={`h-4 w-4 ${
                      isActive ? 'text-zinc-200' : 'text-zinc-500'
                    } ${!isSidebarCollapsed ? 'mr-3' : ''}`}
                  />
                  {!isSidebarCollapsed && <span className="font-medium">{item.label}</span>}
                </Button>
              </Link>
            );
          })}
        </nav>

 <div className="p-4 border-t border-sidebar-border">
 <Button
 variant="ghost"
 className={`w-full ${
 isSidebarCollapsed ? 'justify-center px-2' : 'justify-start'
 } rounded-md text-sidebar-foreground/70 transition-colors hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground`}
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
