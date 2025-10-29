import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiClient } from '@/lib/api';
import { Outline, Job } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, CheckCircle2, Loader2, Edit3, Clock, FileCode } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RepositoryBrowser, FileNode } from '@/components/RepositoryBrowser';
import { FileViewer } from '@/components/FileViewer';

export default function OutlinePreview() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [job, setJob] = useState<Job | null>(null);
  const [outline, setOutline] = useState<Outline | null>(null);
  const [repositoryData, setRepositoryData] = useState<Record<string, FileNode> | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isApproving, setIsApproving] = useState(false);

  useEffect(() => {
    let isActive = true;
    if (!jobId) {
      setJob(null);
      setOutline(null);
      setIsLoading(false);
      return;
    }

    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [jobData, outlineData] = await Promise.all([
          apiClient.getJob(jobId),
          apiClient.getOutline(jobId),
        ]);

        if (!isActive) return;

        setJob(jobData as Job);
        setOutline(outlineData as Outline);

        // Fetch repository analysis if available
        try {
          const parseResponse = await apiClient.parseRepository({
            repo_url: jobData.repo_url,
            git_ref: jobData.git_ref || 'main',
          });
          if (!isActive) return;
          // Convert ParsedFile to FileNode format
          const fileNodes: Record<string, FileNode> = {};
          Object.entries(parseResponse.modules).forEach(([path, file]) => {
            fileNodes[path] = {
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
          });
          setRepositoryData(fileNodes);
        } catch (parseError) {
          console.warn('Failed to fetch repository data:', parseError);
        }
      } catch (error: unknown) {
        if (!isActive) return;
        setOutline(null);
        toast({
          title: 'Failed to load outline',
          description:
            error instanceof Error ? error.message : 'Unable to fetch outline details.',
          variant: 'destructive',
        });
      } finally {
        if (isActive) setIsLoading(false);
      }
    };
    fetchData();
    return () => {
      isActive = false;
    };
  }, [jobId, toast]);

  const handleApprove = async () => {
    if (!jobId || !outline) return;

    setIsApproving(true);
    try {
      const response = await apiClient.approveOutline(jobId, outline.id);
      
      toast({
        title: 'Outline approved!',
        description: 'Proceeding to payment...',
      });

      // Redirect to payment (Stripe checkout)
      // In a real implementation, you'd open Stripe checkout here
      navigate(`/jobs/${jobId}`);
    } catch (error: any) {
      toast({
        title: 'Failed to approve outline',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setIsApproving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!outline || !job) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card>
          <CardContent className="text-center py-12">
            <p>Outline not found</p>
            <Button onClick={() => navigate('/dashboard')} className="mt-4">
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const chapters = outline.outline_data.chapters ?? [];
  const totalChapters = outline.outline_data.total_chapters ?? chapters.length;
  const totalMinutes =
    outline.outline_data.total_estimated_duration_minutes ??
    chapters.reduce((sum, chapter) => sum + Math.max(chapter.estimated_duration_minutes, 0), 0);
  const totalHours = Math.floor(totalMinutes / 60);
  const remainingMinutes = totalMinutes % 60;

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Review Audiobook Outline</h1>
        </div>
        <Tabs defaultValue="outline" className="mb-8">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="outline">Chapter Outline</TabsTrigger>
            <TabsTrigger value="repository">
              <FileCode className="mr-2 h-4 w-4" />
              Repository Browser
            </TabsTrigger>
          </TabsList>

          <TabsContent value="outline" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Chapter Outline</CardTitle>
                <CardDescription>
                  {totalChapters} chapters covering the entire codebase
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Accordion type="single" collapsible className="w-full">
                  {chapters.map((chapter, index) => (
                    <AccordionItem key={index} value={`chapter-${index}`}>
                      <AccordionTrigger>
                        <div className="flex items-center gap-3 text-left">
                          <span className="text-muted-foreground font-mono text-sm">
                            Ch. {chapter.number}
                          </span>
                          <span className="font-medium">{chapter.title}</span>
                          <Clock className="ml-auto h-4 w-4 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">
                            {chapter.estimated_duration_minutes}m
                          </span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-4 pt-4">
                          <p className="text-sm text-muted-foreground">{chapter.description}</p>
                          <div>
                            <h4 className="text-sm font-semibold mb-2">Topics Covered:</h4>
                            <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                              {(chapter.topics ?? []).map((topic, i) => (
                                <li key={i}>{topic}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold mb-2">Files:</h4>
                            <div className="flex flex-wrap gap-2">
                              {(chapter.files_covered ?? []).map((file, i) => (
                                <code key={i} className="text-xs bg-muted px-2 py-1 rounded">
                                  {file}
                                </code>
                              ))}
                            </div>
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="repository" className="mt-6">
            {repositoryData ? (
              <div className="grid lg:grid-cols-2 gap-6">
                <RepositoryBrowser
                  files={repositoryData}
                  onFileSelect={setSelectedFile}
                  selectedPath={selectedFile?.path}
                />
                {selectedFile ? (
                  <FileViewer file={selectedFile} />
                ) : (
                  <Card>
                    <CardContent className="flex items-center justify-center h-[600px] text-muted-foreground">
                      <div className="text-center">
                        <FileCode className="h-12 w-12 mx-auto mb-4 opacity-20" />
                        <p>Select a file to view its contents</p>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center h-[400px] text-muted-foreground">
                  <div className="text-center">
                    <Loader2 className="h-8 w-8 mx-auto mb-4 animate-spin" />
                    <p>Loading repository data...</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
        <div className="flex gap-4 mt-8">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => navigate(`/jobs/${jobId}`)}
          >
            <Edit3 className="mr-2 h-4 w-4" />
            Customize Outline
          </Button>
          <Button
            className="flex-1"
            onClick={handleApprove}
            disabled={isApproving}
          >
            {isApproving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Approve & Continue to Payment
              </>
            )}
          </Button>
        </div>
      </main>
    </div>
  );
}
