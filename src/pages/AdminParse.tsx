import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api';
import { 
  Loader2, 
  PlayCircle, 
  FileCode, 
  Database,
  GitBranch,
  Settings,
  BarChart3,
  Network,
  FileSearch,
  Microscope,
  Zap
} from 'lucide-react';
import { RepositoryBrowser, FileNode } from '@/components/RepositoryBrowser';
import { AdminFileViewer } from '@/components/AdminFileViewer';
import { ChunkVisualizer } from '@/components/ChunkVisualizer';
import { RelationshipGraph } from '@/components/RelationshipGraph';

export default function AdminParse() {
  const { toast } = useToast();
  
  // Form state
  const [repoUrl, setRepoUrl] = useState('https://github.com/microsoft/agent-framework');
  const [gitRef, setGitRef] = useState('main');
  const [includePatterns, setIncludePatterns] = useState('');
  const [excludePatterns, setExcludePatterns] = useState('*test*.py,*.min.js,*.lock');
  const [maxFileSizeKb, setMaxFileSizeKb] = useState(500);
  
  // Chonkie configuration
  const [enableCodeEnrichment, setEnableCodeEnrichment] = useState(true);
  const [enableFormulaEnrichment, setEnableFormulaEnrichment] = useState(false);
  const [enableTableExtraction, setEnableTableExtraction] = useState(true);
  
  // Results state
  const [isLoading, setIsLoading] = useState(false);
  const [parseResults, setParseResults] = useState<any>(null);
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  
  const handleParse = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.parseRepository({
        repo_url: repoUrl,
        git_ref: gitRef,
        include_patterns: includePatterns ? includePatterns.split(',').map(p => p.trim()) : undefined,
        exclude_patterns: excludePatterns ? excludePatterns.split(',').map(p => p.trim()) : undefined,
        max_file_size_kb: maxFileSizeKb,
        enable_code_enrichment: enableCodeEnrichment,
        enable_formula_enrichment: enableFormulaEnrichment,
        enable_table_extraction: enableTableExtraction,
      });
      
      setParseResults(response);
      toast({
        title: 'Repository parsed successfully',
        description: `${response.summary.total_files} files processed in ${response.execution_time_seconds}s`,
      });
    } catch (error: any) {
      toast({
        title: 'Parse failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const fileNodes: Record<string, FileNode> = parseResults?.modules 
    ? Object.entries(parseResults.modules).reduce((acc, [path, file]: [string, any]) => {
        acc[path] = {
          path: file.path,
          language: file.language,
          size_bytes: file.metadata.size_bytes,
          tags: file.metadata.tags,
          summary: file.metadata.summary,
          complexity: file.metadata.complexity,
          content: file.content,
          num_chunks: file.metadata.num_chunks,
          total_tokens: file.metadata.total_tokens,
        };
        return acc;
      }, {} as Record<string, FileNode>)
    : {};

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-[1800px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Microscope className="h-8 w-8" />
              Repository Parser Admin
            </h1>
            <p className="text-muted-foreground mt-1">
              Test chonkie configurations and analyze repository parsing
            </p>
          </div>
          <Badge variant="outline" className="text-lg px-4 py-2">
            <Zap className="h-4 w-4 mr-2" />
            Admin Mode
          </Badge>
        </div>

        {/* Configuration Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Parse Configuration
            </CardTitle>
            <CardDescription>
              Configure repository source and chonkie parsing parameters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Repository Settings */}
            <div className="grid lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 space-y-2">
                <Label htmlFor="repo-url" className="flex items-center gap-2">
                  <GitBranch className="h-4 w-4" />
                  Repository URL
                </Label>
                <Input
                  id="repo-url"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/owner/repo"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="git-ref">Branch/Tag/Commit</Label>
                <Input
                  id="git-ref"
                  value={gitRef}
                  onChange={(e) => setGitRef(e.target.value)}
                  placeholder="main"
                />
              </div>
            </div>

            {/* File Filters */}
            <div className="grid lg:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="include">Include Patterns (comma-separated)</Label>
                <Input
                  id="include"
                  value={includePatterns}
                  onChange={(e) => setIncludePatterns(e.target.value)}
                  placeholder="*.py,*.ts,*.js (leave empty for all)"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="exclude">Exclude Patterns (comma-separated)</Label>
                <Input
                  id="exclude"
                  value={excludePatterns}
                  onChange={(e) => setExcludePatterns(e.target.value)}
                  placeholder="*test*.py,*.min.js"
                />
              </div>
            </div>

            {/* Max File Size Slider */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Max File Size: {maxFileSizeKb} KB</Label>
                <span className="text-sm text-muted-foreground">
                  {formatBytes(maxFileSizeKb * 1024)}
                </span>
              </div>
              <Slider
                value={[maxFileSizeKb]}
                onValueChange={(val) => setMaxFileSizeKb(val[0])}
                min={50}
                max={5000}
                step={50}
                className="w-full"
              />
            </div>

            {/* Chonkie Enrichment Options */}
            <div className="border-t pt-4 space-y-4">
              <h3 className="font-semibold flex items-center gap-2">
                <FileCode className="h-4 w-4" />
                Chonkie Enrichment Features
              </h3>
              
              <div className="grid lg:grid-cols-3 gap-4">
                <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <Label htmlFor="code-enrichment" className="cursor-pointer">
                      Code Enrichment
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Extract functions, classes, imports
                    </p>
                  </div>
                  <Switch
                    id="code-enrichment"
                    checked={enableCodeEnrichment}
                    onCheckedChange={setEnableCodeEnrichment}
                  />
                </div>

                <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <Label htmlFor="formula-enrichment" className="cursor-pointer">
                      Formula Enrichment
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Extract LaTeX formulas
                    </p>
                  </div>
                  <Switch
                    id="formula-enrichment"
                    checked={enableFormulaEnrichment}
                    onCheckedChange={setEnableFormulaEnrichment}
                  />
                </div>

                <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <Label htmlFor="table-extraction" className="cursor-pointer">
                      Table Extraction
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Extract structured tables
                    </p>
                  </div>
                  <Switch
                    id="table-extraction"
                    checked={enableTableExtraction}
                    onCheckedChange={setEnableTableExtraction}
                  />
                </div>
              </div>
            </div>

            {/* Parse Button */}
            <Button 
              onClick={handleParse} 
              disabled={isLoading || !repoUrl}
              className="w-full"
              size="lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Parsing Repository...
                </>
              ) : (
                <>
                  <PlayCircle className="mr-2 h-5 w-5" />
                  Parse Repository
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        {parseResults && (
          <>
            {/* Summary Statistics */}
            <div className="grid lg:grid-cols-5 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Total Files</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{parseResults.summary.total_files}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatBytes(parseResults.summary.total_size_bytes)}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Languages</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{parseResults.summary.languages.length}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {parseResults.summary.languages.slice(0, 3).join(', ')}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {parseResults.summary.parse_success_rate.toFixed(1)}%
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Parse quality
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Frameworks</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{parseResults.summary.frameworks.length}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {parseResults.summary.frameworks.slice(0, 2).join(', ') || 'None detected'}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Parse Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {parseResults.execution_time_seconds.toFixed(1)}s
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {(parseResults.summary.total_size_bytes / 1024 / parseResults.execution_time_seconds).toFixed(0)} KB/s
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Main Analysis Tabs */}
            <Tabs defaultValue="browser" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="browser">
                  <FileSearch className="h-4 w-4 mr-2" />
                  File Browser
                </TabsTrigger>
                <TabsTrigger value="chunks">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Chunk Analysis
                </TabsTrigger>
                <TabsTrigger value="relationships">
                  <Network className="h-4 w-4 mr-2" />
                  Relationships
                </TabsTrigger>
                <TabsTrigger value="metadata">
                  <Database className="h-4 w-4 mr-2" />
                  Raw Metadata
                </TabsTrigger>
              </TabsList>

              <TabsContent value="browser" className="mt-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  <RepositoryBrowser
                    files={fileNodes}
                    onFileSelect={setSelectedFile}
                    selectedPath={selectedFile?.path}
                  />
                  {selectedFile ? (
                    <AdminFileViewer 
                      file={selectedFile}
                      rawData={parseResults.modules[selectedFile.path]}
                    />
                  ) : (
                    <Card>
                      <CardContent className="flex items-center justify-center h-[600px] text-muted-foreground">
                        <div className="text-center">
                          <FileCode className="h-12 w-12 mx-auto mb-4 opacity-20" />
                          <p>Select a file to view detailed analysis</p>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="chunks" className="mt-6">
                {selectedFile ? (
                  <ChunkVisualizer
                    file={selectedFile}
                    rawData={parseResults.modules[selectedFile.path]}
                  />
                ) : (
                  <Card>
                    <CardContent className="flex items-center justify-center h-[400px] text-muted-foreground">
                      <div className="text-center">
                        <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-20" />
                        <p>Select a file from the browser to view chunk analysis</p>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="relationships" className="mt-6">
                <RelationshipGraph
                  modules={parseResults.modules}
                  summary={parseResults.summary}
                />
              </TabsContent>

              <TabsContent value="metadata" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Raw Parse Response</CardTitle>
                    <CardDescription>
                      Complete JSON response from the parse endpoint
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[600px] w-full rounded-md border">
                      <pre className="p-4 text-xs">
                        <code>{JSON.stringify(parseResults, null, 2)}</code>
                      </pre>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </>
        )}

        {/* Warnings */}
        {parseResults?.summary.warnings && parseResults.summary.warnings.length > 0 && (
          <Card className="border-yellow-500">
            <CardHeader>
              <CardTitle className="text-yellow-600">Warnings</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-1">
                {parseResults.summary.warnings.map((warning: string, i: number) => (
                  <li key={i} className="text-sm text-muted-foreground">{warning}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
