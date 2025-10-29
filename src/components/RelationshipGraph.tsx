import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Network, File, Package, GitBranch } from 'lucide-react';

export interface RelationshipGraphProps {
  modules: Record<string, any>;
  summary: any;
}

export function RelationshipGraph({ modules, summary }: RelationshipGraphProps) {
  // Extract relationship data from tags and patterns
  const relationships: { from: string; to: string; type: string }[] = [];
  const entryPoints: string[] = summary.entry_points || [];
  
  // Group files by directory
  const filesByDirectory: Record<string, string[]> = {};
  Object.keys(modules).forEach(path => {
    const dir = path.includes('/') ? path.substring(0, path.lastIndexOf('/')) : '/';
    if (!filesByDirectory[dir]) {
      filesByDirectory[dir] = [];
    }
    filesByDirectory[dir].push(path);
  });

  // Group files by framework
  const filesByFramework: Record<string, string[]> = {};
  Object.entries(modules).forEach(([path, file]: [string, any]) => {
    file.metadata?.tags?.forEach((tag: string) => {
      if (tag.startsWith('framework:')) {
        const framework = tag.split(':')[1];
        if (!filesByFramework[framework]) {
          filesByFramework[framework] = [];
        }
        filesByFramework[framework].push(path);
      }
    });
  });

  // Group files by pattern
  const filesByPattern: Record<string, string[]> = {};
  Object.entries(modules).forEach(([path, file]: [string, any]) => {
    file.metadata?.tags?.forEach((tag: string) => {
      if (tag.startsWith('pattern:')) {
        const pattern = tag.split(':')[1];
        if (!filesByPattern[pattern]) {
          filesByPattern[pattern] = [];
        }
        filesByPattern[pattern].push(path);
      }
    });
  });

  return (
    <div className="space-y-6">
      {/* Overview */}
      <div className="grid lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Entry Points</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{entryPoints.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Starting files</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Directories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{Object.keys(filesByDirectory).length}</div>
            <p className="text-xs text-muted-foreground mt-1">File groups</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Frameworks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{Object.keys(filesByFramework).length}</div>
            <p className="text-xs text-muted-foreground mt-1">Detected</p>
          </CardContent>
        </Card>
      </div>

      {/* Entry Points */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Entry Points
          </CardTitle>
          <CardDescription>
            Files identified as application entry points
          </CardDescription>
        </CardHeader>
        <CardContent>
          {entryPoints.length > 0 ? (
            <div className="space-y-2">
              {entryPoints.map((path, index) => (
                <div key={index} className="flex items-center gap-2 p-2 border rounded">
                  <File className="h-4 w-4 text-primary" />
                  <code className="text-sm">{path}</code>
                  {modules[path]?.metadata?.tags && (
                    <div className="ml-auto flex gap-1">
                      {modules[path].metadata.tags
                        .filter((t: string) => t !== 'entry_point' && t !== 'purpose:entry_point')
                        .slice(0, 3)
                        .map((tag: string, i: number) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            {tag.split(':')[1] || tag}
                          </Badge>
                        ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-8">No entry points detected</p>
          )}
        </CardContent>
      </Card>

      {/* Framework Grouping */}
      {Object.keys(filesByFramework).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Files by Framework
            </CardTitle>
            <CardDescription>
              Code organized by detected framework usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              <div className="space-y-4">
                {Object.entries(filesByFramework).map(([framework, files]) => (
                  <div key={framework} className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge className="text-sm">{framework}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {files.length} files
                      </span>
                    </div>
                    <div className="ml-4 space-y-1">
                      {files.slice(0, 10).map((path, index) => (
                        <div key={index} className="text-sm font-mono text-muted-foreground">
                          • {path}
                        </div>
                      ))}
                      {files.length > 10 && (
                        <div className="text-sm text-muted-foreground italic">
                          ... and {files.length - 10} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Pattern Grouping */}
      {Object.keys(filesByPattern).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Network className="h-5 w-5" />
              Files by Pattern
            </CardTitle>
            <CardDescription>
              Code organized by detected design patterns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              <div className="space-y-4">
                {Object.entries(filesByPattern).map(([pattern, files]) => (
                  <div key={pattern} className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-sm">{pattern}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {files.length} files
                      </span>
                    </div>
                    <div className="ml-4 space-y-1">
                      {files.slice(0, 10).map((path, index) => (
                        <div key={index} className="text-sm font-mono text-muted-foreground">
                          • {path}
                        </div>
                      ))}
                      {files.length > 10 && (
                        <div className="text-sm text-muted-foreground italic">
                          ... and {files.length - 10} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Directory Structure */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <File className="h-5 w-5" />
            Directory Structure
          </CardTitle>
          <CardDescription>
            Files grouped by directory
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {Object.entries(filesByDirectory)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([dir, files]) => (
                  <div key={dir} className="space-y-1">
                    <div className="flex items-center gap-2 font-semibold text-sm">
                      <Badge variant="secondary">{dir || '/'}</Badge>
                      <span className="text-muted-foreground font-normal">
                        ({files.length} files)
                      </span>
                    </div>
                    <div className="ml-4 space-y-0.5">
                      {files.slice(0, 5).map((path, index) => (
                        <div key={index} className="text-sm font-mono text-muted-foreground">
                          {path.split('/').pop()}
                        </div>
                      ))}
                      {files.length > 5 && (
                        <div className="text-sm text-muted-foreground italic">
                          ... and {files.length - 5} more
                        </div>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
