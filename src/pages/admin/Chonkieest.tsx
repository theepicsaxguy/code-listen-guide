import { useState } from "react";
import { FileCode2, Loader2, CheckCircle, XCircle, Settings } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";

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

export default function chonkieTest() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/pallets/click");
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
          chonkie Parse Test
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

        {/* chonkie Options */}
        <div className="border-t border-gray-700 pt-6">
          <h3 className="text-white font-medium mb-4">chonkie Features</h3>
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
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Files Parsed</span>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-white">
                {result.summary.total_files}
              </div>
              <div className="text-sm text-gray-400 mt-1">
                {(result.summary.total_size_bytes / 1024).toFixed(1)} KB total
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Success Rate</span>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-white">
                {result.summary.parse_success_rate}%
              </div>
              <div className="text-sm text-gray-400 mt-1">
                {result.summary.languages.length} languages detected
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Execution Time</span>
                <Activity className="w-5 h-5 text-blue-500" />
              </div>
              <div className="text-3xl font-bold text-white">
                {result.execution_time_seconds}s
              </div>
              <div className="text-sm text-gray-400 mt-1">
                {(result.summary.total_size_bytes / result.execution_time_seconds / 1024).toFixed(1)} KB/s
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="bg-gray-800 rounded-lg p-6 space-y-4">
            <h3 className="text-white font-semibold text-lg">Details</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-gray-400 text-sm mb-2">Languages</h4>
                <div className="flex flex-wrap gap-2">
                  {result.summary.languages.length > 0 ? (
                    result.summary.languages.map((lang) => (
                      <span
                        key={lang}
                        className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm"
                      >
                        {lang}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-500">None detected</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-gray-400 text-sm mb-2">Frameworks</h4>
                <div className="flex flex-wrap gap-2">
                  {result.summary.frameworks.length > 0 ? (
                    result.summary.frameworks.map((fw) => (
                      <span
                        key={fw}
                        className="px-3 py-1 bg-purple-900/30 text-purple-300 rounded-full text-sm"
                      >
                        {fw}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-500">None detected</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-gray-400 text-sm mb-2">Patterns</h4>
                <div className="flex flex-wrap gap-2">
                  {result.summary.patterns.length > 0 ? (
                    result.summary.patterns.map((pattern) => (
                      <span
                        key={pattern}
                        className="px-3 py-1 bg-green-900/30 text-green-300 rounded-full text-sm"
                      >
                        {pattern}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-500">None detected</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-gray-400 text-sm mb-2">Entry Points</h4>
                <div className="space-y-1">
                  {result.summary.entry_points.length > 0 ? (
                    result.summary.entry_points.map((entry) => (
                      <div key={entry} className="text-sm text-gray-300 font-mono">
                        {entry}
                      </div>
                    ))
                  ) : (
                    <span className="text-gray-500">None detected</span>
                  )}
                </div>
              </div>
            </div>

            {result.summary.warnings.length > 0 && (
              <div className="border-t border-gray-700 pt-4">
                <h4 className="text-yellow-400 text-sm mb-2">Warnings</h4>
                <div className="space-y-1">
                  {result.summary.warnings.map((warning, idx) => (
                    <div key={idx} className="text-sm text-yellow-300">
                      • {warning}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sample Files */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-white font-semibold text-lg mb-4">
              Sample Files ({Math.min(5, Object.keys(result.modules).length)} of {Object.keys(result.modules).length})
            </h3>
            <div className="space-y-4">
              {Object.entries(result.modules)
                .slice(0, 5)
                .map(([path, data]: [string, any]) => (
                  <div key={path} className="border border-gray-700 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="font-mono text-sm text-blue-400">{path}</div>
                      <div className="text-xs text-gray-500">
                        {data.metadata.size_bytes} bytes
                      </div>
                    </div>
                    {data.language && (
                      <div className="text-xs text-gray-400 mb-2">
                        Language: {data.language}
                      </div>
                    )}
                    {data.metadata.tags && data.metadata.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {data.metadata.tags.slice(0, 5).map((tag: string) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-gray-900 text-gray-400 rounded text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                    {data.content && (
                      <div className="mt-2 bg-gray-900 rounded p-3 overflow-auto max-h-40">
                        <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
                          {data.content.substring(0, 300)}
                          {data.content.length > 300 && "..."}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
