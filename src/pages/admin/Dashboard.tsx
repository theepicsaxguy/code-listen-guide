import { useEffect, useState } from "react";
import { Activity, DollarSign, HardDrive, TrendingUp, Users, Bot, Package, GitBranch } from "lucide-react";
import { Link } from "react-router-dom";

import { StatCard } from "@/components/admin/StatCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  useGetDashboardStatsApiV1AdminDashboardStatsGet,
  useListWorkflowsApiV1AdminWorkflowsGet,
  useGetAgentRegistryApiV1AdminAgentsRegistryGet,
  useGetToolRegistryApiV1AdminToolsRegistryGet,
} from "@/lib/api/generated";
import { DashboardStats } from "@/types/admin";
import { toast } from "sonner";

export default function AdminDashboard() {
 const { data: stats, isLoading } = useGetDashboardStatsApiV1AdminDashboardStatsGet();

 const { data: workflows } = useListWorkflowsApiV1AdminWorkflowsGet({
   query: { staleTime: 60000 },
 });

 const { data: agentsResponse } = useGetAgentRegistryApiV1AdminAgentsRegistryGet({
   query: { staleTime: 60000 },
 });
 const agents = agentsResponse?.agents;

 const { data: pluginsResponse } = useGetToolRegistryApiV1AdminToolsRegistryGet({
   query: { staleTime: 60000 },
 });
 const plugins = pluginsResponse?.tools;

 if (isLoading) {
 return (
        <div className="mx-auto max-w-content-default px-6 py-6">
 <div className="space-y-4">
 <div className="h-9 w-48 rounded-md bg-muted/20" />
 <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
 {Array.from({ length: 4 }).map((_, index) => (
 <div key={index} className="h-32 rounded-card bg-muted/20" />
 ))}
 </div>
 </div>
 </div>
 );
 }

 return (
 <div className="bg-background text-text">
        <div className="mx-auto max-w-content-default space-y-8 px-6 py-8">
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

 <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
 <Link to="/admin/agents/manage">
 <Card className="rounded-card bg-surface border-zinc-800 transition-card hover:border-primary/50 cursor-pointer">
 <CardHeader className="space-y-1 px-6 pt-6">
 <CardTitle className="text-lg font-semibold text-foreground-h2 flex items-center gap-2">
 <Bot className="h-5 w-5" />
 Agents
 </CardTitle>
 <CardDescription className="text-muted-foreground">
 {agents?.length ?? 0} registered agents
 </CardDescription>
 </CardHeader>
 </Card>
 </Link>

 <Link to="/admin/plugins">
 <Card className="rounded-card bg-surface border-zinc-800 transition-card hover:border-primary/50 cursor-pointer">
 <CardHeader className="space-y-1 px-6 pt-6">
 <CardTitle className="text-lg font-semibold text-foreground-h2 flex items-center gap-2">
 <Package className="h-5 w-5" />
 Plugins
 </CardTitle>
 <CardDescription className="text-muted-foreground">
 {plugins?.length ?? 0} available plugins
 </CardDescription>
 </CardHeader>
 </Card>
 </Link>

 <Link to="/admin/workflows">
 <Card className="rounded-card bg-surface border-zinc-800 transition-card hover:border-primary/50 cursor-pointer">
 <CardHeader className="space-y-1 px-6 pt-6">
 <CardTitle className="text-lg font-semibold text-foreground-h2 flex items-center gap-2">
 <GitBranch className="h-5 w-5" />
 Workflows
 </CardTitle>
 <CardDescription className="text-muted-foreground">
 {workflows?.length ?? 0} workflow definitions
 </CardDescription>
 </CardHeader>
 </Card>
 </Link>
 </div>

 <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card className="rounded-card bg-surface border-zinc-800 transition-card">
        <CardHeader className="space-y-1 px-6 pt-6">
          <CardTitle className="text-lg font-semibold text-foreground-h2">Recent activity</CardTitle>
          <CardDescription className="text-muted-foreground">System activity overview</CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6">
          <Separator className="mb-4" />
          <div className="flex flex-col items-center justify-center py-12">
            <Activity className="h-10 w-10 mb-4 text-zinc-500 stroke-[1.5]" />
            <p className="text-sm font-medium text-foreground-h2 mb-1">No recent activity</p>
            <p className="text-sm text-muted-foreground text-center max-w-md">
              Activity tracking is coming soon. Visit Content and Users for granular details.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-card bg-surface border-zinc-800 transition-card">
        <CardHeader className="space-y-1 px-6 pt-6">
          <CardTitle className="text-lg font-semibold text-foreground-h2">System status</CardTitle>
          <CardDescription className="text-muted-foreground">Key infrastructure signals</CardDescription>
        </CardHeader>
 <CardContent className="space-y-4">
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-foreground-muted">API health</span>
            <span className="text-xs font-semibold uppercase tracking-wide text-success">Operational</span>
          </div>
          <Progress value={100} className="h-1.5 bg-surface-secondary" />
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-foreground-muted">Active jobs</span>
            <span className="text-xs font-semibold text-zinc-300">{stats?.active_jobs ?? 0}</span>
          </div>
          <Progress value={Math.min(100, (stats?.active_jobs ?? 0) * 10)} className="h-1.5 bg-surface-secondary" />
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-foreground-muted">Total users</span>
            <span className="text-xs font-semibold text-zinc-300">{stats?.total_users ?? 0}</span>
          </div>
          <Progress value={Math.min(100, stats?.total_users ?? 0)} className="h-1.5 bg-surface-secondary" />
        </div>
      </div>
 </CardContent>
 </Card>
 </div>

      <Card className="rounded-card bg-surface border-zinc-800 transition-card">
        <CardHeader className="space-y-1 px-6 pt-6">
          <CardTitle className="text-lg font-semibold text-foreground-h2">Revenue trend</CardTitle>
          <CardDescription className="text-muted-foreground">High-level view of revenue momentum</CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6">
          <div className="flex flex-col items-center justify-center py-12">
            <TrendingUp className="h-10 w-10 mb-4 text-zinc-500 stroke-[1.5]" />
            <p className="text-sm font-medium text-foreground-h2 mb-1">Analytics coming soon</p>
            <p className="text-sm text-muted-foreground text-center max-w-md">
              More detailed revenue analytics will appear here.
            </p>
          </div>
        </CardContent>
      </Card>
 </div>
 </div>
 );
}
