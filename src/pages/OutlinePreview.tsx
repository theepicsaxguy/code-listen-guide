import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiClient } from '@/lib/api';
import { Outline, Job } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, CheckCircle2, Loader2, Edit3, Clock } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

export default function OutlinePreview() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [job, setJob] = useState<Job | null>(null);
  const [outline, setOutline] = useState<Outline | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isApproving, setIsApproving] = useState(false);

  useEffect(() => {
    loadData();
  }, [jobId]);

  const loadData = async () => {
    if (!jobId) return;

    try {
      const [jobData, outlineData] = await Promise.all([
        apiClient.getJob(jobId),
        apiClient.generateOutline(jobId, { repo_url: '', depth_tier: '' }),
      ]);
      setJob(jobData as Job);
      setOutline(outlineData as Outline);
    } catch (error: any) {
      toast({
        title: 'Failed to load outline',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

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

  const chapters = outline.outline_data.chapters;

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
          <p className="text-muted-foreground">{job.repo_name}</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Total Chapters</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{outline.outline_data.total_chapters}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Estimated Duration</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {Math.floor(outline.outline_data.total_estimated_duration_minutes / 60)}h{' '}
                {outline.outline_data.total_estimated_duration_minutes % 60}m
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Depth Tier</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold capitalize">{job.depth_tier}</p>
            </CardContent>
          </Card>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Chapter Outline</CardTitle>
            <CardDescription>
              {chapters.length} chapters covering the entire codebase
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
                          {chapter.topics.map((topic, i) => (
                            <li key={i}>{topic}</li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-sm font-semibold mb-2">Files:</h4>
                        <div className="flex flex-wrap gap-2">
                          {chapter.files_covered.map((file, i) => (
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

        <div className="flex gap-4">
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
