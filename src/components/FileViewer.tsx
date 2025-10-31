import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileNode } from './RepositoryBrowser';
import { 
  FileCode, 
  Info, 
  BarChart,
  FileText,
  Tag
} from 'lucide-react';

export interface FileViewerProps {
  file: FileNode;
}

export function FileViewer({ file }: FileViewerProps) {
  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getComplexityColor = (complexity?: string) => {
    switch (complexity) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg font-mono break-all">{file.path}</CardTitle>
            <CardDescription>{formatBytes(file.size_bytes)}</CardDescription>
          </div>
          {file.language && (
            <Badge variant="outline">{file.language}</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="content" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="content">
              <FileCode className="h-4 w-4 mr-2" />
              Content
            </TabsTrigger>
            <TabsTrigger value="metadata">
              <Info className="h-4 w-4 mr-2" />
              Metadata
            </TabsTrigger>
            <TabsTrigger value="chunks">
              <BarChart className="h-4 w-4 mr-2" />
              Chunks
            </TabsTrigger>
          </TabsList>

          <TabsContent value="content" className="space-y-4">
            {file.summary && (
              <div className="rounded-lg border-default bg-surface-subtle p-4">
                <div className="mb-2 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" />
                  <span className="font-semibold">Summary</span>
                </div>
                <p className="text-sm text-muted">{file.summary}</p>
              </div>
            )}

            <ScrollArea className="max-h-pane-lg w-full rounded-lg border-default">
              <pre className="p-4 text-sm text-muted">
                <code>{file.content || 'No content available'}</code>
              </pre>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="metadata" className="space-y-4">
            <div className="grid gap-4">
              {file.complexity && (
                <div>
                  <label className="text-sm font-semibold">Complexity</label>
                  <div className="mt-1">
                    <Badge variant={getComplexityColor(file.complexity)}>
                      {file.complexity}
                    </Badge>
                  </div>
                </div>
              )}

              {file.tags && file.tags.length > 0 && (
                <div>
                  <label className="mb-2 flex items-center gap-2 text-sm font-semibold">
                    <Tag className="h-4 w-4" />
                    Tags
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {file.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {file.num_chunks !== undefined && (
                <div>
                  <label className="text-sm font-semibold">Chunks</label>
                  <p className="text-sm text-muted-foreground mt-1">
                    {file.num_chunks} chunks
                  </p>
                </div>
              )}

              {file.total_tokens !== undefined && (
                <div>
                  <label className="text-sm font-semibold">Total Tokens</label>
                  <p className="text-sm text-muted-foreground mt-1">
                    {file.total_tokens.toLocaleString()} tokens
                  </p>
                </div>
              )}

              <div>
                <label className="text-sm font-semibold">File Size</label>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatBytes(file.size_bytes)}
                </p>
              </div>

              {file.language && (
                <div>
                  <label className="text-sm font-semibold">Language</label>
                  <p className="text-sm text-muted-foreground mt-1">
                    {file.language}
                  </p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="chunks" className="space-y-4">
            {file.num_chunks ? (
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-4 rounded-lg border-default bg-surface-subtle p-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-foreground">{file.num_chunks}</div>
                    <div className="text-xs text-muted">Total chunks</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">
                      {file.total_tokens?.toLocaleString() || 'N/A'}
                    </div>
                    <div className="text-xs text-muted">Total tokens</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-foreground">
                      {Math.round(file.total_tokens! / file.num_chunks) || 'N/A'}
                    </div>
                    <div className="text-xs text-muted">Avg tokens per chunk</div>
                  </div>
                </div>

                <div className="text-sm text-muted">
                  <p>
                    This file has been split into {file.num_chunks} semantic chunks for
                    processing. Each chunk maintains context and code structure.
                  </p>
                </div>
              </div>
            ) : (
              <div className="rounded-lg border-default bg-surface-subtle py-8 text-center text-muted">
                <BarChart className="mx-auto mb-2 h-12 w-12 text-muted" />
                <p>No chunk information available</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
