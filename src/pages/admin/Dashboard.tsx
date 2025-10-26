import { useEffect, useState } from "react";
import { Users, Activity, DollarSign, HardDrive, TrendingUp } from "lucide-react";
import { StatCard } from "@/components/admin/StatCard";
import { apiClient } from "@/lib/api-client";
import { DashboardStats } from "@/types/admin";
import { toast } from "sonner";

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiClient.getDashboardStats();
        setStats(data);
      } catch (error) {
        toast.error("Failed to load dashboard stats");
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-muted rounded w-1/4" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome back! Here's an overview of your system.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={stats?.total_users?.toLocaleString() || "0"}
          icon={Users}
          description="Registered users"
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard
          title="Active Jobs"
          value={stats?.active_jobs || "0"}
          icon={Activity}
          description="Currently processing"
        />
        <StatCard
          title="Monthly Revenue"
          value={`$${stats?.revenue_month?.toLocaleString() || "0"}`}
          icon={DollarSign}
          description="This month"
          trend={{ value: 8, isPositive: true }}
        />
        <StatCard
          title="Storage Used"
          value={`${stats?.storage_used_gb?.toFixed(1) || "0"} GB`}
          icon={HardDrive}
          description="Total storage"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-lg p-6 shadow-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Recent Activity
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div>
                <p className="font-medium">New user registration</p>
                <p className="text-sm text-muted-foreground">2 minutes ago</p>
              </div>
              <div className="w-2 h-2 bg-accent rounded-full" />
            </div>
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div>
                <p className="font-medium">Audiobook completed</p>
                <p className="text-sm text-muted-foreground">15 minutes ago</p>
              </div>
              <div className="w-2 h-2 bg-primary rounded-full" />
            </div>
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div>
                <p className="font-medium">Payment received</p>
                <p className="text-sm text-muted-foreground">1 hour ago</p>
              </div>
              <div className="w-2 h-2 bg-accent rounded-full" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6 shadow-card">
          <h3 className="text-lg font-semibold mb-4">System Status</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">API Health</span>
                <span className="text-sm text-accent">Operational</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-accent h-2 rounded-full w-[100%]" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Agent Activity</span>
                <span className="text-sm text-primary">High</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full w-[85%]" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Queue Length</span>
                <span className="text-sm text-yellow-500">Moderate</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full w-[45%]" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
