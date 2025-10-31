import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search, Plus, GitBranch, Play, Edit, Eye } from "lucide-react";
import { apiClient } from "@/lib/api";
import { WorkflowWithSteps } from "@/lib/types/workflow";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function WorkflowList() {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<WorkflowWithSteps[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchInput, setSearchInput] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState("");
  const [newWorkflowDescription, setNewWorkflowDescription] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const fetchWorkflows = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getWorkflows();
      setWorkflows(data.workflows || []);
    } catch (error) {
      toast.error("Failed to load workflows");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchWorkflows();
  }, [fetchWorkflows]);

  const handleCreateWorkflow = async () => {
    if (!newWorkflowName.trim()) {
      toast.error("Workflow name is required");
      return;
    }

    setIsCreating(true);
    try {
      const workflow = await apiClient.createWorkflow({
        name: newWorkflowName,
        description: newWorkflowDescription,
      });
      toast.success("Workflow created successfully");
      setIsCreateDialogOpen(false);
      setNewWorkflowName("");
      setNewWorkflowDescription("");
      navigate(`/admin/workflows/${workflow.id}`);
    } catch (error) {
      toast.error("Failed to create workflow");
      console.error(error);
    } finally {
      setIsCreating(false);
    }
  };

  const filteredWorkflows = workflows.filter(
    (workflow) =>
      workflow.name.toLowerCase().includes(searchInput.toLowerCase()) ||
      workflow.description?.toLowerCase().includes(searchInput.toLowerCase())
  );

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text-primary flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <GitBranch className="w-6 h-6 text-primary-foreground" />
          </div>
          Workflow Management
        </h1>
        <p className="text-muted-foreground mt-2">
          Configure and manage dynamic agent workflows
        </p>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-primary z-10" />
          <Input
            placeholder="Search workflows by name or description..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="pl-11 border-primary/30 focus:border-primary/60 focus:ring-primary/20"
          />
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-primary hover:opacity-90 text-primary-foreground shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 hover:-translate-y-0.5 px-8">
              <Plus className="w-4 h-4 mr-2" />
              New Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create New Workflow</DialogTitle>
              <DialogDescription>
                Define a new workflow that can be versioned and configured.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Workflow Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., audiobook_generation"
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Brief description of what this workflow does..."
                  value={newWorkflowDescription}
                  onChange={(e) => setNewWorkflowDescription(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
                disabled={isCreating}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateWorkflow}
                disabled={isCreating || !newWorkflowName.trim()}
                className="bg-gradient-primary"
              >
                {isCreating ? "Creating..." : "Create Workflow"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-gradient-card-primary border border-primary/20 rounded-xl shadow-lg overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-muted-foreground">
            Loading workflows...
          </div>
        ) : filteredWorkflows.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            {searchInput ? "No workflows match your search" : "No workflows created yet"}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-primary/10 hover:bg-transparent">
                <TableHead className="text-foreground font-semibold">Name</TableHead>
                <TableHead className="text-foreground font-semibold">Description</TableHead>
                <TableHead className="text-foreground font-semibold">Current Version</TableHead>
                <TableHead className="text-foreground font-semibold">Steps</TableHead>
                <TableHead className="text-foreground font-semibold">Status</TableHead>
                <TableHead className="text-right text-foreground font-semibold">
                  Actions
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredWorkflows.map((workflow) => (
                <TableRow
                  key={workflow.id}
                  className="border-primary/10 hover:bg-primary/5 transition-colors cursor-pointer"
                  onClick={() => navigate(`/admin/workflows/${workflow.id}`)}
                >
                  <TableCell className="font-medium text-foreground">
                    {workflow.name}
                  </TableCell>
                  <TableCell className="text-muted-foreground max-w-md truncate">
                    {workflow.description || "—"}
                  </TableCell>
                  <TableCell>
                    {workflow.current_revision ? (
                      <Badge variant="outline" className="border-accent text-accent">
                        v{workflow.current_revision.version}
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-muted text-muted-foreground">
                        No Published Version
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {workflow.current_revision?.steps ? (
                      <Badge variant="secondary">
                        {workflow.current_revision.steps.length} steps
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {workflow.current_revision?.is_published ? (
                      <Badge className="bg-gradient-primary text-primary-foreground">
                        Published
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-muted-foreground text-muted-foreground">
                        Draft
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex gap-2 justify-end" onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/admin/workflows/${workflow.id}`)}
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/admin/workflows/${workflow.id}/edit`)}
                        title="Edit Workflow"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="bg-gradient-card-secondary border border-accent/20 rounded-xl p-6 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-accent flex items-center justify-center shadow-lg shadow-accent/20">
              <GitBranch className="w-5 h-5 text-accent-foreground" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Workflows</p>
              <p className="text-2xl font-bold text-foreground">{workflows.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-card-primary border border-primary/20 rounded-xl p-6 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-lg shadow-primary/20">
              <Play className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Published</p>
              <p className="text-2xl font-bold text-foreground">
                {workflows.filter((w) => w.current_revision?.is_published).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-card-secondary border border-secondary/20 rounded-xl p-6 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-secondary flex items-center justify-center shadow-lg shadow-secondary/20">
              <Edit className="w-5 h-5 text-secondary-foreground" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Drafts</p>
              <p className="text-2xl font-bold text-foreground">
                {workflows.filter((w) => !w.current_revision?.is_published).length}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
