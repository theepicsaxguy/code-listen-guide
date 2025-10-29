import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiClient } from '@/lib/api';
import { Job } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, ExternalLink, Loader2, CheckCircle2, AlertCircle, Download, XCircle } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export default function JobDetails() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCancelling, setIsCancelling] = useState(false);

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

  const handleCancelJob = async () => {
    if (!jobId) return;
    
    setIsCancelling(true);
    try {
      await apiClient.cancelJob(jobId);
      toast({
        title: 'Job cancelled',
        description: 'The job has been cancelled successfully.',
      });
      loadJob(); // Reload to get updated status
    } catch (error: any) {
      toast({
        title: 'Failed to cancel job',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setIsCancelling(false);
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
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isProcessing = job.status !== 'completed' && job.status !== 'failed';

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 max-w-5xl">
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
            <div className="flex gap-2">
              {isProcessing && (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" disabled={isCancelling}>
                      {isCancelling ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Cancelling...
                        </>
                      ) : (
                        <>
                          <XCircle className="mr-2 h-4 w-4" />
                          Cancel Job
                        </>
                      )}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will stop the audiobook generation process. Any progress will be lost and this action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>No, keep processing</AlertDialogCancel>
                      <AlertDialogAction onClick={handleCancelJob} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                        Yes, cancel job
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}
              {job.status === 'completed' && (
                <Button onClick={() => navigate(`/player/${job.id}`)}>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Open Player
                </Button>
              )}
            </div>
          </div>
          <Badge variant={job.status === 'completed' ? 'default' : job.status === 'failed' ? 'destructive' : 'secondary'} className="text-sm">
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
