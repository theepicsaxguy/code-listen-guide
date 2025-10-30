import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/admin/StatCard";
import { StatusBadge } from "@/components/admin/StatusBadge";
import { DataTable, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, DataTableEmpty } from "@/components/admin/DataTable";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import {
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  RefreshCw,
  Eye,
  TrendingUp,
  TrendingDown,
  Zap,
  DollarSign,
  AlertCircle,
  GitBranch,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { formatCurrency } from "@/lib/theme";

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "completed":
    case "active":
      return "bg-green-500/10 text-green-500 border-green-500/20";
    case "running":
    case "in_progress":
      return "bg-blue-500/10 text-blue-500 border-blue-500/20";
    case "failed":
    case "error":
      return "bg-red-500/10 text-red-500 border-red-500/20";
    case "pending":
    case "waiting":
      return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
    default:
      return "bg-gray-500/10 text-muted-foreground";
  }
};

interface AgentJob {
  id: string;
  user_email: string;
  user_name: string;
  repo_url: string;
  repo_name: string;
  repo_owner: string;
  git_ref: string;
  depth_tier: string;
  status: string;
  progress_percentage: number;
  current_stage: string | null;
  estimated_duration_minutes: number | null;
  estimated_chapters: number | null;
  price_paid_cents: number;
  llm_cost_cents: number;
  tts_cost_cents: number;
  created_at: string;
  updated_at: string;
  error_message: string | null;
  checkpoint: {
    step: string | null;
    metadata: any;
    updated_at: string | null;
  } | null;
}

interface AgentStats {
  total_jobs: number;
  running_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  pending_jobs: number;
  recent_jobs_24h: number;
  avg_llm_cost_cents: number;
  avg_tts_cost_cents: number;
  total_checkpoints: number;
}

interface JobDetails extends AgentJob {
  user: {
    id: string | null;
    email: string | null;
    name: string | null;
  };
  checkpoints: Array<{
    step: string;
    metadata: any;
    thread_state: any;
    created_at: string;
    updated_at: string;
  }>;
  stages: Array<{
    name: string;
    status: string;
    started_at: string;
    metadata: any;
  }>;
  metadata: any;
}

interface JobLog {
  timestamp: string;
  step: string;
  message: string;
  metadata: any;
}

