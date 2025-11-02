import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, ArrowRight, FileText, FolderTree, Languages } from 'lucide-react';
import { ReadmeViewer } from '@/components/ReadmeViewer';
import { RepositoryBrowser } from '@/components/RepositoryBrowser';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api';

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

export default function RepositoryPreview() {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [readmeContent, setReadmeContent] = useState<string | null>(null);

  // Get repo details from location state
  const { repoUrl, gitRef, selectedDepth } = location.state || {};

  useEffect(() => {
    if (!repoUrl) {
      navigate('/submit');
      return;
    }

    const parseRepo = async () => {
      try {
        setIsLoading(true);
        const result = await apiClient.parseRepository({
          repo_url: repoUrl,
          git_ref: gitRef || 'main',
        });

        setParseResult(result);

        // Find README file
        const readmeFile = Object.entries(result.modules).find(([path]) => 
          path.toLowerCase().includes('readme.md') || 
          path.toLowerCase() === 'readme'
        );

        if (readmeFile) {
          setReadmeContent(readmeFile[1].content || '');
        }
      } catch (error: any) {
        toast({
          title: 'Failed to parse repository',
          description: error.message || 'Could not analyze the repository',
          variant: 'destructive',
        });
        navigate('/submit');
      } finally {
        setIsLoading(false);
      }
    };

    parseRepo();
  }, [repoUrl, gitRef, navigate, toast]);

  const handleContinue = () => {
    navigate('/scope-selection', {
      state: {
        repoUrl,
        gitRef,
        selectedDepth,
        parseResult,
      },
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="relative z-10 bg-surface border-b">
          <div className="container mx-auto px-6 py-4">
            <Button variant="ghost" onClick={() => navigate('/submit')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-7xl">
          <div className="space-y-6">
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-96 w-full" />
          </div>
        </main>
      </div>
    );
  }

  if (!parseResult) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Radial gradient accent */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <header className="relative z-10 bg-surface border-b">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/submit')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Repository Entry
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-7xl relative z-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4 text-foreground">Repository Preview</h1>
          <p className="text-muted-foreground">
            Review the repository structure before selecting scope
          </p>
        </div>

        {/* Repository Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Repository Summary
            </CardTitle>
            <CardDescription>
              {repoUrl} ({gitRef})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Files</p>
                <p className="text-2xl font-bold">{parseResult.summary.total_files}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Size</p>
                <p className="text-2xl font-bold">
                  {(parseResult.summary.total_size_bytes / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Languages</p>
                <p className="text-2xl font-bold">{parseResult.summary.languages.length}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Parse Success</p>
                <p className="text-2xl font-bold">{parseResult.summary.parse_success_rate}%</p>
              </div>
            </div>

            {parseResult.summary.languages.length > 0 && (
              <div className="mt-4">
                <div className="flex items-center gap-2 mb-2">
                  <Languages className="h-4 w-4" />
                  <span className="text-sm font-medium">Detected Languages</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {parseResult.summary.languages.map((lang) => (
                    <Badge key={lang} variant="secondary">
                      {lang}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {parseResult.summary.frameworks.length > 0 && (
              <div className="mt-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium">Frameworks</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {parseResult.summary.frameworks.map((framework) => (
                    <Badge key={framework} variant="outline">
                      {framework}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* README Viewer */}
          {readmeContent && (
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  README
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ReadmeViewer content={readmeContent} />
              </CardContent>
            </Card>
          )}

          {/* File Tree Browser */}
          <Card className={readmeContent ? 'md:col-span-1' : 'md:col-span-2'}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FolderTree className="h-5 w-5" />
                File Structure
              </CardTitle>
            </CardHeader>
            <CardContent>
              <RepositoryBrowser modules={parseResult.modules} />
            </CardContent>
          </Card>
        </div>

        {/* Warnings */}
        {parseResult.summary.warnings.length > 0 && (
          <Card className="mb-8 border-yellow-500/50">
            <CardHeader>
              <CardTitle className="text-yellow-600 dark:text-yellow-500">Warnings</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-1">
                {parseResult.summary.warnings.map((warning, i) => (
                  <li key={i} className="text-sm text-muted-foreground">
                    {warning}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={() => navigate('/submit')}>
            Change Repository
          </Button>
          <Button onClick={handleContinue} size="lg">
            Continue to Scope Selection
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
