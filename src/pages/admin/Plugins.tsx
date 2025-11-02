import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  useGetToolRegistryApiV1AdminToolsRegistryGet,
  useCreatePluginApiV1AdminPluginsPost,
  useUpdatePluginApiV1AdminPluginsPluginIdPatch,
  useDeletePluginApiV1AdminPluginsPluginIdDelete,
} from "@/lib/api/generated";
import type { AdminPlugin } from "@/lib/types";
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
import { Plus, Edit, Trash2, Package } from "lucide-react";
import { toast } from "sonner";

export default function AdminPlugins() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingPlugin, setEditingPlugin] = useState<AdminPlugin | null>(null);
  const queryClient = useQueryClient();

  const { data: pluginsResponse, isLoading } = useGetToolRegistryApiV1AdminToolsRegistryGet();
  const plugins = pluginsResponse?.tools as AdminPlugin[] | undefined;

  const createMutation = useCreatePluginApiV1AdminPluginsPost({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["listPluginsApiV1AdminPluginsGet"] });
        setIsCreateDialogOpen(false);
        toast.success("Plugin created successfully");
      },
      onError: (error: Error) => {
        toast.error(`Failed to create plugin: ${error.message}`);
      },
    },
  });

  const updateMutation = useUpdatePluginApiV1AdminPluginsPluginIdPatch({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["listPluginsApiV1AdminPluginsGet"] });
        setIsEditDialogOpen(false);
        setEditingPlugin(null);
        toast.success("Plugin updated successfully");
      },
      onError: (error: Error) => {
        toast.error(`Failed to update plugin: ${error.message}`);
      },
    },
  });

  const deleteMutation = useDeletePluginApiV1AdminPluginsPluginIdDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["listPluginsApiV1AdminPluginsGet"] });
        toast.success("Plugin deleted successfully");
      },
      onError: (error: Error) => {
        toast.error(`Failed to delete plugin: ${error.message}`);
      },
    },
  });

  const handleEdit = (plugin: AdminPlugin) => {
    setEditingPlugin(plugin);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this plugin?")) {
      deleteMutation.mutateAsync(id);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-primary bg-clip-text text-transparent">
            Plugin Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage tools and plugins that agents can use
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Plugin
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Plugin</DialogTitle>
              <DialogDescription>
                Register a new tool/plugin that agents can use.
              </DialogDescription>
            </DialogHeader>
            <PluginForm
              onSubmit={(data) => {
                createMutation.mutateAsync({ data });
              }}
              isLoading={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-card">
        <CardHeader>
          <CardTitle>Plugins</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-center text-muted-foreground py-8">Loading plugins...</p>
          ) : !plugins || plugins.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No plugins found</p>
              <p className="text-sm mt-2">Create your first plugin to get started.</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Module</TableHead>
                    <TableHead>Function</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Metadata</TableHead>
                    <TableHead>Cost Profile</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Updated</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {plugins?.map((plugin) => (
                    <TableRow key={plugin.id}>
                      <TableCell className="font-medium">{plugin.name}</TableCell>
                      <TableCell className="font-mono text-xs">{plugin.module_path}</TableCell>
                      <TableCell className="font-mono text-xs">{plugin.function_name}</TableCell>
                      <TableCell className="max-w-xs truncate">
                        {plugin.description || "-"}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-2 text-xs">
                          {plugin.stable_slug ? (
                            <Badge variant="secondary" className="uppercase tracking-wide">
                              {plugin.stable_slug}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">No slug</span>
                          )}
                          {plugin.semantic_version && (
                            <Badge variant="outline">v{plugin.semantic_version}</Badge>
                          )}
                        </div>
                        <div className="mt-1 space-y-1 text-xs text-muted-foreground">
                          <div>Team: {plugin.owning_team || "-"}</div>
                          <div>Scope: {plugin.authorization_scope || "-"}</div>
                          <div>Approval: {plugin.approval_mode || "-"}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {plugin.cost_profile ? (
                          <pre className="max-h-32 overflow-y-auto rounded bg-muted p-2 text-xs">
                            {JSON.stringify(plugin.cost_profile, null, 2)}
                          </pre>
                        ) : (
                          <span className="text-muted-foreground text-xs">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(plugin.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {new Date(plugin.updated_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(plugin)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-danger"
                            onClick={() => handleDelete(plugin.id)}
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
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Plugin</DialogTitle>
            <DialogDescription>
              Update plugin configuration.
            </DialogDescription>
          </DialogHeader>
          {editingPlugin && (
            <PluginForm
              initialData={editingPlugin}
              onSubmit={(data) => {
                updateMutation.mutateAsync({ pluginId: editingPlugin.id, data });
              }}
              isLoading={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

type PluginFormState = {
  name: string;
  module_path: string;
  function_name: string;
  description: string;
  input_schema: string;
  output_schema: string;
  stable_slug: string;
  semantic_version: string;
  owning_team: string;
  authorization_scope: string;
  approval_mode: string;
  cost_profile: string;
};

type PluginFormSubmit = Partial<PluginMutationPayload> & { name?: string };

function PluginForm({
  initialData,
  onSubmit,
  isLoading,
}: {
  initialData?: AdminPlugin;
  onSubmit: (data: PluginFormSubmit) => void;
  isLoading: boolean;
}) {
  const [formData, setFormData] = useState<PluginFormState>({
    name: initialData?.name || "",
    module_path: initialData?.module_path || "",
    function_name: initialData?.function_name || "",
    description: initialData?.description || "",
    input_schema: initialData?.input_schema
      ? JSON.stringify(initialData.input_schema, null, 2)
      : "",
    output_schema: initialData?.output_schema
      ? JSON.stringify(initialData.output_schema, null, 2)
      : "",
    stable_slug: initialData?.stable_slug || "",
    semantic_version: initialData?.semantic_version || "",
    owning_team: initialData?.owning_team || "",
    authorization_scope: initialData?.authorization_scope || "",
    approval_mode: initialData?.approval_mode || "",
    cost_profile: initialData?.cost_profile
      ? JSON.stringify(initialData.cost_profile, null, 2)
      : "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const modulePath = formData.module_path.trim();
      const functionName = formData.function_name.trim();
      const description = formData.description.trim();

      if (!modulePath) {
        toast.error("Module path is required");
        return;
      }

      if (!functionName) {
        toast.error("Function name is required");
        return;
      }

      const data: PluginFormSubmit = {
        module_path: modulePath,
        function_name: functionName,
        description: description ? description : undefined,
      };

      if (formData.input_schema) {
        try {
          data.input_schema = JSON.parse(formData.input_schema) as Record<string, unknown>;
        } catch {
          toast.error("Invalid JSON in input schema");
          return;
        }
      }

      if (formData.output_schema) {
        try {
          data.output_schema = JSON.parse(formData.output_schema) as Record<string, unknown>;
        } catch {
          toast.error("Invalid JSON in output schema");
          return;
        }
      }

      if (formData.stable_slug.trim()) {
        data.stable_slug = formData.stable_slug.trim();
      }

      if (formData.semantic_version.trim()) {
        data.semantic_version = formData.semantic_version.trim();
      }

      if (formData.owning_team.trim()) {
        data.owning_team = formData.owning_team.trim();
      }

      if (formData.authorization_scope.trim()) {
        data.authorization_scope = formData.authorization_scope.trim();
      }

      if (formData.approval_mode.trim()) {
        data.approval_mode = formData.approval_mode.trim();
      }

      if (formData.cost_profile) {
        try {
          data.cost_profile = JSON.parse(formData.cost_profile) as Record<string, unknown>;
        } catch {
          toast.error("Invalid JSON in cost profile");
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
            placeholder="my_plugin"
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
          placeholder="backend.tools.my_tool"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="function_name">Function Name</Label>
        <Input
          id="function_name"
          value={formData.function_name}
          onChange={(e) => setFormData({ ...formData, function_name: e.target.value })}
          required
          placeholder="my_function"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="What does this plugin do?"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="stable_slug">Stable Slug</Label>
        <Input
          id="stable_slug"
          value={formData.stable_slug}
          onChange={(e) => setFormData({ ...formData, stable_slug: e.target.value })}
          placeholder="my-plugin"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="semantic_version">Semantic Version</Label>
        <Input
          id="semantic_version"
          value={formData.semantic_version}
          onChange={(e) => setFormData({ ...formData, semantic_version: e.target.value })}
          placeholder="1.0.0"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="owning_team">Owning Team</Label>
        <Input
          id="owning_team"
          value={formData.owning_team}
          onChange={(e) => setFormData({ ...formData, owning_team: e.target.value })}
          placeholder="core-platform"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="authorization_scope">Authorization Scope</Label>
        <Input
          id="authorization_scope"
          value={formData.authorization_scope}
          onChange={(e) => setFormData({ ...formData, authorization_scope: e.target.value })}
          placeholder="internal"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="approval_mode">Approval Mode</Label>
        <Input
          id="approval_mode"
          value={formData.approval_mode}
          onChange={(e) => setFormData({ ...formData, approval_mode: e.target.value })}
          placeholder="auto"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="cost_profile">Cost Profile (JSON)</Label>
        <Textarea
          id="cost_profile"
          value={formData.cost_profile}
          onChange={(e) => setFormData({ ...formData, cost_profile: e.target.value })}
          placeholder='{"unit": "call", "estimated_cost_usd": 0.0}'
          className="font-mono text-sm"
          rows={4}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="input_schema">Input Schema (JSON)</Label>
        <Textarea
          id="input_schema"
          value={formData.input_schema}
          onChange={(e) => setFormData({ ...formData, input_schema: e.target.value })}
          placeholder='{"type": "object", "properties": {...}}'
          className="font-mono text-sm"
          rows={6}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="output_schema">Output Schema (JSON)</Label>
        <Textarea
          id="output_schema"
          value={formData.output_schema}
          onChange={(e) => setFormData({ ...formData, output_schema: e.target.value })}
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
