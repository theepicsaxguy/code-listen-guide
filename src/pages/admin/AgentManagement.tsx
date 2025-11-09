import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListAgents,
  useCreateAgent,
  useUpdateAgent,
  useDeleteAgent,
  useListPlugins,
} from "@/lib/api/generated";
import type { AgentOut, PluginOut } from "@/lib/api/generated/codebaseAudiobookAPI.schemas";
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
import { Plus, Edit, Trash2, Bot, Package, ChevronUp, ChevronDown, X } from "lucide-react";
import { toast } from "sonner";

export default function AgentManagement() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AgentOut | null>(null);
  const queryClient = useQueryClient();

  const { data: agents, isLoading } = useListAgents();

  const { data: plugins } = useListPlugins();

  const createMutation = useCreateAgent({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["listAgents"] });
        setIsCreateDialogOpen(false);
        toast.success("Agent created successfully");
      },
      onError: (error: Error) => {
        toast.error(`Failed to create agent: ${error.message}`);
      },
    },
  });

  const updateMutation = useUpdateAgent({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["listAgents"] });
        setIsEditDialogOpen(false);
        setEditingAgent(null);
        toast.success("Agent updated successfully");
      },
      onError: (error: Error) => {
        toast.error(`Failed to update agent: ${error.message}`);
      },
    },
  });

  const deleteMutation = useDeleteAgent({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["listAgents"] });
        toast.success("Agent deleted successfully");
      },
      onError: (error: Error) => {
        toast.error(`Failed to delete agent: ${error.message}`);
      },
    },
  });

  const handleEdit = (agent: AgentOut) => {
    setEditingAgent(agent);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (id: string) => {
      if (confirm("Are you sure you want to delete this agent?")) {
        deleteMutation.mutate({ agentId: id });
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
                createMutation.mutate({ data });
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
                    <TableHead>Description</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agents?.map((agent) => (
                    <TableRow key={agent.id}>
                      <TableCell className="font-medium">{agent.name}</TableCell>
                      <TableCell className="font-mono text-xs">{agent.module_path}</TableCell>
                      <TableCell className="font-mono text-xs">{agent.factory_function}</TableCell>
                      <TableCell>
                        {agent.tools && agent.tools.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {agent.tools.map((tool, idx) => {
                              const toolId = typeof tool === 'object' && tool !== null && 'id' in tool 
                                ? String((tool as any).id) 
                                : String(idx);
                              const toolName = typeof tool === 'object' && tool !== null && 'name' in tool
                                ? String((tool as any).name)
                                : typeof tool === 'string' 
                                  ? tool 
                                  : 'Unknown';
                              return (
                                <Badge key={toolId} variant="outline" className="text-xs">
                                  {toolName}
                                </Badge>
                              );
                            })}
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
                updateMutation.mutate({ agentId: editingAgent.id, data });
              }}
              isLoading={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

type AgentFormState = {
  name: string;
  module_path: string;
  factory_function: string;
  description: string;
  config_schema: string;
  selectedTools: string[];
};

function AgentForm({
  plugins,
  initialData,
  onSubmit,
  isLoading,
}: {
  plugins: PluginOut[];
  initialData?: AgentOut;
  onSubmit: (data: any) => void;
  isLoading: boolean;
}) {
  // Extract tool IDs from initialData
  const getToolIds = (tools: AgentOut['tools']): string[] => {
    if (!tools || !Array.isArray(tools)) return [];
    return tools
      .map((tool) => {
        if (typeof tool === 'object' && tool !== null && 'id' in tool) {
          return String((tool as any).id);
        }
        if (typeof tool === 'string') {
          // If it's a string, try to find plugin by name or slug
          const plugin = plugins.find(p => p.name === tool || p.stable_slug === tool);
          return plugin?.id || tool;
        }
        return null;
      })
      .filter((id): id is string => Boolean(id));
  };

  const [formData, setFormData] = useState<AgentFormState>({
    name: initialData?.name || "",
    module_path: initialData?.module_path || "",
    factory_function: initialData?.factory_function || "",
    description: initialData?.description || "",
    config_schema: initialData?.config_schema
      ? JSON.stringify(initialData.config_schema, null, 2)
      : "",
    selectedTools: initialData ? getToolIds(initialData.tools) : [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const modulePath = formData.module_path.trim();
      const factoryFunction = formData.factory_function.trim();
      const description = formData.description.trim();

      if (!modulePath) {
        toast.error("Module path is required");
        return;
      }

      if (!factoryFunction) {
        toast.error("Factory function is required");
        return;
      }

      const data: any = {
        module_path: modulePath,
        factory_function: factoryFunction,
        description: description ? description : undefined,
        tools: formData.selectedTools.length > 0 ? formData.selectedTools : undefined,
      };

      if (formData.config_schema) {
        try {
          data.config_schema = JSON.parse(formData.config_schema) as Record<string, unknown>;
        } catch {
          toast.error("Invalid JSON in config schema");
          return;
        }
      }

      if (!initialData) {
        const trimmedName = formData.name.trim();
        if (!trimmedName) {
          toast.error("Name is required");
          return;
        }
        data.name = trimmedName;
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
              setFormData((prev) => ({
                ...prev,
                selectedTools: [...prev.selectedTools, value],
              }));
            }
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a plugin to add" />
          </SelectTrigger>
          <SelectContent>
            {plugins
              ?.filter((plugin) => Boolean(plugin.id))
              .map((plugin) => (
                <SelectItem key={plugin.id} value={plugin.id}>
                  {plugin.name}
                </SelectItem>
              ))}
          </SelectContent>
        </Select>
        {formData.selectedTools.length > 0 && (
          <div className="flex flex-col gap-2 mt-2">
            {formData.selectedTools.map((toolId, index) => {
              const plugin = plugins.find((p) => p.id === toolId);
              return (
                <div key={toolId} className="flex items-center gap-2">
                  <Badge variant="outline" className="flex-1 justify-start text-xs">
                    {plugin?.name || toolId}
                  </Badge>
                  <div className="flex gap-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      disabled={index === 0}
                      onClick={() => {
                        if (index === 0) {
                          return;
                        }
                        setFormData((prev) => {
                          const next = [...prev.selectedTools];
                          [next[index - 1], next[index]] = [next[index], next[index - 1]];
                          return { ...prev, selectedTools: next };
                        });
                      }}
                      aria-label="Move up"
                    >
                      <ChevronUp className="h-4 w-4" />
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      disabled={index === formData.selectedTools.length - 1}
                      onClick={() => {
                        if (index === formData.selectedTools.length - 1) {
                          return;
                        }
                        setFormData((prev) => {
                          const next = [...prev.selectedTools];
                          [next[index + 1], next[index]] = [next[index], next[index + 1]];
                          return { ...prev, selectedTools: next };
                        });
                      }}
                      aria-label="Move down"
                    >
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setFormData((prev) => ({
                          ...prev,
                          selectedTools: prev.selectedTools.filter((id) => id !== toolId),
                        }));
                      }}
                      aria-label="Remove"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
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
