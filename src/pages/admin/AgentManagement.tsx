import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Edit, Trash2, Bot, Package } from "lucide-react";
import { toast } from "sonner";

export default function AgentManagement() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data: agents, isLoading } = useQuery({
    queryKey: ["admin-agents"],
    queryFn: () => apiClient.listAgents(),
  });

  const { data: plugins } = useQuery({
    queryKey: ["admin-plugins"],
    queryFn: () => apiClient.listPlugins(),
  });

  const createMutation = useMutation({
    mutationFn: (agent: {
      name: string;
      module_path: string;
      factory_function: string;
      description?: string;
      config_schema?: Record<string, any>;
      tools?: string[];
    }) => apiClient.createAgent(agent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-agents"] });
      setIsCreateDialogOpen(false);
      toast.success("Agent created successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to create agent: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: any }) =>
      apiClient.updateAgent(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-agents"] });
      setIsEditDialogOpen(false);
      setEditingAgent(null);
      toast.success("Agent updated successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to update agent: ${error.message}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-agents"] });
      toast.success("Agent deleted successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete agent: ${error.message}`);
    },
  });

  const handleEdit = (agent: any) => {
    setEditingAgent(agent);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this agent?")) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-primary bg-clip-text text-transparent">
            Agent Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage AI agents, their plugins, and configurations
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Agent</DialogTitle>
              <DialogDescription>
                Register a new agent with plugins and configuration.
              </DialogDescription>
            </DialogHeader>
            <AgentForm
              plugins={plugins || []}
              onSubmit={(data) => {
                createMutation.mutate(data);
              }}
              isLoading={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-card">
        <CardHeader>
          <CardTitle>Agents</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-center text-muted-foreground py-8">Loading agents...</p>
          ) : !agents || agents.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No agents found</p>
              <p className="text-sm mt-2">Create your first agent to get started.</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Module</TableHead>
                  <TableHead>Factory</TableHead>
                  <TableHead>Plugins</TableHead>
                  <TableHead>Account ACL</TableHead>
                  <TableHead>Quota Limits</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agents.map((agent: any) => (
                    <TableRow key={agent.id}>
                      <TableCell className="font-medium">{agent.name}</TableCell>
                      <TableCell className="font-mono text-xs">{agent.module_path}</TableCell>
                      <TableCell className="font-mono text-xs">{agent.factory_function}</TableCell>
                      <TableCell>
                        {agent.tools && agent.tools.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {agent.tools.map((tool: any, idx: number) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {tool.name}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs">None</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {agent.account_acl && agent.account_acl.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {agent.account_acl.map((entry: string) => (
                              <Badge key={entry} variant="outline" className="text-xs">
                                {entry}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs">Open</span>
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs">
                        {agent.quota_limits && agent.quota_limits.length > 0 ? (
                          <div className="space-y-1">
                            {agent.quota_limits.map((entry: any, idx: number) => (
                              <div
                                key={idx}
                                className="text-xs font-mono bg-muted/40 rounded px-2 py-1 break-words"
                              >
                                {JSON.stringify(entry)}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-xs">None</span>
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {agent.description || "-"}
                      </TableCell>
                      <TableCell>
                        {new Date(agent.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(agent)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-danger"
                            onClick={() => handleDelete(agent.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Agent</DialogTitle>
            <DialogDescription>
              Update agent configuration and plugins.
            </DialogDescription>
          </DialogHeader>
          {editingAgent && (
            <AgentForm
              plugins={plugins || []}
              initialData={editingAgent}
              onSubmit={(data) => {
                updateMutation.mutate({ id: editingAgent.id, updates: data });
              }}
              isLoading={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function AgentForm({
  plugins,
  initialData,
  onSubmit,
  isLoading,
}: {
  plugins: any[];
  initialData?: any;
  onSubmit: (data: any) => void;
  isLoading: boolean;
}) {
  const [formData, setFormData] = useState({
    name: initialData?.name || "",
    module_path: initialData?.module_path || "",
    factory_function: initialData?.factory_function || "",
    description: initialData?.description || "",
    config_schema: initialData?.config_schema
      ? JSON.stringify(initialData.config_schema, null, 2)
      : "",
    selectedTools: initialData?.tools?.map((t: any) => t.id || t.name) || [],
    accountAclText:
      initialData?.account_acl && initialData.account_acl.length > 0
        ? (initialData.account_acl as string[]).join("\n")
        : "",
    quotaLimitsText:
      initialData?.quota_limits && initialData.quota_limits.length > 0
        ? JSON.stringify(initialData.quota_limits, null, 2)
        : "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const accountAcl = formData.accountAclText
        .split(/\r?\n/)
        .map((value) => value.trim())
        .filter((value) => value.length > 0);

      const data: any = {
        module_path: formData.module_path,
        factory_function: formData.factory_function,
        description: formData.description || undefined,
        tools: [...formData.selectedTools],
        account_acl: accountAcl,
        quota_limits: [],
      };

      if (formData.config_schema) {
        try {
          data.config_schema = JSON.parse(formData.config_schema);
        } catch {
          toast.error("Invalid JSON in config schema");
          return;
        }
      }

      if (formData.quotaLimitsText.trim()) {
        try {
          const parsed = JSON.parse(formData.quotaLimitsText);
          if (!Array.isArray(parsed)) {
            toast.error("Quota limits must be a JSON array");
            return;
          }
          data.quota_limits = parsed;
        } catch {
          toast.error("Quota limits must be valid JSON");
          return;
        }
      }

      if (!initialData) {
        data.name = formData.name;
      }

      onSubmit(data);
    } catch (error) {
      toast.error("Failed to submit form");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!initialData && (
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            placeholder="my_agent"
          />
        </div>
      )}
      <div className="space-y-2">
        <Label htmlFor="module_path">Module Path</Label>
        <Input
          id="module_path"
          value={formData.module_path}
          onChange={(e) => setFormData({ ...formData, module_path: e.target.value })}
          required
          placeholder="backend.agents.my_agent"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="factory_function">Factory Function</Label>
        <Input
          id="factory_function"
          value={formData.factory_function}
          onChange={(e) => setFormData({ ...formData, factory_function: e.target.value })}
          required
          placeholder="create_my_agent"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="What does this agent do?"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="tools">Plugins/Tools</Label>
        <Select
          value=""
          onValueChange={(value) => {
            if (value && !formData.selectedTools.includes(value)) {
              setFormData({
                ...formData,
                selectedTools: [...formData.selectedTools, value],
              });
            }
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a plugin to add" />
          </SelectTrigger>
          <SelectContent>
            {plugins.map((plugin) => (
              <SelectItem key={plugin.id} value={plugin.id}>
                {plugin.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {formData.selectedTools.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {formData.selectedTools.map((toolId) => {
              const plugin = plugins.find((p) => p.id === toolId);
              return (
                <Badge
                  key={toolId}
                  variant="outline"
                  className="flex items-center gap-1"
                >
                  {plugin?.name || toolId}
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ...formData,
                        selectedTools: formData.selectedTools.filter((id) => id !== toolId),
                      });
                    }}
                    className="ml-1 hover:text-destructive"
                  >
                    ×
                  </button>
                </Badge>
              );
            })}
          </div>
        )}
      </div>
      <div className="space-y-2">
        <Label htmlFor="account_acl">Account Allowlist</Label>
        <Textarea
          id="account_acl"
          value={formData.accountAclText}
          onChange={(e) => setFormData({ ...formData, accountAclText: e.target.value })}
          placeholder="team-alpha\nenterprise-customer"
        />
        <p className="text-xs text-muted-foreground">
          One identifier per line. Leave blank to allow all accounts.
        </p>
      </div>
      <div className="space-y-2">
        <Label htmlFor="quota_limits">Quota Limits (JSON array)</Label>
        <Textarea
          id="quota_limits"
          value={formData.quotaLimitsText}
          onChange={(e) => setFormData({ ...formData, quotaLimitsText: e.target.value })}
          placeholder='[{"scope":"daily","limit":100}]'
          className="font-mono"
        />
        <p className="text-xs text-muted-foreground">
          Provide structured quota rules as JSON. Use an empty value for no quotas.
        </p>
      </div>
      <div className="space-y-2">
        <Label htmlFor="config_schema">Config Schema (JSON)</Label>
        <Textarea
          id="config_schema"
          value={formData.config_schema}
          onChange={(e) => setFormData({ ...formData, config_schema: e.target.value })}
          placeholder='{"type": "object", "properties": {...}}'
          className="font-mono text-sm"
          rows={6}
        />
      </div>
      <DialogFooter>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : initialData ? "Update" : "Create"}
        </Button>
      </DialogFooter>
    </form>
  );
}
