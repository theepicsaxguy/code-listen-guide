import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  useListJobEpisodesEpisodesJobJobIdGet,
  useGetJobApiV1JobsJobIdGet,
  usePlanEpisodesEpisodesJobJobIdPlanPost,
} from '@/lib/api/generated';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, CheckCircle2, Loader2, Clock, FileCode, MessageSquare, Target } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import type { EpisodeResponse } from '@/lib/api/generated/codebaseAudiobookAPI.schemas';

export default function EpisodeOutlinePreview() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [approved, setApproved] = useState(false);

  const { data: jobData, isLoading: jobLoading } = useGetJobApiV1JobsJobIdGet(
    jobId || '',
    { query: { enabled: !!jobId } }
  );
  
  const { data: episodesData, isLoading: episodesLoading, refetch: refetchEpisodes } = useListJobEpisodesEpisodesJobJobIdGet(
    jobId || '',
    { query: { enabled: !!jobId } }
  );
  
  const planMutation = usePlanEpisodesEpisodesJobJobIdPlanPost();

  const isLoading = jobLoading || episodesLoading;
  const episodes = episodesData?.episodes || [];

  // Auto-plan episodes if they don't exist and job has selected_files
  useEffect(() => {
    if (!jobId || isLoading || planMutation.isPending || episodes.length > 0) return;
    if (!jobData) return;
    
    const job = jobData as any;
    if (job?.selected_files && Array.isArray(job.selected_files) && job.selected_files.length > 0) {
      planMutation.mutate(
        { jobId },
        {
          onSuccess: (data) => {
            toast({
              title: 'Episodes planned',
              description: `Created ${data?.total || 0} episodes for this job.`,
            });
            refetchEpisodes();
          },
          onError: (error: any) => {
            toast({
              title: 'Planning failed',
              description: error instanceof Error
                ? error.message
                : error?.message || 'Failed to plan episodes',
              variant: 'danger',
            });
          },
        }
      );
    }
  }, [jobId, jobData, isLoading, planMutation, episodes.length, refetchEpisodes, toast]);

  const handleApprove = async () => {
    if (!jobId) return;

    try {
      const { customInstance } = await import('@/lib/api/mutator');
      const result = await customInstance<{
        success: boolean;
        message: string;
        episode_count: number;
        job_status: string;
      }>({
        url: `/jobs/${jobId}/episodes/approve`,
        method: 'POST',
      });

      setApproved(true);
      
      toast({
        title: 'Episodes approved',
        description: `Approved ${result.episode_count || episodes.length} episodes. Generation will begin shortly.`,
      });

      // Navigate to job details
      setTimeout(() => {
        navigate(`/jobs/${jobId}`);
      }, 2000);
    } catch (error: any) {
      toast({
        title: 'Approval failed',
        description: error.message || 'Failed to approve episodes',
        variant: 'danger',
      });
    }
  };

  if (isLoading || planMutation.isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading episodes...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          
          <h1 className="text-4xl font-bold mb-2">Episode Outline Review</h1>
          <p className="text-muted-foreground">
            We've planned {episodes.length} thematic episodes based on architectural relationships in your codebase.
          </p>
        </div>

        {/* Episodes List */}
        {episodes.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileCode className="h-12 w-12 mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">No episodes planned yet.</p>
              {jobData && (jobData as any).selected_files ? (
                <Button onClick={() => planMutation.mutate({ jobId: jobId! })}>
                  Plan Episodes
                </Button>
              ) : (
                <p className="text-sm text-muted-foreground">Job must have selected files to plan episodes.</p>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6 mb-8">
            {episodes.map((episode) => (
              <EpisodeCard key={episode.id} episode={episode} />
            ))}
          </div>
        )}

        {/* Approval Section */}
        {episodes.length > 0 && (
          <Card className="sticky bottom-4">
            <CardHeader>
              <CardTitle>Ready to Approve?</CardTitle>
              <CardDescription>
                Review the episodes above. Once approved, dialogue generation will begin.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <span className="font-medium">
                    {episodes.length} episode{episodes.length !== 1 ? 's' : ''} ready
                  </span>
                </div>
                <Button
                  onClick={handleApprove}
                  disabled={approved}
                  size="lg"
                >
                  {approved ? 'Approved' : 'Approve Episodes & Continue'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function EpisodeCard({ episode }: { episode: EpisodeResponse }) {
  const fileClusters = episode.file_clusters || {};
  const conversationHooks = episode.conversation_hooks || [];
  const learningObjectives = episode.learning_objectives || [];
  
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Badge variant="outline">Episode {episode.episode_number}</Badge>
              {episode.architectural_boundary && (
                <Badge variant="secondary">{episode.architectural_boundary}</Badge>
              )}
              {episode.estimated_duration_minutes && (
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  {episode.estimated_duration_minutes} min
                </div>
              )}
            </div>
            <CardTitle className="text-2xl mb-2">{episode.title}</CardTitle>
            <CardDescription className="text-base">
              {episode.narrative_theme}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <Accordion type="multiple" className="w-full">
          {/* File Clusters */}
          <AccordionItem value="files">
            <AccordionTrigger>
              <div className="flex items-center gap-2">
                <FileCode className="h-4 w-4" />
                <span>Files ({Object.values(fileClusters).flat().length})</span>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-3">
                {Object.entries(fileClusters).map(([clusterName, files]) => (
                  <div key={clusterName}>
                    <Badge variant="outline" className="mb-2">{clusterName}</Badge>
                    <ul className="list-disc list-inside ml-2 space-y-1">
                      {(files as string[]).map((file) => (
                        <li key={file} className="text-sm font-mono">{file}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Conversation Hooks */}
          {conversationHooks.length > 0 && (
            <AccordionItem value="hooks">
              <AccordionTrigger>
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  <span>Conversation Topics ({conversationHooks.length})</span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <ul className="list-disc list-inside space-y-2">
                  {conversationHooks.map((hook, i) => (
                    <li key={i} className="text-sm">{hook}</li>
                  ))}
                </ul>
              </AccordionContent>
            </AccordionItem>
          )}

          {/* Learning Objectives */}
          {learningObjectives.length > 0 && (
            <AccordionItem value="objectives">
              <AccordionTrigger>
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  <span>Learning Objectives ({learningObjectives.length})</span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <ul className="list-disc list-inside space-y-2">
                  {learningObjectives.map((objective, i) => (
                    <li key={i} className="text-sm">{objective}</li>
                  ))}
                </ul>
              </AccordionContent>
            </AccordionItem>
          )}
        </Accordion>
      </CardContent>
    </Card>
  );
}
