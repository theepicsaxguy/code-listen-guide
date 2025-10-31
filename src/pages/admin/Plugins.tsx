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
import { Plus, Edit, Trash2, Package } from "lucide-react";
import { toast } from "sonner";

export default function AdminPlugins() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingPlugin, setEditingPlugin] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data: plugins, isLoading } = useQuery({
    queryKey: ["admin-plugins"],
    queryFn: () => apiClient.listPlugins(),
  });

  const createMutation = useMutation({
    mutationFn: (plugin: {
      name: string;
      module_path: string;
      function_name: string;
      description?: string;
      input_schema?: Record<string, any>;
      output_schema?: Record<string, any>;
    }) => apiClient.createPlugin(plugin),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-plugins"] });
      setIsCreateDialogOpen(false);
      toast.success("Plugin created successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to create plugin: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: any }) =>
      apiClient.updatePlugin(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-plugins"] });
      setIsEditDialogOpen(false);
      setEditingPlugin(null);
      toast.success("Plugin updated successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to update plugin: ${error.message}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.deletePlugin(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-plugins"] });
      toast.success("Plugin deleted successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete plugin: ${error.message}`);
    },
  });

  const handleEdit = (plugin: any) => {
    setEditingPlugin(plugin);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this plugin?")) {
      deleteMutation.mutate(id);
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
                createMutation.mutate(data);
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
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {plugins.map((plugin: any) => (
                    <TableRow key={plugin.id}>
                      <TableCell className="font-medium">{plugin.name}</TableCell>
                      <TableCell className="font-mono text-xs">{plugin.module_path}</TableCell>
                      <TableCell className="font-mono text-xs">{plugin.function_name}</TableCell>
                      <TableCell className="max-w-xs truncate">
                        {plugin.description || "-"}
                      </TableCell>
                      <TableCell>
                        {new Date(plugin.created_at).toLocaleDateString()}
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
                updateMutation.mutate({ id: editingPlugin.id, updates: data });
              }}
              isLoading={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function PluginForm({
  initialData,
  onSubmit,
  isLoading,
}: {
  initialData?: any;
  onSubmit: (data: any) => void;
  isLoading: boolean;
}) {
  const [formData, setFormData] = useState({
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
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data: any = {
        module_path: formData.module_path,
        function_name: formData.function_name,
        description: formData.description || undefined,
      };

      if (formData.input_schema) {
        try {
          data.input_schema = JSON.parse(formData.input_schema);
        } catch {
          toast.error("Invalid JSON in input schema");
          return;
        }
      }

      if (formData.output_schema) {
        try {
          data.output_schema = JSON.parse(formData.output_schema);
        } catch {
          toast.error("Invalid JSON in output schema");
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
