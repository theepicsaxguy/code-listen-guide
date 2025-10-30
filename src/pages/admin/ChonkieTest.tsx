import { useMemo, useState } from "react";
import { AdminFileViewer } from '@/components/AdminFileViewer';
import { ChunkVisualizer } from '@/components/ChunkVisualizer';
import { RelationshipGraph } from '@/components/RelationshipGraph';
import { RepositoryBrowser, FileNode } from '@/components/RepositoryBrowser';
import { FileCode2, Loader2, CheckCircle, XCircle, Settings, Activity } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface ParseResult {
  repository_url: string;
  git_ref: string;
  commit_sha: string | null;
  modules: Record<string, any>;
  summary: {
    total_files: number;
    total_size_bytes: number;
    languages: string[];
    frameworks: string[];
    patterns: string[];
    entry_points: string[];
    parse_success_rate: number;
    warnings: string[];
  };
  execution_time_seconds: number;
}

export default function ChonkieTest() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/microsoft/agent-framework/");
  const [gitRef, setGitRef] = useState("main");
  const [maxFileSizeKb, setMaxFileSizeKb] = useState(500);
  const [enableCodeEnrichment, setEnableCodeEnrichment] = useState(true);
  const [enableFormulaEnrichment, setEnableFormulaEnrichment] = useState(false);
  const [enableTableExtraction, setEnableTableExtraction] = useState(true);
  const [includePatterns, setIncludePatterns] = useState("");
  const [excludePatterns, setExcludePatterns] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ParseResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // For file selection in UI
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const selectedFile: FileNode | null = useMemo(() => {
    if (!result || !selectedPath) return null;
    const file = result.modules[selectedPath];
    if (!file) return null;
    // Add path to file object for AdminFileViewer
    return { ...file, path: selectedPath };
  }, [result, selectedPath]);

  const handleParse = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiClient.parseRepository({
        repo_url: repoUrl,
        git_ref: gitRef,
        max_file_size_kb: maxFileSizeKb,
        enable_code_enrichment: enableCodeEnrichment,
        enable_formula_enrichment: enableFormulaEnrichment,
        enable_table_extraction: enableTableExtraction,
        include_patterns: includePatterns ? includePatterns.split(",").map((p) => p.trim()) : null,
        exclude_patterns: excludePatterns ? excludePatterns.split(",").map((p) => p.trim()) : null,
      });

      setResult(data);
      toast.success("Repository parsed successfully!");
    } catch (err: any) {
      setError(err.message || "Failed to parse repository");
      toast.error(err.message || "Failed to parse repository");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <FileCode2 className="w-8 h-8" />
          Chonkie Parse Test
        </h1>
        <p className="text-gray-400 mt-1">
          Test the chonkie parsing pipeline with configurable settings
        </p>
      </div>

      {/* Configuration Form */}
      <div className="bg-gray-800 rounded-lg p-6 space-y-6">
        <div className="flex items-center gap-2 text-white font-semibold mb-4">
          <Settings className="w-5 h-5" />
          Configuration
        </div>

        {/* Repository Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Repository URL *
            </label>
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Git Ref (branch/tag)
            </label>
            <input
              type="text"
              value={gitRef}
              onChange={(e) => setGitRef(e.target.value)}
              placeholder="main"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* File Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Include Patterns (comma-separated)
            </label>
            <input
              type="text"
              value={includePatterns}
              onChange={(e) => setIncludePatterns(e.target.value)}
              placeholder="*.py, *.ts, src/**/*"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Leave empty to include all files</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Exclude Patterns (comma-separated)
            </label>
            <input
              type="text"
              value={excludePatterns}
              onChange={(e) => setExcludePatterns(e.target.value)}
              placeholder="*test*.py, *.min.js"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Leave empty to exclude nothing</p>
          </div>
        </div>

        {/* Size Limit */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Max File Size (KB)
          </label>
          <input
            type="number"
            value={maxFileSizeKb}
            onChange={(e) => setMaxFileSizeKb(Number(e.target.value))}
            min="1"
            max="5000"
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Chonkie Options */}
        <div className="border-t border-gray-700 pt-6">
          <h3 className="text-white font-medium mb-4">Chonkie Features</h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={enableCodeEnrichment}
                onChange={(e) => setEnableCodeEnrichment(e.target.checked)}
                className="w-5 h-5 rounded bg-gray-900 border-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="text-white">Code Enrichment</div>
                <div className="text-sm text-gray-400">
                  Extract functions, classes, imports, and code structure
                </div>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={enableFormulaEnrichment}
                onChange={(e) => setEnableFormulaEnrichment(e.target.checked)}
                className="w-5 h-5 rounded bg-gray-900 border-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="text-white">Formula Enrichment</div>
                <div className="text-sm text-gray-400">
                  Parse mathematical formulas (useful for scientific papers)
                </div>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={enableTableExtraction}
                onChange={(e) => setEnableTableExtraction(e.target.checked)}
                className="w-5 h-5 rounded bg-gray-900 border-gray-700 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="text-white">Table Extraction</div>
                <div className="text-sm text-gray-400">
                  Extract tables from documents and markdown files
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* Parse Button */}
        <div className="flex justify-end pt-4">
          <button
            onClick={handleParse}
            disabled={isLoading || !repoUrl}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Parsing...
              </>
            ) : (
              <>
                <FileCode2 className="w-5 h-5" />
                Parse Repository
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 flex items-start gap-3">
          <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-red-500 font-semibold">Error</h3>
            <p className="text-red-300 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-10">
          {/* Relationship Graph */}
          <RelationshipGraph modules={result.modules} summary={result.summary} />

          {/* Repository Browser and File Viewer */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <RepositoryBrowser
              files={Object.fromEntries(
                Object.entries(result.modules).map(([path, file]) => [path, { ...file, path }])
              )}
              onFileSelect={file => setSelectedPath(file.path)}
              selectedPath={selectedPath || undefined}
            />
            {selectedFile ? (
              <div className="space-y-6">
                <AdminFileViewer file={selectedFile} rawData={result.modules[selectedFile.path]} />
                <ChunkVisualizer file={selectedFile} rawData={result.modules[selectedFile.path]} />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <span>Select a file to view details</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
