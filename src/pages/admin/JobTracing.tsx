import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import {
  Search,
  Clock,
  CheckCircle2,
  XCircle,
  Play,
  RotateCcw,
  ExternalLink,
  AlertCircle,
} from "lucide-react";
import { JobStage } from "@/types/admin";

export default function JobTracing() {
  const [jobId, setJobId] = useState("");
  const [searchedJobId, setSearchedJobId] = useState("");
  const queryClient = useQueryClient();

  const { data: jobTrace, isLoading } = useQuery({
    queryKey: ["job-trace", searchedJobId],
    queryFn: () => apiClient.getJobTrace(searchedJobId),
    enabled: Boolean(searchedJobId),
  });

  const retryMutation = useMutation({
    mutationFn: ({ jobId: id, stageName }: { jobId: string; stageName: string }) =>
      apiClient.retryJobStage(id, stageName),
    onSuccess: () => {
      toast.success("Stage retry initiated");
      queryClient.invalidateQueries({ queryKey: ["job-trace"] });
    },
    onError: () => toast.error("Failed to retry stage"),
  });

  const handleSearch = () => {
    if (jobId.trim()) {
      setSearchedJobId(jobId.trim());
    }
  };

  const getStageIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "running":
        return <Play className="h-5 w-5 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: "bg-green-500/10 text-green-500 border-green-500/20",
      failed: "bg-red-500/10 text-red-500 border-red-500/20",
      running: "bg-blue-500/10 text-blue-500 border-blue-500/20",
      queued: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
      parsing: "bg-purple-500/10 text-purple-500 border-purple-500/20",
      generating: "bg-cyan-500/10 text-cyan-500 border-cyan-500/20",
      rendering: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    };
    return colors[status] || colors.queued;
  };

  const calculateProgress = () => {
    if (!jobTrace?.stages?.length) return 0;
    const completed = jobTrace.stages.filter((stage: JobStage) => stage.status === "completed").length;
    return (completed / jobTrace.stages.length) * 100;
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return "—";
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    }
    return `${seconds}s`;
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Job Visualization & Tracing
        </h1>
        <p className="text-muted-foreground mt-2">
          Track job execution with detailed stage timeline and logs
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search Job
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Enter Job ID..."
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="max-w-md"
            />
            <Button onClick={handleSearch} disabled={isLoading}>
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {jobTrace && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Job Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Job ID</p>
                  <p className="font-mono text-sm">{jobTrace.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">User</p>
                  <p className="font-mono text-sm">{jobTrace.user_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge className={getStatusColor(jobTrace.status)}>{jobTrace.status}</Badge>
                </div>
              </div>

              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Repository</p>
                  <a
                    href={jobTrace.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                  >
                    View Repo <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Started</p>
                  <p className="text-sm">{new Date(jobTrace.started_at).toLocaleString()}</p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span>{Math.round(calculateProgress())}%</span>
                </div>
                <Progress value={calculateProgress()} />
              </div>

              {jobTrace.error && (
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                    <div>
                      <p className="font-semibold text-destructive">Error</p>
                      <p className="text-sm mt-1">{jobTrace.error}</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Stage Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {jobTrace.stages.map((stage: JobStage, index: number) => (
                  <div key={stage.name} className="relative">
                    {index !== jobTrace.stages.length - 1 && (
                      <div className="absolute left-[11px] top-8 bottom-0 w-0.5 bg-border" />
                    )}
                    <div className="flex items-start gap-4">
                      <div className="mt-1">{getStageIcon(stage.status)}</div>
                      <div className="flex-1 pb-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold capitalize">{stage.name}</h4>
                            <div className="flex items-center gap-3 mt-1">
                              <Badge variant="outline" className={getStatusColor(stage.status)}>
                                {stage.status}
                              </Badge>
                              {stage.duration_ms && (
                                <span className="text-sm text-muted-foreground">
                                  Duration: {formatDuration(stage.duration_ms)}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {stage.logs_url && (
                              <Button size="sm" variant="outline" asChild>
                                <a href={stage.logs_url} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-3 w-3 mr-1" />
                                  Logs
                                </a>
                              </Button>
                            )}
                            {stage.status === "failed" && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() =>
                                  retryMutation.mutate({
                                    jobId: jobTrace.id,
                                    stageName: stage.name,
                                  })
                                }
                                disabled={retryMutation.isPending}
                              >
                                <RotateCcw className="h-3 w-3 mr-1" />
                                Retry
                              </Button>
                            )}
                          </div>
                        </div>
                        {stage.error && (
                          <div className="mt-2 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded p-2">
                            {stage.error}
                          </div>
                        )}
                        {stage.started_at && (
                          <p className="text-xs text-muted-foreground mt-2">
                            Started: {new Date(stage.started_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
