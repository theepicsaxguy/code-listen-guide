import { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react';
import { FileTreeSelector } from '@/components/FileTreeSelector';
import { LanguagePrioritySelector } from '@/components/LanguagePrioritySelector';
import { useToast } from '@/hooks/use-toast';

export default function ScopeSelection() {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();

  const { repoUrl, gitRef, selectedDepth, parseResult } = location.state || {};

  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [excludedPatterns, setExcludedPatterns] = useState<string[]>([
    'node_modules/**',
    '*.test.ts',
    '*.test.js',
    '*.spec.ts',
    '*.spec.js',
    '__tests__/**',
    'test/**',
    'tests/**',
  ]);
  const [primaryLanguage, setPrimaryLanguage] = useState<string | null>(null);

  if (!parseResult) {
    navigate('/submit');
    return null;
  }

  const languages = useMemo(() => {
    const counts: Record<string, number> = {};

    Object.values(parseResult.modules).forEach((module: any) => {
      const language = module?.language;
      if (!language) {
        return;
      }

      counts[language] = (counts[language] ?? 0) + 1;
    });

    const totalFiles = parseResult.summary.total_files;

    if (totalFiles === 0) {
      return Object.keys(counts).reduce<Record<string, number>>((acc, language) => {
        acc[language] = 0;
        return acc;
      }, {});
    }

    return Object.entries(counts).reduce<Record<string, number>>((acc, [language, count]) => {
      acc[language] = Math.round((count / totalFiles) * 100);
      return acc;
    }, {});
  }, [parseResult]);

  const isMixedStack = Object.keys(languages).length > 1;

  const handleContinue = () => {
    if (isMixedStack && !primaryLanguage) {
      toast({
        title: 'Select primary language',
        description: 'Please choose the primary language for this mixed-stack repository',
        variant: 'destructive',
      });
      return;
    }

    navigate('/cost-estimate', {
      state: {
        repoUrl,
        gitRef,
        selectedDepth,
        parseResult,
        selectedFiles: selectedFiles.length > 0 ? selectedFiles : null,
        excludedPatterns,
        primaryLanguage,
      },
    });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Radial gradient accent */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <header className="relative z-10 bg-surface border-b">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/repository-preview', { state: location.state })}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Preview
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-7xl relative z-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4 text-foreground">Select Scope</h1>
          <p className="text-muted-foreground">
            Choose which files to include in your podcast. Smart defaults are pre-selected.
          </p>
        </div>

        {/* Language Priority Selector (if mixed stack) */}
        {isMixedStack && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Multiple Languages Detected</CardTitle>
              <CardDescription>
                This repository uses multiple programming languages. Select the primary language to focus the podcast on.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <LanguagePrioritySelector
                languages={languages}
                selectedLanguage={primaryLanguage}
                onSelect={setPrimaryLanguage}
              />
            </CardContent>
          </Card>
        )}

        {/* File Tree Selector */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>File Selection</CardTitle>
            <CardDescription>
              Select specific files or folders to include. By default, common test and build files are excluded.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FileTreeSelector
              modules={parseResult.modules}
              selectedFiles={selectedFiles}
              excludedPatterns={excludedPatterns}
              onSelectionChange={setSelectedFiles}
              onExclusionChange={setExcludedPatterns}
            />
          </CardContent>
        </Card>

        {/* Summary */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              Scope Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Files</p>
                <p className="text-2xl font-bold">{parseResult.summary.total_files}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Selected</p>
                <p className="text-2xl font-bold">
                  {selectedFiles.length > 0 ? selectedFiles.length : parseResult.summary.total_files}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Excluded Patterns</p>
                <p className="text-2xl font-bold">{excludedPatterns.length}</p>
              </div>
              {isMixedStack && (
                <div>
                  <p className="text-sm text-muted-foreground">Primary Language</p>
                  <p className="text-2xl font-bold">{primaryLanguage || 'Not set'}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <Button variant="outline" onClick={() => navigate('/repository-preview', { state: location.state })}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button onClick={handleContinue} size="lg">
            Continue to Cost Estimate
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
