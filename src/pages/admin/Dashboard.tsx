import { useEffect, useState } from "react";
import { Activity, DollarSign, HardDrive, TrendingUp, Users } from "lucide-react";

import { StatCard } from "@/components/admin/StatCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
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
      <div className="mx-auto max-w-[1280px] px-6 py-6">
        <div className="space-y-4">
          <div className="h-9 w-48 rounded-md bg-muted/20" />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-32 rounded-lg bg-muted/20" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-background text-text">
      <div className="mx-auto max-w-[1280px] space-y-6 px-6 py-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Admin</p>
              <h1 className="text-4xl font-semibold text-text">Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Welcome back! Here's an overview of system performance.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total users"
            value={stats?.total_users?.toLocaleString() ?? "0"}
            icon={Users}
            description="Registered accounts"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="Active jobs"
            value={stats?.active_jobs ?? "0"}
            icon={Activity}
            description="Currently processing"
          />
          <StatCard
            title="Monthly revenue"
            value={`$${stats?.revenue_month?.toLocaleString() ?? "0"}`}
            icon={DollarSign}
            description="This month"
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard
            title="Storage used"
            value={`${stats?.storage_used_gb?.toFixed(1) ?? "0"} GB`}
            icon={HardDrive}
            description="Total storage"
          />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card className="rounded-lg border border-border bg-surface">
            <CardHeader className="space-y-2">
              <CardTitle className="text-lg font-semibold text-text">Recent activity</CardTitle>
              <CardDescription>System activity overview</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Separator />
              <p className="text-sm text-muted-foreground">
                Activity tracking is coming soon. Visit Content and Users for granular details.
              </p>
            </CardContent>
          </Card>

          <Card className="rounded-lg border border-border bg-surface">
            <CardHeader className="space-y-2">
              <CardTitle className="text-lg font-semibold text-text">System status</CardTitle>
              <CardDescription>Key infrastructure signals</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-text">API health</span>
                  <span className="text-xs font-semibold text-success">Operational</span>
                </div>
                <Progress value={100} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-text">Active jobs</span>
                  <span className="text-xs font-semibold text-primary">{stats?.active_jobs ?? 0}</span>
                </div>
                <Progress value={Math.min(100, (stats?.active_jobs ?? 0) * 10)} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-text">Total users</span>
                  <span className="text-xs font-semibold text-primary">{stats?.total_users ?? 0}</span>
                </div>
                <Progress value={Math.min(100, stats?.total_users ?? 0)} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="rounded-lg border border-border bg-surface">
          <CardHeader className="space-y-2">
            <CardTitle className="text-lg font-semibold text-text">Revenue trend</CardTitle>
            <CardDescription>High-level view of revenue momentum</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>More detailed revenue analytics will appear here.</span>
              <TrendingUp className="h-5 w-5 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
