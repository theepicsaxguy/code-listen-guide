import { useEffect, useState } from "react";
import { Users, Activity, DollarSign, HardDrive, TrendingUp } from "lucide-react";
import { StatCard } from "@/components/admin/StatCard";
import { apiClient } from "@/lib/api";
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
    <div className="p-8 space-y-8 animate-slide-up">
      <div>
        <h1 className="text-3xl font-bold text-foreground tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2 text-base">
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
        <div className="bg-gradient-card-primary rounded-xl p-6 card-elevation">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-md shadow-primary/20">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">Recent Activity</h3>
              <p className="text-xs text-muted-foreground">System activity overview</p>
            </div>
          </div>
          <div className="text-center py-12 text-muted-foreground">
            <p className="font-medium mb-1">Activity tracking coming soon</p>
            <p className="text-sm">Check the Content and Users pages for detailed information</p>
          </div>
        </div>

        <div className="bg-gradient-card-accent rounded-xl p-6 card-elevation">
          <h3 className="text-lg font-bold text-foreground mb-6">System Status</h3>
          <div className="space-y-5">
            <div>
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-sm font-semibold text-foreground">API Health</span>
                <span className="text-sm font-bold text-success bg-success/10 px-2.5 py-1 rounded-full">Operational</span>
              </div>
              <div className="w-full bg-secondary/30 rounded-full h-2.5 overflow-hidden">
                <div className="bg-gradient-to-r from-success to-success/80 h-full rounded-full w-[100%] shadow-sm shadow-success/30" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-sm font-semibold text-foreground">Active Jobs</span>
                <span className="text-sm font-bold text-primary">{stats?.active_jobs || 0}</span>
              </div>
              <div className="w-full bg-secondary/30 rounded-full h-2.5 overflow-hidden">
                <div 
                  className="bg-gradient-primary h-full rounded-full transition-all duration-500 shadow-sm shadow-primary/30" 
                  style={{ width: `${Math.min(100, (stats?.active_jobs || 0) * 10)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-sm font-semibold text-foreground">Total Users</span>
                <span className="text-sm font-bold text-primary">{stats?.total_users || 0}</span>
              </div>
              <div className="w-full bg-secondary/30 rounded-full h-2.5 overflow-hidden">
                <div 
                  className="bg-gradient-accent h-full rounded-full transition-all duration-500 shadow-sm shadow-accent/30" 
                  style={{ width: `${Math.min(100, (stats?.total_users || 0))}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
