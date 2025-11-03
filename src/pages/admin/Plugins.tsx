import { useGetCodeRegistryPluginsApiV1AdminToolsCodeRegistryGet } from "@/lib/api/generated";
import type { ToolRegistryItem } from "@/lib/api/generated/codebaseAudiobookAPI.schemas";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Package, Info } from "lucide-react";

export default function AdminPlugins() {
  const { data: pluginsResponse, isLoading } = useGetCodeRegistryPluginsApiV1AdminToolsCodeRegistryGet();
  const plugins = pluginsResponse?.tools as ToolRegistryItem[] | undefined;

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-primary bg-clip-text text-transparent">
          Plugin Registry
        </h1>
        <p className="text-muted-foreground mt-1">
          View code-defined plugins that agents can use. Plugins are defined in source code and cannot be modified via UI.
        </p>
      </div>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Read-Only Registry</AlertTitle>
        <AlertDescription>
          Plugins are defined in code (backend/models/tool_registry.py) and loaded at application startup.
          To add or modify plugins, edit the source code and restart the application.
        </AlertDescription>
      </Alert>

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
              <p className="text-sm mt-2">Plugins are defined in backend/models/tool_registry.py</p>
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
                    <TableHead>Source</TableHead>
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
                        <Badge variant="secondary" className="font-mono text-xs">
                          Code
                        </Badge>
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
