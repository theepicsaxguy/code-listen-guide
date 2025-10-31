import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
 ArrowLeft,
 GitBranch,
 Play,
 AlertCircle,
 CheckCircle2,
 Settings,
 Edit,
 Plus,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { WorkflowWithSteps, WorkflowRevision } from "@/lib/types/workflow";
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

 const fetchWorkflow = useCallback(async () => {
 if (!workflowId) return;

 setIsLoading(true);
 try {
 const [workflowData, revisionsData] = await Promise.all([
 apiClient.getWorkflow(workflowId),
 apiClient.getWorkflowRevisions(workflowId),
 ]);
 setWorkflow(workflowData);
 setRevisions(revisionsData.revisions || []);
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

 if (isLoading) {
 return (
 <div className="p-8">
 <div className="text-center text-muted-foreground">Loading workflow...</div>
 </div>
 );
 }

 if (!workflow) {
 return (
 <div className="p-8">
 <div className="text-center text-muted-foreground">Workflow not found</div>
 </div>
 );
 }

 return (
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
 <p className="text-muted-foreground mt-2">{workflow.description || "No description"}</p>
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
 onClick={() => navigate(`/admin/workflows/${workflowId}/new-revision`)}
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
 <Badge variant="outline" className="border-primary text-primary">
 {workflow.current_revision.steps?.length || 0} steps
 </Badge>
 </div>
 <p className="text-sm text-muted-foreground">
 Published{" "}
 {workflow.current_revision.published_at
 ? formatDistanceToNow(new Date(workflow.current_revision.published_at), {
 addSuffix: true,
 })
 : "—"}
 </p>
 </div>
 ) : (
 <p className="text-muted-foreground">No published version</p>
 )}
 </div>

 <div className="bg-surface border border-accent/20 rounded-lg p-6 shadow-lg">
 <h3 className="text-sm font-semibold text-muted-foreground mb-2">Total Revisions</h3>
 <p className="text-3xl font-bold text-foreground">{revisions.length}</p>
 </div>
 </div>

 {workflow.current_revision?.steps && workflow.current_revision.steps.length > 0 && (
 <div className="bg-surface border border-primary/20 rounded-lg p-6 shadow-lg">
 <h3 className="text-lg font-semibold text-foreground mb-4">Current Workflow Steps</h3>
 <div className="space-y-3">
 {workflow.current_revision.steps
 .sort((a, b) => a.step_order - b.step_order)
 .map((step, index) => (
 <div
 key={step.id}
 className="flex items-center gap-4 p-4 bg-background/50 rounded-lg border border-primary/10"
 >
 <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold shadow-lg shadow-primary/20">
 {index + 1}
 </div>
 <div className="flex-1">
 <div className="flex items-center gap-2">
 <h4 className="font-semibold text-foreground">{step.step_name}</h4>
 <Badge variant="outline" className="border-muted text-muted-foreground text-xs">
 {step.execution_mode || "sequential"}
 </Badge>
 {step.checkpoint_enabled && (
 <Badge variant="outline" className="border-primary text-primary text-xs">
 <CheckCircle2 className="h-3 w-3 mr-1" />
 Checkpoint
 </Badge>
 )}
 </div>
 {step.agent_name && (
 <p className="text-sm text-muted-foreground mt-1">
 Agent: <span className="font-mono">{step.agent_name}</span>
 </p>
 )}
 </div>
 <Button
 variant="ghost"
 size="sm"
 onClick={() => {/* TODO: View step details */}}
 >
 <Settings className="h-4 w-4" />
 </Button>
 </div>
 ))}
 </div>
 </div>
 )}

 <div className="bg-surface border border-primary/20 rounded-lg shadow-lg overflow-hidden">
 <div className="p-4 border-b border-primary/10">
 <h3 className="text-lg font-semibold text-foreground">Revision History</h3>
 </div>
 {revisions.length === 0 ? (
 <div className="p-8 text-center text-muted-foreground">No revisions created yet</div>
 ) : (
 <Table>
 <TableHeader>
 <TableRow className="border-primary/10 hover:bg-transparent">
 <TableHead className="text-foreground font-semibold">Version</TableHead>
 <TableHead className="text-foreground font-semibold">Status</TableHead>
 <TableHead className="text-foreground font-semibold">Steps</TableHead>
 <TableHead className="text-foreground font-semibold">Created</TableHead>
 <TableHead className="text-foreground font-semibold">Published</TableHead>
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
 <Badge variant="outline" className="border-accent text-accent">
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
 <Badge variant="outline" className="border-muted text-muted-foreground gap-1">
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
 {formatDistanceToNow(new Date(revision.created_at), { addSuffix: true })}
 </TableCell>
 <TableCell className="text-muted-foreground">
 {revision.published_at
 ? formatDistanceToNow(new Date(revision.published_at), {
 addSuffix: true,
 })
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
 );
}
