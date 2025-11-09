import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileNode } from './RepositoryBrowser';
import { BarChart3, FileText, Hash, ArrowRight } from 'lucide-react';

interface Chunk {
  index: number;
  token_count: number;
  start_index: number;
  end_index: number;
  text: string;
}

export interface ChunkVisualizerProps {
  file: FileNode;
  rawData: {
    chunks?: Chunk[];
    [key: string]: unknown;
  };
}

export function ChunkVisualizer({ file, rawData }: ChunkVisualizerProps) {
  const chunks = rawData?.chunks || [];
  
  if (!chunks || chunks.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[25rem] text-muted-foreground">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-20" />
            <p>No chunk information available for this file</p>
            <p className="text-sm mt-2">File may not have been chunked or chunking data wasn't saved</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalTokens = chunks.reduce((sum: number, chunk: Chunk) => sum + (chunk.token_count || 0), 0);
  const avgTokensPerChunk = totalTokens / chunks.length;
  const maxTokens = Math.max(...chunks.map((c: Chunk) => c.token_count || 0));
  const minTokens = Math.min(...chunks.map((c: Chunk) => c.token_count || 0));

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Chunks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{chunks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Avg Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{Math.round(avgTokensPerChunk)}</div>
            <p className="text-xs text-muted-foreground mt-1">per chunk</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Size Range</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold">{minTokens} - {maxTokens}</div>
            <p className="text-xs text-muted-foreground mt-1">tokens</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{totalTokens.toLocaleString()}</div>
          </CardContent>
        </Card>
      </div>

      {/* Chunk Size Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Chunk Size Distribution
          </CardTitle>
          <CardDescription>
            Visual representation of token distribution across chunks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {chunks.map((chunk: Chunk, index: number) => {
              const percentage = (chunk.token_count / maxTokens) * 100;
              return (
                <div key={index} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-mono text-muted-foreground">
                      Chunk {chunk.index}
                    </span>
                    <span className="font-semibold">
                      {chunk.token_count} tokens
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Chunk Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Chunk Contents
          </CardTitle>
          <CardDescription>
            Detailed view of each chunk's text and boundaries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[37.5rem] w-full">
            <div className="space-y-6">
              {chunks.map((chunk: Chunk, index: number) => (
                <div key={index} className="border rounded-card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="font-mono">
                        Chunk {chunk.index}
                      </Badge>
                      <div className="text-sm text-muted-foreground flex items-center gap-2">
                        <Hash className="h-3 w-3" />
                        {chunk.token_count} tokens
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground font-mono">
                      Chars {chunk.start_index} <ArrowRight className="h-3 w-3 inline" /> {chunk.end_index}
                    </div>
                  </div>

                  <div className="bg-muted rounded-md p-3">
                    <pre className="text-sm whitespace-pre-wrap">
                      <code>{chunk.text}</code>
                    </pre>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs text-muted-foreground">
                    <div>
                      <span className="font-semibold">Start:</span> {chunk.start_index}
                    </div>
                    <div>
                      <span className="font-semibold">End:</span> {chunk.end_index}
                    </div>
                    <div>
                      <span className="font-semibold">Length:</span> {chunk.end_index - chunk.start_index} chars
                    </div>
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
