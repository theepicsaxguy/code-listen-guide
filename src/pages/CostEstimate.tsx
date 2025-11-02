import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, DollarSign, Zap, Clock, FileText, CheckCircle2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api';

interface CostEstimate {
  estimated_cost_cents: number;
  estimated_duration_minutes: number;
  estimated_chapters: number;
  depth_tier: string;
  llm_tokens?: number;
  tts_chars?: number;
  llm_cost_cents?: number;
  tts_cost_cents?: number;
  total_cost_cents?: number;
}

export default function CostEstimate() {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();

  const {
    repoUrl,
    gitRef,
    selectedDepth,
    parseResult,
    selectedFiles,
    excludedPatterns,
    primaryLanguage,
  } = location.state || {};

  const [estimate, setEstimate] = useState<CostEstimate | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [approved, setApproved] = useState(false);
  const [isCreatingJob, setIsCreatingJob] = useState(false);

  useEffect(() => {
    if (!repoUrl || !selectedDepth) {
      navigate('/submit');
      return;
    }

    const getEstimate = async () => {
      try {
        setIsLoading(true);
        const result = await apiClient.estimateJob({
          repo_url: repoUrl,
          git_ref: gitRef || 'main',
          depth_tier: selectedDepth,
          selected_files: selectedFiles,
          excluded_patterns: excludedPatterns,
        });

        setEstimate(result);
      } catch (error: any) {
        toast({
          title: 'Failed to estimate cost',
          description: error.message || 'Could not calculate token estimate',
          variant: 'destructive',
        });
        navigate('/scope-selection', { state: location.state });
      } finally {
        setIsLoading(false);
      }
    };

    getEstimate();
  }, [repoUrl, selectedDepth, gitRef, selectedFiles, excludedPatterns, navigate, toast]);

  const handleApprove = async () => {
    if (!approved) {
      toast({
        title: 'Approval required',
        description: 'Please check the box to approve this cost estimate',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsCreatingJob(true);
      const job = await apiClient.createJob({
        repo_url: repoUrl,
        depth_tier: selectedDepth,
        git_ref: gitRef || 'main',
        selected_files: selectedFiles,
        excluded_patterns: excludedPatterns,
        primary_language: primaryLanguage,
        estimated_total_tokens: estimate?.llm_tokens || 0 + (estimate?.tts_chars || 0),
        user_approved_cost: true,
      });

      toast({
        title: 'Job created!',
        description: 'Proceeding to payment...',
      });

      // Navigate to payment (or outline approval if no payment needed)
      navigate(`/jobs/${job.id}/outline`);
    } catch (error: any) {
      toast({
        title: 'Failed to create job',
        description: error.message || 'Could not create audiobook job',
        variant: 'destructive',
      });
    } finally {
      setIsCreatingJob(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="relative z-10 bg-surface border-b">
          <div className="container mx-auto px-6 py-4">
            <Button variant="ghost" onClick={() => navigate('/scope-selection', { state: location.state })}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-4xl">
          <div className="space-y-6">
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-64 w-full" />
          </div>
        </main>
      </div>
    );
  }

  if (!estimate) {
    return null;
  }

  const formatCost = (cents: number) => `$${(cents / 100).toFixed(2)}`;
  const formatNumber = (num: number) => num.toLocaleString();

  return (
    <div className="min-h-screen bg-background">
      {/* Radial gradient accent */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <header className="relative z-10 bg-surface border-b">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/scope-selection', { state: location.state })}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Scope Selection
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl relative z-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4 text-foreground">Cost Estimate</h1>
          <p className="text-muted-foreground">
            Review the token usage and cost breakdown before proceeding
          </p>
        </div>

        {/* Token Usage Breakdown */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              Token Usage
            </CardTitle>
            <CardDescription>
              Based on actual code analysis and selected scope
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">LLM Tokens (Code Analysis & Script Generation)</span>
                  <span className="text-sm font-bold">{formatNumber(estimate.llm_tokens || 0)}</span>
                </div>
                <Progress value={60} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">TTS Characters (Audio Synthesis)</span>
                  <span className="text-sm font-bold">{formatNumber(estimate.tts_chars || 0)}</span>
                </div>
                <Progress value={40} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cost Breakdown */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-500" />
              Cost Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">LLM Processing</span>
                <span className="text-sm font-medium">{formatCost(estimate.llm_cost_cents || 0)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Text-to-Speech</span>
                <span className="text-sm font-medium">{formatCost(estimate.tts_cost_cents || 0)}</span>
              </div>
              <div className="border-t pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-bold">Total Estimated Cost</span>
                  <span className="text-2xl font-bold text-primary">
                    {formatCost(estimate.total_cost_cents || estimate.estimated_cost_cents)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Deliverables Summary */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-500" />
              What You'll Get
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Clock className="h-8 w-8 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="text-xl font-bold">
                  {Math.floor(estimate.estimated_duration_minutes / 60)}h {estimate.estimated_duration_minutes % 60}m
                </p>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground">Episodes</p>
                <p className="text-xl font-bold">{estimate.estimated_chapters}</p>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <CheckCircle2 className="h-8 w-8 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground">Depth Tier</p>
                <p className="text-xl font-bold capitalize">{estimate.depth_tier}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Approval Section */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3 mb-6">
              <Checkbox
                id="cost-approval"
                checked={approved}
                onCheckedChange={(checked) => setApproved(checked === true)}
              />
              <div className="flex-1">
                <Label
                  htmlFor="cost-approval"
                  className="text-sm font-medium leading-none cursor-pointer"
                >
                  I approve this cost estimate
                </Label>
                <p className="text-sm text-muted-foreground mt-1">
                  I understand that {formatCost(estimate.total_cost_cents || estimate.estimated_cost_cents)} in tokens will be used to generate this podcast, 
                  and I authorize the system to proceed with processing.
                </p>
              </div>
            </div>

            <Button
              onClick={handleApprove}
              disabled={!approved || isCreatingJob}
              size="lg"
              className="w-full"
            >
              {isCreatingJob ? (
                'Creating Job...'
              ) : (
                <>
                  Approve & Continue to Payment
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
