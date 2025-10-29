import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
      const response = await apiClient.request("/admin/agents/stats");
      return response as AgentStats;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  // Fetch agent jobs
  const { data: jobsData, isLoading: jobsLoading, refetch: refetchJobs } = useQuery({
    queryKey: ["agent-jobs", statusFilter],
    queryFn: async () => {
      const url = statusFilter === "all" 
        ? "/admin/agents/jobs"
        : `/admin/agents/jobs?status=${statusFilter}`;
      const response = await apiClient.request(url);
      return response as { jobs: AgentJob[]; total: number };
    },
    refetchInterval: 3000, // Refresh every 3 seconds for real-time feel
  });

  // Fetch job details
  const { data: jobDetails } = useQuery<JobDetails>({
    queryKey: ["agent-job-details", selectedJobId],
    queryFn: async () => {
      const response = await apiClient.request(`/admin/agents/jobs/${selectedJobId}`);
      return response as JobDetails;
    },
    enabled: !!selectedJobId,
  });

  // Fetch job logs
  const { data: logsData } = useQuery({
    queryKey: ["agent-job-logs", selectedJobId],
    queryFn: async () => {
      const response = await apiClient.request(`/admin/agents/jobs/${selectedJobId}/logs`);
      return response as { logs: JobLog[]; total: number };
    },
    enabled: !!selectedJobId && showLogs,
  });

  const handleRetryJob = async (jobId: string) => {
    try {
      await apiClient.request(`/admin/agents/jobs/${jobId}/retry`, {
        method: "POST",
      });
      toast.success("Job queued for retry");
      refetchJobs();
    } catch (error: any) {
      toast.error(error.message || "Failed to retry job");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "analyzing":
      case "scripting":
      case "synthesizing":
      case "post_processing":
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case "waiting_approval":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "failed":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "analyzing":
      case "scripting":
      case "synthesizing":
      case "post_processing":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "waiting_approval":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

  const formatCost = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const filteredJobs = jobsData?.jobs.filter((job) =>
    searchTerm === "" ||
    job.repo_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.user_email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Agent Execution Monitoring
        </h1>
        <p className="text-muted-foreground mt-2">
          Real-time monitoring of agent workflows and job execution
        </p>
      </div>

      {/* Stats Cards */}
      {statsLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse h-20 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Jobs</p>
                  <p className="text-2xl font-bold">{stats.total_jobs}</p>
                </div>
                <Activity className="h-8 w-8 text-primary opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Running</p>
                  <p className="text-2xl font-bold text-blue-500">{stats.running_jobs}</p>
                </div>
                <Loader2 className="h-8 w-8 text-blue-500 opacity-50 animate-spin" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="text-2xl font-bold text-green-500">{stats.completed_jobs}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Failed</p>
                  <p className="text-2xl font-bold text-red-500">{stats.failed_jobs}</p>
                </div>
                <XCircle className="h-8 w-8 text-red-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Recent (24h)</p>
                  <p className="text-2xl font-bold">{stats.recent_jobs_24h}</p>
                </div>
                {stats.recent_jobs_24h > stats.total_jobs / 10 ? (
                  <TrendingUp className="h-8 w-8 text-green-500 opacity-50" />
                ) : (
                  <TrendingDown className="h-8 w-8 text-gray-500 opacity-50" />
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg LLM Cost</p>
                  <p className="text-2xl font-bold">{formatCost(stats.avg_llm_cost_cents)}</p>
                </div>
                <DollarSign className="h-8 w-8 text-primary opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg TTS Cost</p>
                  <p className="text-2xl font-bold">{formatCost(stats.avg_tts_cost_cents)}</p>
                </div>
                <Zap className="h-8 w-8 text-accent opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Checkpoints</p>
                  <p className="text-2xl font-bold">{stats.total_checkpoints}</p>
                </div>
                <GitBranch className="h-8 w-8 text-muted-foreground opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Filters and Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Active Jobs</CardTitle>
          <CardDescription>Monitor and manage agent execution in real-time</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
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
            <div className="text-center py-12">
              <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-semibold">No jobs found</p>
              <p className="text-sm text-muted-foreground">
                Try adjusting your filters or search term
              </p>
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
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
                        <Badge variant="outline" className={getStatusColor(job.status)}>
                          <span className="flex items-center gap-1">
                            {getStatusIcon(job.status)}
                            {job.status}
                          </span>
                        </Badge>
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
                          <p>LLM: {formatCost(job.llm_cost_cents)}</p>
                          <p>TTS: {formatCost(job.tts_cost_cents)}</p>
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
                                      <Badge variant="outline" className={getStatusColor(jobDetails.status)}>
                                        {jobDetails.status}
                                      </Badge>
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">User</p>
                                      <p className="font-medium">{jobDetails.user.email}</p>
                                    </div>
                                    <div>
                                      <p className="text-sm text-muted-foreground">Price Paid</p>
                                      <p className="font-medium">{formatCost(jobDetails.price_paid_cents)}</p>
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
                                          <Card key={index}>
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
                                          <Card key={index}>
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
                                            className="bg-muted p-2 rounded border border-border"
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
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
