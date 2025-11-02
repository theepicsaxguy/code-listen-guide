import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useGetJob, useCancelJob } from '@/lib/api/generated';
import type { JobResponse } from '@/lib/api/generated';
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
  const [isCancelling, setIsCancelling] = useState(false);

  const { data: job, isLoading, refetch } = useGetJob(
    jobId || '',
    {
      query: {
        enabled: !!jobId,
        refetchInterval: 3000, // Poll every 3s
      },
    }
  );

  const cancelJobMutation = useCancelJob();

  const handleCancelJob = async () => {
    if (!jobId) return;
    
    setIsCancelling(true);
    try {
      await cancelJobMutation.mutateAsync(jobId);
      toast({
        title: 'Job cancelled',
        description: 'The job has been cancelled successfully.',
      });
      refetch(); // Reload to get updated status
    } catch (error: any) {
      toast({
        title: 'Failed to cancel job',
        description: error.message,
        variant: 'danger',
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

  const jobData = job as unknown as Job | null;
  if (!jobData) {
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

  const isProcessing = jobData?.status !== 'completed' && jobData?.status !== 'failed';

  return (
    <div className="min-h-screen bg-background relative">
      {/* Radial gradient background accent */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />
      
      <header className="bg-surface">
        <div className="container mx-auto px-6 py-6 max-w-5xl">
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-5xl relative">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-semibold mb-2 text-foreground">{jobData.repo_name}</h1>
              <p className="text-muted-foreground leading-relaxed">{jobData.repo_url}</p>
            </div>
            <div className="flex gap-2">
              {isProcessing && (
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="danger" disabled={isCancelling}>
                      {isCancelling || cancelJobMutation.isPending ? (
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
                      <AlertDialogAction onClick={handleCancelJob} className="bg-danger text-danger-foreground hover:bg-danger/90">
                        Yes, cancel job
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              )}
              {jobData.status === 'completed' && (
                <Button onClick={() => navigate(`/player/${jobData.id}`)}>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Open Player
                </Button>
              )}
            </div>
          </div>
          <Badge variant={jobData.status === 'completed' ? 'default' : jobData.status === 'failed' ? 'danger' : 'secondary'} className="text-sm">
            {jobData.status}
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
                  <span className="text-muted-foreground">{jobData.current_stage}</span>
                  <span className="font-semibold text-foreground">{Math.round(jobData.progress_percentage)}%</span>
                </div>
                <Progress value={jobData.progress_percentage} className="h-2" />
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                This may take 15-45 minutes depending on repository size and depth tier.
              </p>
            </CardContent>
          </Card>
        )}

        {jobData.status === 'failed' && jobData.error_message && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-danger flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Processing Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed">{job.error_message}</p>
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
