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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAdminAuth } from "@/contexts/AdminAuthContext";

const navItems = [
  { path: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { path: "/admin/users", label: "Users", icon: Users },
  { path: "/admin/payments", label: "Payments", icon: CreditCard },
  { path: "/admin/content", label: "Content", icon: BookOpen },
  { path: "/admin/versioning", label: "Versioning", icon: History },
  { path: "/admin/agents", label: "Agents", icon: Activity },
  { path: "/admin/tracing", label: "Job Tracing", icon: ActivityIcon },
  { path: "/admin/support", label: "Support", icon: MessageSquare },
  { path: "/admin/audit", label: "Audit Logs", icon: FileText },
  { path: "/admin/settings", label: "Settings", icon: Settings },
];

export const AdminLayout = () => {
  const location = useLocation();
  const { isAuthenticated, isLoading, logout } = useAdminAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <span className="text-muted-foreground">Loading dashboard…</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return (
    <div className="min-h-screen flex bg-background">
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            Codebase Audiobook
          </h1>
          <p className="text-xs text-muted-foreground mt-1">Admin Dashboard</p>
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
                  className={`w-full justify-start ${
                    isActive ? "bg-primary/10 text-primary hover:bg-primary/20" : ""
                  }`}
                >
                  <Icon className="mr-3 h-4 w-4" />
                  {item.label}
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <Button
            variant="ghost"
            className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={logout}
          >
            <LogOut className="mr-3 h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};
