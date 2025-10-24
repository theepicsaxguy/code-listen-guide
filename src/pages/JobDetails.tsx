import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiClient } from '@/lib/api';
import { Job, Chapter } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, ExternalLink, Loader2, CheckCircle2, AlertCircle, Download } from 'lucide-react';

export default function JobDetails() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [job, setJob] = useState<Job | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!jobId) return;

    loadJob();
    const interval = setInterval(loadJob, 3000); // Poll every 3s
    return () => clearInterval(interval);
  }, [jobId]);

  const loadJob = async () => {
    if (!jobId) return;

    try {
      const response = await apiClient.getJob(jobId);
      setJob(response as Job);
      setChapters(response.chapters || []);
    } catch (error: any) {
      toast({
        title: 'Failed to load job',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card>
          <CardContent className="text-center py-12">
            <p>Job not found</p>
            <Button onClick={() => navigate('/dashboard')} className="mt-4">
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isProcessing = !['completed', 'failed'].includes(job.status);

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
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">{job.repo_name}</h1>
              <p className="text-muted-foreground">{job.repo_url}</p>
            </div>
            {job.status === 'completed' && (
              <Button onClick={() => navigate(`/player/${job.id}`)}>
                <ExternalLink className="mr-2 h-4 w-4" />
                Open Player
              </Button>
            )}
          </div>
          <Badge variant={job.status === 'completed' ? 'default' : 'secondary'} className="text-sm">
            {job.status}
          </Badge>
        </div>

        {isProcessing && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Processing Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{job.current_stage}</span>
                  <span className="font-medium">{Math.round(job.progress_percentage)}%</span>
                </div>
                <Progress value={job.progress_percentage} className="h-2" />
              </div>
              <p className="text-sm text-muted-foreground">
                This may take 15-45 minutes depending on repository size and depth tier.
              </p>
            </CardContent>
          </Card>
        )}

        {job.status === 'failed' && job.error_message && (
          <Card className="mb-8 border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Processing Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{job.error_message}</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>
              Chapters {chapters.length > 0 && `(${chapters.length})`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chapters.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                Chapters will appear here as they are generated
              </p>
            ) : (
              <div className="space-y-3">
                {chapters.map((chapter) => (
                  <div
                    key={chapter.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <span className="text-sm text-muted-foreground font-mono">
                        Ch. {chapter.chapter_number}
                      </span>
                      <div className="flex-1">
                        <h4 className="font-medium">{chapter.title}</h4>
                        {chapter.description && (
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {chapter.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {chapter.audio_duration_seconds && (
                        <span className="text-sm text-muted-foreground">
                          {Math.floor(chapter.audio_duration_seconds / 60)}m
                        </span>
                      )}
                      {chapter.status === 'completed' ? (
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                      ) : (
                        <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {job.status === 'completed' && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Downloads</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Download className="mr-2 h-4 w-4" />
                Full Audiobook (MP3)
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Download className="mr-2 h-4 w-4" />
                All Scripts (ZIP)
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Download className="mr-2 h-4 w-4" />
                Metadata (JSON)
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
