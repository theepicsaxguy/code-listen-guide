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
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">
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
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-purple-500" />
            Recent Activity
          </h3>
          <div className="text-center py-8 text-gray-400">
            <p>Activity tracking coming soon</p>
            <p className="text-sm mt-2">Check the Content and Users pages for detailed information</p>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">API Health</span>
                <span className="text-sm text-green-500">Operational</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full w-[100%]" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Active Jobs</span>
                <span className="text-sm text-primary">{stats?.active_jobs || 0}</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${Math.min(100, (stats?.active_jobs || 0) * 10)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Total Users</span>
                <span className="text-sm text-primary">{stats?.total_users || 0}</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all duration-300" 
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