export default function AgentMonitoring() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(false);

  // Fetch agent stats
  const { data: stats, isLoading: statsLoading } = useQuery<AgentStats>({
    queryKey: ["agent-stats"],
    queryFn: async () => {
      const response = await apiClient.getAgentStats();
      return response as AgentStats;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  // Fetch agent jobs
  const { data: jobsData, isLoading: jobsLoading, refetch: refetchJobs } = useQuery({
    queryKey: ["agent-jobs", statusFilter],
    queryFn: async () => {
      const status = statusFilter === "all" ? undefined : statusFilter;
      const response = await apiClient.getAgentJobs(status);
      return response as { jobs: AgentJob[]; total: number };
    },
    refetchInterval: 3000, // Refresh every 3 seconds for real-time feel
  });

  // Fetch job details
  const { data: jobDetails } = useQuery<JobDetails>({
    queryKey: ["agent-job-details", selectedJobId],
    queryFn: async () => {
      const response = await apiClient.getAgentJobDetails(selectedJobId!);
      return response as JobDetails;
    },
    enabled: !!selectedJobId,
  });

  // Fetch job logs
  const { data: logsData } = useQuery({
    queryKey: ["agent-job-logs", selectedJobId],
    queryFn: async () => {
      const response = await apiClient.getAgentJobLogs(selectedJobId!);
      return response as { logs: JobLog[]; total: number };
    },
    enabled: !!selectedJobId && showLogs,
  });

  const handleRetryJob = async (jobId: string) => {
    try {
      await apiClient.restartAgentJob(jobId);
      toast.success("Job queued for retry");
      refetchJobs();
    } catch (error: any) {
      toast.error(error.message || "Failed to retry job");
    }
  };


  const filteredJobs = jobsData?.jobs.filter((job) =>
    searchTerm === "" ||
    job.repo_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.user_email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Agent Execution Monitoring</h1>
        <p className="text-muted-foreground mt-1">
          Real-time monitoring of agent workflows and job execution
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="bg-card">
                <CardContent className="p-6">
                  <div className="animate-pulse h-20 bg-muted rounded" />
                </CardContent>
              </Card>
            ))}
          </>
        ) : (
          <>
            <StatCard
              title="Total Jobs"
              value={stats.total_jobs}
              icon={Activity}
              description="All time"
            />
            <StatCard
              title="Running Jobs"
              value={stats.running_jobs}
              icon={Loader2}
              description="Currently active"
            />
            <StatCard
              title="Completed"
              value={stats.completed_jobs}
              icon={CheckCircle2}
              description="Successfully finished"
            />
            <StatCard
              title="Failed"
              value={stats.failed_jobs}
              icon={XCircle}
              description="Requires attention"
            />
            <StatCard
              title="Recent (24h)"
              value={stats.recent_jobs_24h}
              icon={stats.recent_jobs_24h > stats.total_jobs / 10 ? TrendingUp : TrendingDown}
              description="Last 24 hours"
            />
            <StatCard
              title="Avg LLM Cost"
              value={formatCurrency(stats.avg_llm_cost_cents)}
              icon={DollarSign}
              description="Per job"
            />
            <StatCard
              title="Avg TTS Cost"
              value={formatCurrency(stats.avg_tts_cost_cents)}
              icon={Zap}
              description="Per job"
            />
            <StatCard
              title="Checkpoints"
              value={stats.total_checkpoints}
              icon={GitBranch}
              description="Total saved states"
            />
          </>
        )}
      </div>

      {/* Filters and Controls */}
      <Card className="bg-card shadow-card">
        <CardHeader>
          <CardTitle>Active Jobs</CardTitle>
          <CardDescription>Monitor and manage agent execution in real-time</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              placeholder="Search by repo name or user email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="analyzing">Analyzing</SelectItem>
                <SelectItem value="waiting_approval">Waiting Approval</SelectItem>
                <SelectItem value="scripting">Scripting</SelectItem>
                <SelectItem value="synthesizing">Synthesizing</SelectItem>
                <SelectItem value="post_processing">Post Processing</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={() => refetchJobs()} disabled={jobsLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${jobsLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>

          {jobsLoading ? (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground mt-2">Loading jobs...</p>
            </div>
          ) : filteredJobs.length === 0 ? (
            <DataTableEmpty
              title="No jobs found"
              description="Try adjusting your filters or search term"
            />
          ) : (
            <DataTable>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Repository</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead>Costs</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredJobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{job.repo_name}</p>
                          <p className="text-xs text-muted-foreground">{job.repo_owner}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm">{job.user_name}</p>
                          <p className="text-xs text-muted-foreground">{job.user_email}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={job.status} />
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <Progress value={job.progress_percentage} className="h-2" />
                          <p className="text-xs text-muted-foreground">
                            {Math.round(job.progress_percentage)}%
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{job.current_stage || "—"}</span>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm space-y-1">
                          <p>LLM: {formatCurrency(job.llm_cost_cents)}</p>
                          <p>TTS: {formatCurrency(job.tts_cost_cents)}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedJobId(job.id);
                                setShowLogs(false);
                              }}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              Details
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle>Job Details: {job.repo_name}</DialogTitle>
                              <DialogDescription>
                                Job ID: {job.id}
                              </DialogDescription>
                            </DialogHeader>

                            {jobDetails && jobDetails.id === job.id ? (
                              <Tabs defaultValue="overview">
                                <TabsList className="grid w-full grid-cols-4">
                                  <TabsTrigger value="overview">Overview</TabsTrigger>
                                  <TabsTrigger value="stages">Stages</TabsTrigger>
                                  <TabsTrigger value="checkpoints">Checkpoints</TabsTrigger>
                                  <TabsTrigger value="logs" onClick={() => setShowLogs(true)}>
                                    Logs
                                  </TabsTrigger>
                                </TabsList>

                                <TabsContent value="overview" className="space-y-4">
                                  <div className="grid grid-cols-2 gap-4">
                                    <div>
                                      <p className="text-sm text-muted-foreground">Repository</p>
                                      <p className="font-medium">{jobDetails.repo_url}</p>
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">Git Ref</p>
                                      <p className="font-medium">{jobDetails.git_ref}</p>
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">Depth Tier</p>
                                      <Badge>{jobDetails.depth_tier}</Badge>
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">Status</p>
                                      <StatusBadge status={jobDetails.status} />
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">User</p>
                                      <p className="font-medium">{jobDetails.user.email}</p>
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">Price Paid</p>
                                      <p className="font-medium">{formatCurrency(jobDetails.price_paid_cents)}</p>
                                    </div>
                                  </div>

                                  {jobDetails.error_message && (
                                    <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
                                      <div className="flex items-start gap-2">
                                        <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                                        <div>
                                          <p className="font-semibold text-destructive">Error</p>
                                          <p className="text-sm mt-1">{jobDetails.error_message}</p>
                                        </div>
                                      </div>
                                    </div>
                                  )}

                                  {jobDetails.status === "failed" && (
                                    <Button
                                      onClick={() => handleRetryJob(jobDetails.id)}
                                      className="w-full"
                                    >
                                      <RefreshCw className="h-4 w-4 mr-2" />
                                      Retry Job
                                    </Button>
                                  )}
                                </TabsContent>

                                <TabsContent value="stages">
                                  <ScrollArea className="h-[400px]">
                                    <div className="space-y-4">
                                      {jobDetails.stages && jobDetails.stages.length > 0 ? (
                                        jobDetails.stages.map((stage, index) => (
                                          <Card key={index} className="bg-card">
                                            <CardContent className="p-4">
                                              <div className="flex items-center justify-between">
                                                <div>
                                                  <p className="font-semibold capitalize">{stage.name}</p>
                                                  <p className="text-sm text-muted-foreground">
                                                    {formatDistanceToNow(new Date(stage.started_at), {
                                                      addSuffix: true,
                                                    })}
                                                  </p>
                                                </div>
                                                <Badge
                                                  variant="outline"
                                                  className={getStatusColor(stage.status)}
                                                >
                                                  {stage.status}
                                                </Badge>
                                              </div>
                                            </CardContent>
                                          </Card>
                                        ))
                                      ) : (
                                        <p className="text-center text-muted-foreground py-8">
                                          No stage information available
                                        </p>
                                      )}
                                    </div>
                                  </ScrollArea>
                                </TabsContent>

                                <TabsContent value="checkpoints">
                                  <ScrollArea className="h-[400px]">
                                    <div className="space-y-2">
                                      {jobDetails.checkpoints && jobDetails.checkpoints.length > 0 ? (
                                        jobDetails.checkpoints.map((checkpoint, index) => (
                                          <Card key={index} className="bg-card">
                                            <CardContent className="p-3">
                                              <div className="flex items-center justify-between">
                                                <div>
                                                  <p className="text-sm font-medium">{checkpoint.step}</p>
                                                  <p className="text-xs text-muted-foreground">
                                                    {new Date(checkpoint.updated_at).toLocaleString()}
                                                  </p>
                                                </div>
                                                <GitBranch className="h-4 w-4 text-muted-foreground" />
                                              </div>
                                            </CardContent>
                                          </Card>
                                        ))
                                      ) : (
                                        <p className="text-center text-muted-foreground py-8">
                                          No checkpoints recorded yet
                                        </p>
                                      )}
                                    </div>
                                  </ScrollArea>
                                </TabsContent>

                                <TabsContent value="logs">
                                  <ScrollArea className="h-[400px]">
                                    <div className="space-y-2 font-mono text-xs">
                                      {logsData?.logs && logsData.logs.length > 0 ? (
                                        logsData.logs.map((log, index) => (
                                          <div
                                            key={index}
                                            className="bg-muted p-2 rounded"
                                          >
                                            <div className="flex items-start justify-between gap-2">
                                              <p className="text-muted-foreground">
                                                {new Date(log.timestamp).toLocaleTimeString()}
                                              </p>
                                              <Badge variant="outline" className="text-xs">
                                                {log.step}
                                              </Badge>
                                            </div>
                                            <p className="mt-1">{log.message}</p>
                                          </div>
                                        ))
                                      ) : (
                                        <p className="text-center text-muted-foreground py-8">
                                          No logs available
                                        </p>
                                      )}
                                    </div>
                                  </ScrollArea>
                                </TabsContent>
                              </Tabs>
                            ) : (
                              <div className="flex items-center justify-center py-12">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                              </div>
                            )}
                          </DialogContent>
                        </Dialog>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </DataTable>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
