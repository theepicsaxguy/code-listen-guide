import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ArrowLeft,
  GitBranch,
  Play,
  AlertCircle,
  CheckCircle2,
  Settings,
  Edit,
  Plus,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import {
  WorkflowWithSteps,
  WorkflowRevision,
  WorkflowStep,
  ToolRegistry,
} from "@/lib/types/workflow";
import { normalizeWorkflow, normalizeRevisionList } from "@/lib/workflow-utils";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDistanceToNow } from "date-fns";

export default function WorkflowDetails() {
  const { workflowId } = useParams<{ workflowId: string }>();
  const navigate = useNavigate();
  const [workflow, setWorkflow] = useState<WorkflowWithSteps | null>(null);
  const [revisions, setRevisions] = useState<WorkflowRevision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [toolRegistry, setToolRegistry] = useState<ToolRegistry[]>([]);
  const [isStepEditorOpen, setIsStepEditorOpen] = useState(false);
  const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);
  const [allowedTools, setAllowedTools] = useState<string[]>([]);
  const [stepConfigText, setStepConfigText] = useState("{}");
  const [isSavingStep, setIsSavingStep] = useState(false);
  const [stepError, setStepError] = useState<string | null>(null);
  const [customToolName, setCustomToolName] = useState("");

  const toolOptions = useMemo(
    () =>
      toolRegistry
        .map((tool) => tool.name)
        .filter((name): name is string => Boolean(name))
        .sort((a, b) => a.localeCompare(b)),
    [toolRegistry],
  );

  const fetchWorkflow = useCallback(async () => {
    if (!workflowId) return;

    setIsLoading(true);
    try {
      const [workflowData, revisionsData] = await Promise.all([
        apiClient.getWorkflow(workflowId),
        apiClient.getWorkflowRevisions(workflowId),
      ]);
      const normalizedWorkflow = normalizeWorkflow(workflowData);
      const normalizedRevisions = normalizeRevisionList(
        revisionsData,
        workflowId,
      );
      setWorkflow(normalizedWorkflow);
      setRevisions(normalizedRevisions);
    } catch (error) {
      toast.error("Failed to load workflow details");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    void fetchWorkflow();
  }, [fetchWorkflow]);

  useEffect(() => {
    let mounted = true;
    const loadTools = async () => {
      try {
        const response = await apiClient.getToolRegistry();
        const tools = Array.isArray(response)
          ? response
          : (response?.tools ?? []);
        if (mounted) {
          setToolRegistry(tools);
        }
      } catch (error) {
        console.error(error);
      }
    };

    void loadTools();

    return () => {
      mounted = false;
    };
  }, []);

  const handleEditStep = (step: WorkflowStep) => {
    const uniqueTools = Array.from(
      new Set(
        (step.allowed_tools ?? []).filter(
          (tool) => typeof tool === "string" && tool.trim().length > 0,
        ),
      ),
    ).sort((a, b) => a.localeCompare(b));
    const configSource =
      step.step_config && Object.keys(step.step_config).length > 0
        ? step.step_config
        : {};

    setSelectedStep(step);
    setAllowedTools(uniqueTools);
    setStepConfigText(JSON.stringify(configSource, null, 2));
    setCustomToolName("");
    setStepError(null);
    setIsStepEditorOpen(true);
  };

  const handleToggleTool = (toolName: string) => {
    setAllowedTools((prev) => {
      const exists = prev.includes(toolName);
      if (exists) {
        return prev.filter((item) => item !== toolName);
      }
      return [...prev, toolName].sort((a, b) => a.localeCompare(b));
    });
  };

  const handleAddCustomTool = () => {
    const trimmed = customToolName.trim();
    if (!trimmed) {
      return;
    }
    setAllowedTools((prev) => {
      const next = new Set(prev.map((item) => item.trim()));
      next.add(trimmed);
      return Array.from(next).sort((a, b) => a.localeCompare(b));
    });
    setCustomToolName("");
  };

  const closeStepEditor = () => {
    setIsStepEditorOpen(false);
    setSelectedStep(null);
    setAllowedTools([]);
    setStepConfigText("{}");
    setStepError(null);
    setCustomToolName("");
  };

  const handleSaveStep = async () => {
    if (!workflowId || !selectedStep) {
      return;
    }

    let parsedConfig: Record<string, unknown> | null = {};

    try {
      const trimmed = stepConfigText.trim();
      if (!trimmed || trimmed === "{}") {
        parsedConfig = {};
      } else {
        const candidate = JSON.parse(trimmed);
        if (
          !candidate ||
          typeof candidate !== "object" ||
          Array.isArray(candidate)
        ) {
          throw new Error("Step configuration must be a JSON object");
        }
        parsedConfig = candidate as Record<string, unknown>;
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Invalid step configuration";
      setStepError(message);
      return;
    }

    const payloadAllowedTools = allowedTools
      .map((tool) => tool.trim())
      .filter((tool) => tool.length > 0);

    setIsSavingStep(true);
    setStepError(null);
    try {
      await apiClient.updateWorkflowStep(workflowId, selectedStep.id, {
        allowed_tools: payloadAllowedTools,
        step_config: parsedConfig,
      });
      toast.success("Step updated successfully");
      closeStepEditor();
      void fetchWorkflow();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to update step";
      setStepError(message);
      toast.error("Failed to update step");
      console.error(error);
    } finally {
      setIsSavingStep(false);
    }
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="text-center text-muted-foreground">
          Loading workflow...
        </div>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="p-8">
        <div className="text-center text-muted-foreground">
          Workflow not found
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="p-8 space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/admin/workflows")}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Workflows
          </Button>
        </div>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold gradient-text-primary flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
                <GitBranch className="w-6 h-6 text-primary-foreground" />
              </div>
              {workflow.name}
            </h1>
            <p className="text-muted-foreground mt-2">
              {workflow.description || "No description"}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => navigate(`/admin/workflows/${workflowId}/edit`)}
              className="gap-2"
            >
              <Edit className="h-4 w-4" />
              Edit
            </Button>
            <Button
              onClick={() =>
                navigate(`/admin/workflows/${workflowId}/new-revision`)
              }
              className="bg-primary gap-2"
            >
              <Plus className="h-4 w-4" />
              New Revision
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="bg-surface border border-primary/20 rounded-lg p-6 shadow-lg">
            <h3 className="text-sm font-semibold text-muted-foreground mb-2">
              Current Published Version
            </h3>
            {workflow.current_revision ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge className="bg-primary text-primary-foreground">
                    v{workflow.current_revision.version}
                  </Badge>
                  <Badge
                    variant="outline"
                    className="border-primary text-primary"
                  >
                    {workflow.current_revision.steps?.length || 0} steps
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  Published{" "}
                  {workflow.current_revision.published_at
                    ? formatDistanceToNow(
                        new Date(workflow.current_revision.published_at),
                        {
                          addSuffix: true,
                        },
                      )
                    : "—"}
                </p>
              </div>
            ) : (
              <p className="text-muted-foreground">No published version</p>
            )}
          </div>

          <div className="bg-surface border border-accent/20 rounded-lg p-6 shadow-lg">
            <h3 className="text-sm font-semibold text-muted-foreground mb-2">
              Total Revisions
            </h3>
            <p className="text-3xl font-bold text-foreground">
              {revisions.length}
            </p>
          </div>
        </div>

        {workflow.current_revision?.steps &&
          workflow.current_revision.steps.length > 0 && (
            <div className="bg-surface border border-primary/20 rounded-lg p-6 shadow-lg">
              <h3 className="text-lg font-semibold text-foreground mb-4">
                Current Workflow Steps
              </h3>
              <div className="space-y-4">
                {workflow.current_revision.steps
                  .sort((a, b) => a.step_order - b.step_order)
                  .map((step, index) => {
                    const allowedList = Array.isArray(step.allowed_tools)
                      ? step.allowed_tools.filter(
                          (tool) =>
                            typeof tool === "string" && tool.trim().length > 0,
                        )
                      : [];
                    const stepConfig =
                      step.step_config && typeof step.step_config === "object"
                        ? step.step_config
                        : {};
                    const hasConfig = Object.keys(stepConfig).length > 0;

                    return (
                      <div
                        key={step.id}
                        className="space-y-4 rounded-lg border border-primary/10 bg-background/50 p-4 shadow-sm"
                      >
                        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                          <div className="flex items-start gap-4">
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold shadow-lg shadow-primary/20">
                              {index + 1}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-semibold text-foreground">
                                  {step.step_name}
                                </h4>
                                <Badge
                                  variant="outline"
                                  className="border-muted text-muted-foreground text-xs capitalize"
                                >
                                  {step.execution_mode || "sequential"}
                                </Badge>
                                {step.checkpoint_enabled && (
                                  <Badge
                                    variant="outline"
                                    className="border-primary text-primary text-xs"
                                  >
                                    <CheckCircle2 className="h-3 w-3 mr-1" />
                                    Checkpoint
                                  </Badge>
                                )}
                              </div>
                              {step.agent_name && (
                                <p className="mt-1 text-sm text-muted-foreground">
                                  Agent:{" "}
                                  <span className="font-mono">
                                    {step.agent_name}
                                  </span>
                                </p>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                            onClick={() => handleEditStep(step)}
                          >
                            <Settings className="h-4 w-4" />
                            Configure
                          </Button>
                        </div>

                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              Allowed tools
                            </p>
                            {allowedList.length > 0 ? (
                              <div className="mt-2 flex flex-wrap gap-2">
                                {allowedList.map((tool) => (
                                  <Badge
                                    key={tool}
                                    variant="outline"
                                    className="border-primary/40 text-primary"
                                  >
                                    {tool}
                                  </Badge>
                                ))}
                              </div>
                            ) : (
                              <p className="mt-2 text-sm text-muted-foreground">
                                Inherits agent registry permissions
                              </p>
                            )}
                          </div>
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              Step configuration
                            </p>
                            {hasConfig ? (
                              <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-muted/30 p-3 text-xs text-muted-foreground">
                                {JSON.stringify(stepConfig, null, 2)}
                              </pre>
                            ) : (
                              <p className="mt-2 text-sm text-muted-foreground">
                                No overrides configured
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

        <div className="bg-surface border border-primary/20 rounded-lg shadow-lg overflow-hidden">
          <div className="p-4 border-b border-primary/10">
            <h3 className="text-lg font-semibold text-foreground">
              Revision History
            </h3>
          </div>
          {revisions.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No revisions created yet
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-primary/10 hover:bg-transparent">
                  <TableHead className="text-foreground font-semibold">
                    Version
                  </TableHead>
                  <TableHead className="text-foreground font-semibold">
                    Status
                  </TableHead>
                  <TableHead className="text-foreground font-semibold">
                    Steps
                  </TableHead>
                  <TableHead className="text-foreground font-semibold">
                    Created
                  </TableHead>
                  <TableHead className="text-foreground font-semibold">
                    Published
                  </TableHead>
                  <TableHead className="text-right text-foreground font-semibold">
                    Actions
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {revisions
                  .sort((a, b) => b.version - a.version)
                  .map((revision) => (
                    <TableRow
                      key={revision.id}
                      className="border-primary/10 hover:bg-primary/5 transition-colors"
                    >
                      <TableCell className="font-medium">
                        <Badge
                          variant="outline"
                          className="border-accent text-accent"
                        >
                          v{revision.version}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {revision.is_published ? (
                          <Badge className="bg-primary text-primary-foreground gap-1">
                            <Play className="h-3 w-3" />
                            Published
                          </Badge>
                        ) : (
                          <Badge
                            variant="outline"
                            className="border-muted text-muted-foreground gap-1"
                          >
                            <AlertCircle className="h-3 w-3" />
                            Draft
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {revision.revision_metadata?.steps_count || 0} steps
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatDistanceToNow(new Date(revision.created_at), {
                          addSuffix: true,
                        })}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {revision.published_at
                          ? formatDistanceToNow(
                              new Date(revision.published_at),
                              {
                                addSuffix: true,
                              },
                            )
                          : "—"}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm">
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>

      <Dialog
        open={isStepEditorOpen}
        onOpenChange={(open) => {
          if (!open) {
            closeStepEditor();
          } else {
            setIsStepEditorOpen(true);
          }
        }}
      >
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Configure Step</DialogTitle>
            <DialogDescription>
              {selectedStep
                ? `Update tool access and configuration for "${selectedStep.step_name}"`
                : "Update tool access and configuration for this step."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            <div className="space-y-3">
              <Label>Allowed tools</Label>
              {toolOptions.length > 0 ? (
                <ScrollArea className="h-40 rounded-md border border-border">
                  <div className="space-y-2 p-3">
                    {toolOptions.map((tool) => (
                      <label
                        key={tool}
                        className="flex items-center gap-2 text-sm text-foreground"
                      >
                        <Checkbox
                          checked={allowedTools.includes(tool)}
                          onCheckedChange={() => handleToggleTool(tool)}
                        />
                        <span>{tool}</span>
                      </label>
                    ))}
                  </div>
                </ScrollArea>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No tools are registered. Add tools in the registry to enable
                  overrides.
                </p>
              )}
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom tool"
                  value={customToolName}
                  onChange={(event) => setCustomToolName(event.target.value)}
                />
                <Button
                  type="button"
                  onClick={handleAddCustomTool}
                  disabled={!customToolName.trim()}
                >
                  Add
                </Button>
              </div>
              {allowedTools.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {allowedTools.map((tool) => (
                    <Badge key={tool} variant="secondary">
                      {tool}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            <div className="space-y-3">
              <Label htmlFor="step-config">Step configuration JSON</Label>
              <Textarea
                id="step-config"
                value={stepConfigText}
                onChange={(event) => setStepConfigText(event.target.value)}
                rows={10}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Provide a JSON object to override agent settings for this step.
                Leave empty to inherit defaults.
              </p>
            </div>
            {stepError && <p className="text-sm text-danger">{stepError}</p>}
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={closeStepEditor}
              disabled={isSavingStep}
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleSaveStep}
              disabled={isSavingStep}
              className="gap-2"
            >
              {isSavingStep ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving…
                </>
              ) : (
                "Save changes"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
