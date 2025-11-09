import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useGetJobTrace } from "@/lib/api/generated";
import { Button } from "@/components/ui/button";

// BLOCKED: retryJobStage endpoint not in OpenAPI spec
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const stub: any = null;
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
import {
  AgentMessageTraceEvent,
  AgentPromptTraceEvent,
  JobStage,
  ToolCallTraceEvent,
  WorkflowStepTrace,
  WorkflowTraceEvent,
} from "@/types/admin";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export default function JobTracing() {
  const [jobId, setJobId] = useState("");
  const [searchedJobId, setSearchedJobId] = useState("");
  const queryClient = useQueryClient();

  const { data: jobTrace, isLoading } = useGetJobTrace(searchedJobId, {
    query: {
      enabled: Boolean(searchedJobId),
      refetchInterval: (data) => {
        if (!searchedJobId) {
          return false;
        }
        // Check if tab is visible
        if (document.hidden) {
          return false;
        }
        if (!data) {
          return false;
        }
        return data.status === "completed" || data.status === "failed"
          ? false
          : 10000; // Increased from 4s to 10s
      },
      onError: (err) => {
        console.error(err);
        toast.error("Failed to load job trace");
      },
    },
  });

  const retryMutation = useMutation({
    mutationFn: ({
      jobId: id,
      stageName,
    }: {
      jobId: string;
      stageName: string;
    }) => stub.retryJobStage(id, stageName),
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
        return <CheckCircle2 className="h-5 w-5 text-success" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-danger" />;
      case "running":
        return <Play className="h-5 w-5 text-primary animate-pulse" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: "bg-success/10 text-success border-success/20",
      failed: "bg-danger/10 text-danger border-danger/20",
      running: "bg-primary/10 text-primary border-primary/20",
      pending: "bg-muted/40 text-muted-foreground border-border",
      queued: "bg-warning/10 text-warning border-warning/20",
      parsing: "bg-secondary/10 text-secondary border-secondary/20",
      generating: "bg-accent/10 text-accent border-accent/20",
      rendering: "bg-warning/10 text-warning border-warning/20",
    };
    return colors[status] || colors.queued;
  };

  const calculateProgress = () => {
    if (!jobTrace?.stages?.length) return 0;
    const completed = jobTrace.stages.filter(
      (stage: JobStage) => stage.status === "completed",
    ).length;
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

  const formatTimestamp = (value?: string) => {
    if (!value) {
      return "—";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "—";
    }
    return date.toLocaleString();
  };

  const formatPayload = (payload: unknown) => {
    if (payload === null || payload === undefined) {
      return "—";
    }
    if (typeof payload === "string") {
      const trimmed = payload.trim();
      if (!trimmed) {
        return "—";
      }
      try {
        const parsed = JSON.parse(trimmed);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return payload;
      }
    }
    if (typeof payload === "object") {
      return JSON.stringify(payload, null, 2);
    }
    return String(payload);
  };

  const getToolStatusColor = (status?: string) => {
    const normalized = status ? status.toLowerCase() : "";
    const colors: Record<string, string> = {
      ok: "bg-success/10 text-success border-success/20",
      completed: "bg-success/10 text-success border-success/20",
      success: "bg-success/10 text-success border-success/20",
      running: "bg-primary/10 text-primary border-primary/20",
      pending: "bg-muted/40 text-muted-foreground border-border",
      error: "bg-danger/10 text-danger border-danger/20",
      failed: "bg-danger/10 text-danger border-danger/20",
      forbidden: "bg-danger/10 text-danger border-danger/20",
    };
    return colors[normalized] || colors.pending;
  };

  const getAgentEventColor = (type: string) => {
    const colors: Record<string, string> = {
      agent_prompt: "bg-secondary/10 text-secondary border-secondary/20",
      agent_update: "bg-muted/40 text-muted-foreground border-border",
      agent_final: "bg-success/10 text-success border-success/20",
    };
    return colors[type] || colors.agent_update;
  };

  const isToolCallEvent = (
    event: WorkflowTraceEvent,
  ): event is ToolCallTraceEvent => !event.type || event.type === "tool_call";

  const isAgentPromptEvent = (
    event: WorkflowTraceEvent,
  ): event is AgentPromptTraceEvent => event.type === "agent_prompt";

  const isAgentMessageEvent = (
    event: WorkflowTraceEvent,
  ): event is AgentMessageTraceEvent =>
    event.type === "agent_update" || event.type === "agent_final";

  const summarizeText = (value?: string) => {
    if (!value) {
      return "—";
    }
    const trimmed = value.trim();
    if (trimmed.length <= 80) {
      return trimmed;
    }
    return `${trimmed.slice(0, 80)}…`;
  };

  const workflowSteps = useMemo(() => {
    if (!jobTrace) {
      return [] as WorkflowStepTrace[];
    }
    const traces = jobTrace.tool_traces ?? {};
    const stages = jobTrace.stages ?? [];
    const seen = new Set<string>();
    const steps: WorkflowStepTrace[] = stages.map((stage) => {
      seen.add(stage.name);
      return {
        step_id: stage.name,
        step_name: stage.name,
        status: stage.status,
        started_at: stage.started_at,
        completed_at: stage.completed_at,
        duration_ms: stage.duration_ms,
        allowed_tools: null,
        tool_calls: traces[stage.name] ?? [],
      };
    });
    for (const [name, events] of Object.entries(traces)) {
      if (seen.has(name)) {
        continue;
      }
      steps.push({
        step_id: name,
        step_name: name,
        status: "pending",
        started_at: undefined,
        completed_at: undefined,
        duration_ms: undefined,
        allowed_tools: null,
        tool_calls: events,
      });
    }
    return steps;
  }, [jobTrace]) as WorkflowStepTrace[];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-primary bg-clip-text text-transparent">
          Job Visualization & Tracing
        </h1>
        <p className="text-muted-foreground mt-2">
          Track job execution with detailed stage timeline and logs
        </p>
      </div>

      <Card className="bg-card">
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

      {searchedJobId && !jobTrace && !isLoading && (
        <Card className="bg-card">
          <CardContent className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-lg font-semibold mb-2">No job found</p>
            <p className="text-sm text-muted-foreground">
              Job ID "{searchedJobId}" not found. Please check the ID and try
              again.
            </p>
          </CardContent>
        </Card>
      )}

      {isLoading && (
        <Card className="bg-card">
          <CardContent className="text-center py-12">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
              <p className="text-muted-foreground">Loading job trace...</p>
            </div>
          </CardContent>
        </Card>
      )}

      {jobTrace && (
        <>
          <Card className="bg-card">
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
                  <Badge className={getStatusColor(jobTrace.status)}>
                    {jobTrace.status}
                  </Badge>
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
                  <p className="text-sm">
                    {new Date(jobTrace.started_at).toLocaleString()}
                  </p>
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
                <div className="bg-danger/10 rounded-card p-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 text-danger mt-0.5" />
                    <div>
                      <p className="font-semibold text-danger">Error</p>
                      <p className="text-sm mt-1">{jobTrace.error}</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-card">
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
                            <h4 className="font-semibold capitalize">
                              {stage.name}
                            </h4>
                            <div className="flex items-center gap-3 mt-1">
                              <Badge
                                variant="outline"
                                className={getStatusColor(stage.status)}
                              >
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
                                <a
                                  href={stage.logs_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
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
                          <div className="mt-2 text-sm text-danger bg-danger/10 rounded p-2">
                            {stage.error}
                          </div>
                        )}
                        {stage.started_at && (
                          <p className="text-xs text-muted-foreground mt-2">
                            Started:{" "}
                            {new Date(stage.started_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {workflowSteps.length > 0 && (
            <Card className="bg-card">
              <CardHeader>
                <CardTitle>Workflow Tool Trace</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Inspect tool calls and payloads captured from each workflow
                  step.
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                {workflowSteps.map((step) => {
                  const allowedList = Array.isArray(step.allowed_tools)
                    ? step.allowed_tools.filter(
                        (tool) =>
                          typeof tool === "string" && tool.trim().length > 0,
                      )
                    : [];
                  const statusBadge = getStatusColor(step.status);

                  return (
                    <Card
                      key={step.step_id}
                      className="border border-border/60 bg-background"
                    >
                      <CardHeader className="space-y-3">
                        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                          <div>
                            <CardTitle className="text-base">
                              {step.step_name}
                            </CardTitle>
                            <p className="text-xs text-muted-foreground">
                              Started {formatTimestamp(step.started_at)} •
                              Duration {formatDuration(step.duration_ms)}
                            </p>
                          </div>
                          <Badge className={statusBadge}>{step.status}</Badge>
                        </div>
                        {allowedList.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {allowedList.map((tool) => (
                              <Badge
                                key={tool}
                                variant="outline"
                                className="border-muted text-muted-foreground"
                              >
                                {tool}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </CardHeader>
                      <CardContent>
                        {step.tool_calls.length === 0 ? (
                          <p className="text-sm text-muted-foreground">
                            No tool activity recorded for this step.
                          </p>
                        ) : (
                          <Accordion type="multiple" className="space-y-2">
                            {step.tool_calls.map((event, index) => {
                              const eventType = event.type ?? "tool_call";
                              const fallbackKey = `${step.step_id}-${eventType}-${index}`;
                              const eventKey =
                                isToolCallEvent(event) &&
                                typeof event.id === "string" &&
                                event.id
                                  ? event.id
                                  : fallbackKey;

                              if (isToolCallEvent(event)) {
                                const toolEvent = event;
                                const badgeClass = getToolStatusColor(
                                  typeof toolEvent.status === "string"
                                    ? toolEvent.status
                                    : undefined,
                                );
                                const toolName =
                                  toolEvent.tool_name ||
                                  toolEvent.tool ||
                                  "Tool call";
                                const startedAt =
                                  toolEvent.started_at || toolEvent.called_at;
                                return (
                                  <AccordionItem
                                    key={eventKey}
                                    value={eventKey}
                                    className="overflow-hidden rounded-md border border-border"
                                  >
                                    <AccordionTrigger className="px-4 py-3 hover:no-underline">
                                      <div className="flex w-full items-start justify-between gap-4 text-left">
                                        <div>
                                          <p className="text-sm font-medium text-foreground">
                                            {toolName}
                                          </p>
                                          <p className="text-xs text-muted-foreground">
                                            Duration{" "}
                                            {formatDuration(toolEvent.duration_ms)} •
                                            Started{" "}
                                            {formatTimestamp(startedAt)}
                                          </p>
                                        </div>
                                        <Badge className={badgeClass}>
                                          {toolEvent.status ?? "pending"}
                                        </Badge>
                                      </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="bg-muted/30 px-4 py-4">
                                      <div className="grid gap-4 md:grid-cols-2">
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Input
                                          </p>
                                          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(
                                              toolEvent.input_payload ??
                                                toolEvent.input,
                                            )}
                                          </pre>
                                        </div>
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Output
                                          </p>
                                          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(
                                              toolEvent.output_payload ??
                                                toolEvent.output,
                                            )}
                                          </pre>
                                        </div>
                                      </div>
                                      {toolEvent.error && (
                                        <p className="mt-3 text-sm text-danger">
                                          {toolEvent.error}
                                        </p>
                                      )}
                                      <p className="mt-2 text-xs text-muted-foreground">
                                        Completed{" "}
                                        {formatTimestamp(toolEvent.completed_at)}
                                      </p>
                                    </AccordionContent>
                                  </AccordionItem>
                                );
                              }

                              if (isAgentPromptEvent(event)) {
                                const promptEvent = event;
                                const badgeClass = getAgentEventColor(
                                  promptEvent.type,
                                );
                                return (
                                  <AccordionItem
                                    key={eventKey}
                                    value={eventKey}
                                    className="overflow-hidden rounded-md border border-border"
                                  >
                                    <AccordionTrigger className="px-4 py-3 hover:no-underline">
                                      <div className="flex w-full items-start justify-between gap-4 text-left">
                                        <div>
                                          <p className="text-sm font-medium text-foreground">
                                            Prompt to {promptEvent.agent_name ?? "agent"}
                                          </p>
                                          <p className="text-xs text-muted-foreground">
                                            {summarizeText(promptEvent.prompt_text)}
                                          </p>
                                          <p className="text-xs text-muted-foreground">
                                            Sent {formatTimestamp(promptEvent.occurred_at)}
                                          </p>
                                        </div>
                                        <Badge className={badgeClass}>Prompt</Badge>
                                      </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="bg-muted/30 px-4 py-4 space-y-4">
                                      <div>
                                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                          Prompt
                                        </p>
                                        <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                          {formatPayload(promptEvent.prompt_text ?? "—")}
                                        </pre>
                                      </div>
                                      {promptEvent.system_prompt && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            System instructions
                                          </p>
                                          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(promptEvent.system_prompt)}
                                          </pre>
                                        </div>
                                      )}
                                      {promptEvent.prompt_template &&
                                        promptEvent.prompt_template !== promptEvent.prompt_text && (
                                          <div>
                                            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                              Template
                                            </p>
                                            <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                              {formatPayload(promptEvent.prompt_template)}
                                            </pre>
                                          </div>
                                        )}
                                      {promptEvent.message && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Serialized message
                                          </p>
                                          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(promptEvent.message)}
                                          </pre>
                                        </div>
                                      )}
                                    </AccordionContent>
                                  </AccordionItem>
                                );
                              }

                              if (isAgentMessageEvent(event)) {
                                const messageEvent = event;
                                const badgeClass = getAgentEventColor(
                                  messageEvent.type,
                                );
                                const label =
                                  messageEvent.type === "agent_final"
                                    ? "Model response"
                                    : "Model update";
                                return (
                                  <AccordionItem
                                    key={eventKey}
                                    value={eventKey}
                                    className="overflow-hidden rounded-md border border-border"
                                  >
                                    <AccordionTrigger className="px-4 py-3 hover:no-underline">
                                      <div className="flex w-full items-start justify-between gap-4 text-left">
                                        <div>
                                          <p className="text-sm font-medium text-foreground">
                                            {label}
                                            {messageEvent.agent_name
                                              ? ` from ${messageEvent.agent_name}`
                                              : ""}
                                          </p>
                                          <p className="text-xs text-muted-foreground">
                                            {summarizeText(messageEvent.text)}
                                          </p>
                                          <p className="text-xs text-muted-foreground">
                                            {formatTimestamp(messageEvent.occurred_at)}
                                            {messageEvent.role ? ` • ${messageEvent.role}` : ""}
                                          </p>
                                        </div>
                                        <Badge className={badgeClass}>{label}</Badge>
                                      </div>
                                    </AccordionTrigger>
                                    <AccordionContent className="bg-muted/30 px-4 py-4 space-y-4">
                                      {messageEvent.text && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Text
                                          </p>
                                          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(messageEvent.text)}
                                          </pre>
                                        </div>
                                      )}
                                      {messageEvent.value !== undefined &&
                                        messageEvent.value !== null && (
                                          <div>
                                            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                              Structured value
                                            </p>
                                            <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                              {formatPayload(messageEvent.value)}
                                            </pre>
                                          </div>
                                        )}
                                      {messageEvent.messages &&
                                        messageEvent.messages.length > 0 && (
                                          <div>
                                            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                              Messages
                                            </p>
                                            <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                              {formatPayload(messageEvent.messages)}
                                            </pre>
                                          </div>
                                        )}
                                      {messageEvent.message && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Raw event payload
                                          </p>
                                          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(messageEvent.message)}
                                          </pre>
                                        </div>
                                      )}
                                      {messageEvent.usage && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Usage
                                          </p>
                                          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(messageEvent.usage)}
                                          </pre>
                                        </div>
                                      )}
                                      {messageEvent.metadata && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Metadata
                                          </p>
                                          <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-background/80 p-3 text-xs text-muted-foreground">
                                            {formatPayload(messageEvent.metadata)}
                                          </pre>
                                        </div>
                                      )}
                                      {messageEvent.response_id && (
                                        <p className="text-xs text-muted-foreground">
                                          Response ID {messageEvent.response_id}
                                        </p>
                                      )}
                                    </AccordionContent>
                                  </AccordionItem>
                                );
                              }
                              return null;
                            })}
                          </Accordion>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
