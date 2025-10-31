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
  Tag,
  Diff,
  Braces,
  Eye
} from 'lucide-react';

export interface AdminFileViewerProps {
  file: FileNode;
  rawData: any; // Full response data from parse endpoint
}

export function AdminFileViewer({ file, rawData }: AdminFileViewerProps) {
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

  const hasRawContent = rawData?.raw_content && rawData.raw_content !== rawData.content;
  const hasChunks = rawData?.chunks && rawData.chunks.length > 0;

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1 min-w-0">
            <CardTitle className="text-lg font-mono break-all">{file.path}</CardTitle>
            <CardDescription>{formatBytes(file.size_bytes)}</CardDescription>
          </div>
          {file.language && (
            <Badge variant="outline">{file.language}</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="cleaned" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="cleaned">
              <Eye className="h-4 w-4 mr-2" />
              Cleaned
            </TabsTrigger>
            {hasRawContent && (
              <TabsTrigger value="raw">
                <FileCode className="h-4 w-4 mr-2" />
                Raw
              </TabsTrigger>
            )}
            {hasRawContent && (
              <TabsTrigger value="diff">
                <Diff className="h-4 w-4 mr-2" />
                Diff
              </TabsTrigger>
            )}
            <TabsTrigger value="metadata">
              <Info className="h-4 w-4 mr-2" />
              Metadata
            </TabsTrigger>
            <TabsTrigger value="structure">
              <Braces className="h-4 w-4 mr-2" />
              Structure
            </TabsTrigger>
          </TabsList>

          <TabsContent value="cleaned" className="space-y-4">
            {file.summary && (
              <div className="rounded-lg border-default bg-surface-subtle p-4">
                <div className="mb-2 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" />
                  <span className="font-semibold">AI-Generated Summary</span>
                </div>
                <p className="text-sm text-muted">{file.summary}</p>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold">Cleaned Content</span>
                <Badge variant="secondary">
                  {file.content?.split('\n').length || 0} lines
                </Badge>
              </div>
              <ScrollArea className="max-h-pane-lg w-full rounded-lg border-default">
                <pre className="p-4 text-sm text-muted">
                  <code>{file.content || 'No content available'}</code>
                </pre>
              </ScrollArea>
            </div>
          </TabsContent>

          {hasRawContent && (
            <TabsContent value="raw" className="space-y-4">
              <div className="rounded-lg border-warning/30 bg-warning/10 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <Info className="h-4 w-4 text-warning" />
                  <span className="font-semibold text-warning">Original File</span>
                </div>
                <p className="text-sm text-warning">
                  This is the original content before chonkie processing. Compare with cleaned version to see transformations.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold">Raw Content</span>
                  <Badge variant="secondary">
                    {rawData.raw_content?.split('\n').length || 0} lines
                  </Badge>
                </div>
                <ScrollArea className="max-h-pane-lg w-full rounded-lg border-default">
                  <pre className="p-4 text-sm text-muted">
                    <code>{rawData.raw_content}</code>
                  </pre>
                </ScrollArea>
              </div>
            </TabsContent>
          )}

          {hasRawContent && (
            <TabsContent value="diff" className="space-y-4">
              <div className="rounded-lg border-primary/30 bg-primary/10 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <Diff className="h-4 w-4 text-primary" />
                  <span className="font-semibold text-primary">Content Transformations</span>
                </div>
                <p className="text-sm text-primary">
                  Shows what chonkie changed: removed comments, normalized whitespace, extracted code blocks, etc.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <span className="text-sm font-semibold text-danger">Original Size</span>
                  <div className="text-2xl font-bold text-danger">
                    {formatBytes(rawData.raw_content?.length || 0)}
                  </div>
                </div>
                <div className="space-y-2">
                  <span className="text-sm font-semibold text-success">Cleaned Size</span>
                  <div className="text-2xl font-bold text-success">
                    {formatBytes(file.content?.length || 0)}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-sm font-semibold">Changes Summary</span>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Lines removed:</span>
                    <Badge variant="danger">
                      {Math.max(0, (rawData.raw_content?.split('\n').length || 0) - (file.content?.split('\n').length || 0))}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Size reduction:</span>
                    <Badge variant="secondary">
                      {(((rawData.raw_content?.length || 0) - (file.content?.length || 0)) / (rawData.raw_content?.length || 1) * 100).toFixed(1)}%
                    </Badge>
                  </div>
                </div>
              </div>

              <ScrollArea className="max-h-pane-md w-full rounded-lg border-default">
                <div className="space-y-0.5 p-4 text-sm font-mono text-muted">
                  {(() => {
                    const rawLines = rawData.raw_content?.split('\n') || [];
                    const cleanedLines = file.content?.split('\n') || [];
                    const maxLines = Math.max(rawLines.length, cleanedLines.length);
                    
                    return Array.from({ length: Math.min(maxLines, 100) }).map((_, i) => {
                      const rawLine = rawLines[i] || '';
                      const cleanedLine = cleanedLines[i] || '';
                      
                      if (rawLine === cleanedLine) {
                        return (
                          <div key={i} className="text-muted-foreground">
                            {i + 1}: {rawLine || '(empty)'}
                          </div>
                        );
                      } else if (!cleanedLine) {
                        return (
                          <div key={i} className="rounded-sm bg-danger/10 px-2 py-1 text-danger">
                            -{i + 1}: {rawLine}
                          </div>
                        );
                      } else if (!rawLine) {
                        return (
                          <div key={i} className="rounded-sm bg-success/10 px-2 py-1 text-success">
                            +{i + 1}: {cleanedLine}
                          </div>
                        );
                      } else {
                        return (
                          <div key={i} className="space-y-1 rounded-sm bg-warning/10 px-2 py-1">
                            <div className="text-danger">-{i + 1}: {rawLine}</div>
                            <div className="text-success">+{i + 1}: {cleanedLine}</div>
                          </div>
                        );
                      }
                    });
                  })()}
                  {(() => {
                    const maxLines = Math.max(
                      rawData.raw_content?.split('\n').length || 0,
                      file.content?.split('\n').length || 0
                    );
                    return maxLines > 100 && (
                      <div className="text-muted-foreground italic">
                        ... {maxLines - 100} more lines
                      </div>
                    );
                  })()}
                </div>
              </ScrollArea>
            </TabsContent>
          )}

          <TabsContent value="metadata" className="space-y-4">
            <div className="grid gap-4">
              {file.complexity && (
                <div>
                  <label className="text-sm font-semibold">Complexity Analysis</label>
                  <div className="mt-1">
                    <Badge variant={getComplexityColor(file.complexity)} className="text-lg">
                      {file.complexity}
                    </Badge>
                  </div>
                </div>
              )}

              {file.tags && file.tags.length > 0 && (
                <div>
                  <label className="text-sm font-semibold flex items-center gap-2 mb-2">
                    <Tag className="h-4 w-4" />
                    Detected Tags ({file.tags.length})
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {file.tags.map((tag, index) => {
                      const [category, value] = tag.split(':');
                      return (
                        <Badge key={index} variant="secondary">
                          {value ? (
                            <>
                              <span className="opacity-60">{category}:</span>
                              {value}
                            </>
                          ) : (
                            tag
                          )}
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg">
                <div>
                  <label className="text-sm font-semibold">File Size</label>
                  <p className="text-2xl font-bold mt-1">
                    {formatBytes(file.size_bytes)}
                  </p>
                </div>

                {file.num_chunks !== undefined && (
                  <div>
                    <label className="text-sm font-semibold">Chunks Created</label>
                    <p className="text-2xl font-bold mt-1">
                      {file.num_chunks}
                    </p>
                  </div>
                )}

                {file.total_tokens !== undefined && (
                  <div>
                    <label className="text-sm font-semibold">Total Tokens</label>
                    <p className="text-2xl font-bold mt-1">
                      {file.total_tokens.toLocaleString()}
                    </p>
                  </div>
                )}

                {file.num_chunks && file.total_tokens && (
                  <div>
                    <label className="text-sm font-semibold">Avg Tokens/Chunk</label>
                    <p className="text-2xl font-bold mt-1">
                      {Math.round(file.total_tokens / file.num_chunks)}
                    </p>
                  </div>
                )}
              </div>

              {file.language && (
                <div>
                  <label className="text-sm font-semibold">Detected Language</label>
                  <p className="text-sm text-muted-foreground mt-1">
                    {file.language}
                  </p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="structure" className="space-y-4">
            <Card className="bg-muted/50">
              <CardHeader>
                <CardTitle className="text-sm">Raw JSON Structure</CardTitle>
                <CardDescription>Complete parse response for this file</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[450px] w-full">
                  <pre className="text-xs">
                    <code>{JSON.stringify(rawData, null, 2)}</code>
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
