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
  rawData: {
    raw_content?: string;
    content?: string;
    chunks?: unknown[];
    [key: string]: unknown;
  }; // Full response data from parse endpoint
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
              <div className="rounded-card bg-surface-secondary shadow-sm p-4">
                <div className="mb-2 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" />
                  <span className="font-semibold">AI-Generated Summary</span>
                </div>
                <p className="text-body-sm text-muted-foreground">{file.summary}</p>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-body-sm font-semibold">Cleaned Content</span>
                <Badge variant="secondary">
                  {file.content?.split('\n').length || 0} lines
                </Badge>
              </div>
              <ScrollArea className="max-h-pane-lg w-full rounded-card bg-surface-secondary shadow-sm">
                <pre className="p-4 text-body-sm text-muted-foreground">
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
                <ScrollArea className="max-h-pane-lg w-full rounded-card bg-surface-secondary shadow-sm">
                  <pre className="p-4 text-body-sm text-muted-foreground">
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

              <ScrollArea className="max-h-pane-md w-full rounded-card bg-surface-secondary shadow-sm">
                <div className="space-y-0.5 p-4 text-body-sm font-mono text-muted-foreground">
                  {(() => {
                    const rawLines = rawData.raw_content?.split('\n') || [];
                    const cleanedLines = file.content?.split('\n') || [];

                    // Check if the contents are actually different
                    if (rawData.raw_content === file.content) {
                      return (
                        <div className="text-center py-8 text-muted-foreground">
                          <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p>No changes detected - raw and cleaned content are identical</p>
                        </div>
                      );
                    }

                    const maxLines = Math.max(rawLines.length, cleanedLines.length);
                    const diffLines = [];
                    let lineNum = 0;

                    for (let i = 0; i < Math.min(maxLines, 100); i++) {
                      const rawLine = rawLines[i];
                      const cleanedLine = cleanedLines[i];

                      if (rawLine === undefined && cleanedLine === undefined) continue;

                      lineNum++;

                      if (rawLine === cleanedLine) {
                        diffLines.push(
                          <div key={i} className="text-muted-foreground">
                            {lineNum}: {rawLine || '(empty)'}
                          </div>
                        );
                      } else if (cleanedLine === undefined) {
                        diffLines.push(
                          <div key={i} className="rounded-sm bg-danger/10 px-2 py-1 text-danger">
                            -{lineNum}: {rawLine}
                          </div>
                        );
                      } else if (rawLine === undefined) {
                        diffLines.push(
                          <div key={i} className="rounded-sm bg-success/10 px-2 py-1 text-success">
                            +{lineNum}: {cleanedLine}
                          </div>
                        );
                      } else {
                        diffLines.push(
                          <div key={i} className="space-y-1 rounded-sm bg-warning/10 px-2 py-1">
                            <div className="text-danger">-{lineNum}: {rawLine}</div>
                            <div className="text-success">+{lineNum}: {cleanedLine}</div>
                          </div>
                        );
                      }
                    }

                    return diffLines;
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

              {/* Basic File Metrics */}
              <div className="space-y-2">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <BarChart className="h-4 w-4" />
                  File Metrics
                </h3>
                <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg">
                  <div>
                    <label className="text-sm font-semibold">File Size</label>
                    <p className="text-2xl font-bold mt-1">
                      {file.file_size_mb !== undefined && file.file_size_mb !== null
                        ? `${file.file_size_mb.toFixed(2)} MB`
                        : formatBytes(file.size_bytes)}
                    </p>
                  </div>

                  {file.language && (
                    <div>
                      <label className="text-sm font-semibold">Detected Language</label>
                      <p className="text-lg font-bold mt-1">
                        {file.language}
                      </p>
                    </div>
                  )}

                  {file.num_chunks !== undefined && file.num_chunks !== null && (
                    <div>
                      <label className="text-sm font-semibold">Chunks Created</label>
                      <p className="text-2xl font-bold mt-1">
                        {file.num_chunks}
                      </p>
                    </div>
                  )}

                  {file.total_tokens !== undefined && file.total_tokens !== null && (
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
              </div>

              {/* Code Structure */}
              {(file.function_count !== undefined || file.class_count !== undefined ||
                file.import_count !== undefined || file.export_count !== undefined) && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Braces className="h-4 w-4" />
                    Code Structure
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 border rounded-lg">
                    {file.function_count !== undefined && file.function_count !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Functions</label>
                        <p className="text-xl font-bold mt-1">{file.function_count}</p>
                      </div>
                    )}

                    {file.class_count !== undefined && file.class_count !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Classes</label>
                        <p className="text-xl font-bold mt-1">{file.class_count}</p>
                      </div>
                    )}

                    {file.import_count !== undefined && file.import_count !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Imports</label>
                        <p className="text-xl font-bold mt-1">{file.import_count}</p>
                      </div>
                    )}

                    {file.export_count !== undefined && file.export_count !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Exports</label>
                        <p className="text-xl font-bold mt-1">{file.export_count}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Line Metrics */}
              {(file.total_lines !== undefined || file.code_lines !== undefined ||
                file.comment_lines !== undefined || file.blank_lines !== undefined) && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">Line Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 border rounded-lg">
                    {file.total_lines !== undefined && file.total_lines !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Total Lines</label>
                        <p className="text-xl font-bold mt-1">{file.total_lines.toLocaleString()}</p>
                      </div>
                    )}

                    {file.code_lines !== undefined && file.code_lines !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Code Lines</label>
                        <p className="text-xl font-bold mt-1">{file.code_lines.toLocaleString()}</p>
                      </div>
                    )}

                    {file.comment_lines !== undefined && file.comment_lines !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Comment Lines</label>
                        <p className="text-xl font-bold mt-1">{file.comment_lines.toLocaleString()}</p>
                      </div>
                    )}

                    {file.blank_lines !== undefined && file.blank_lines !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Blank Lines</label>
                        <p className="text-xl font-bold mt-1">{file.blank_lines.toLocaleString()}</p>
                      </div>
                    )}

                    {file.comment_ratio !== undefined && file.comment_ratio !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Comment Ratio</label>
                        <p className="text-xl font-bold mt-1">{(file.comment_ratio * 100).toFixed(1)}%</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Complexity Metrics */}
              {(file.cyclomatic_complexity !== undefined || file.cognitive_complexity !== undefined ||
                file.maintainability_index !== undefined) && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">Complexity Metrics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 border rounded-lg">
                    {file.cyclomatic_complexity !== undefined && file.cyclomatic_complexity !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Cyclomatic</label>
                        <p className="text-xl font-bold mt-1">{file.cyclomatic_complexity}</p>
                      </div>
                    )}

                    {file.cognitive_complexity !== undefined && file.cognitive_complexity !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Cognitive</label>
                        <p className="text-xl font-bold mt-1">{file.cognitive_complexity}</p>
                      </div>
                    )}

                    {file.maintainability_index !== undefined && file.maintainability_index !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Maintainability (0-171)</label>
                        <p className="text-xl font-bold mt-1">{file.maintainability_index.toFixed(1)}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Cleaning Statistics */}
              {(file.original_lines !== undefined || file.cleaned_lines !== undefined ||
                file.lines_removed !== undefined) && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">Cleaning Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 border rounded-lg">
                    {file.original_lines !== undefined && file.original_lines !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Original Lines</label>
                        <p className="text-xl font-bold mt-1">{file.original_lines.toLocaleString()}</p>
                      </div>
                    )}

                    {file.cleaned_lines !== undefined && file.cleaned_lines !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Cleaned Lines</label>
                        <p className="text-xl font-bold mt-1">{file.cleaned_lines.toLocaleString()}</p>
                      </div>
                    )}

                    {file.lines_removed !== undefined && file.lines_removed !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Lines Removed</label>
                        <p className="text-xl font-bold mt-1 text-danger">{file.lines_removed.toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Additional Metadata */}
              {(file.framework !== undefined || file.patterns !== undefined ||
                file.has_tests !== undefined || file.entry_point !== undefined) && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">Additional Information</h3>
                  <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg">
                    {file.framework !== undefined && file.framework !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Framework</label>
                        <Badge variant="outline" className="mt-1">{file.framework}</Badge>
                      </div>
                    )}

                    {file.patterns !== undefined && file.patterns !== null && file.patterns.length > 0 && (
                      <div>
                        <label className="text-sm text-muted-foreground">Patterns</label>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {file.patterns.map((pattern: string, i: number) => (
                            <Badge key={i} variant="secondary" className="text-xs">{pattern}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {file.has_tests !== undefined && file.has_tests !== null && (
                      <div>
                        <label className="text-sm text-muted-foreground">Has Tests</label>
                        <Badge variant={file.has_tests ? "success" : "secondary"} className="mt-1">
                          {file.has_tests ? "Yes" : "No"}
                        </Badge>
                      </div>
                    )}

                    {file.entry_point !== undefined && file.entry_point !== null && file.entry_point && (
                      <div>
                        <label className="text-sm text-muted-foreground">Entry Point</label>
                        <Badge variant="primary" className="mt-1">Yes</Badge>
                      </div>
                    )}
                  </div>
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
