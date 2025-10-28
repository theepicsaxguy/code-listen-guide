import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { Job } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { Plus, ExternalLink, Clock, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }

    loadJobs();
    const interval = setInterval(loadJobs, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, [user, navigate]);

  const loadJobs = async () => {
    try {
      const response = await apiClient.getJobs({ limit: 20 });
      setJobs(response.jobs || []);
    } catch (error: any) {
      console.error('Failed to load jobs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'default';
      case 'failed':
        return 'destructive';
      case 'pending':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/30 glass">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold gradient-text-primary">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground hidden sm:inline">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout} className="hover:border-primary hover:text-primary transition-colors">
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">Your <span className="gradient-text-accent">Audiobooks</span></h2>
            <p className="text-muted-foreground">Manage and listen to your generated audiobooks</p>
          </div>
          <Button
            onClick={() => navigate('/submit')}
            size="lg"
            className="bg-gradient-to-r from-primary to-accent hover:scale-105 shadow-[0_0_20px_rgba(138,43,226,0.3)] hover:shadow-[0_0_30px_rgba(0,255,255,0.4)] transition-all duration-300"
          >
            <Plus className="mr-2 h-5 w-5" />
            New Audiobook
          </Button>
        </div>

        {jobs.length === 0 ? (
          <Card className="text-center py-16 glass border-dashed border-2 hover:border-primary/50 transition-all">
            <CardContent className="space-y-6">
              <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                <Plus className="w-12 h-12 text-primary" />
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">No audiobooks yet</h3>
                <p className="text-muted-foreground mb-6">Start learning codebases through audio today!</p>
              </div>
              <Button
                onClick={() => navigate('/submit')}
                size="lg"
                className="bg-gradient-to-r from-primary to-accent hover:scale-105 shadow-[0_0_20px_rgba(138,43,226,0.3)] transition-all duration-300"
              >
                <Plus className="mr-2 h-5 w-5" />
                Create Your First Audiobook
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <Card
                key={job.id}
                className="glass hover:border-primary/50 hover-lift cursor-pointer transition-all duration-300 overflow-hidden group"
                onClick={() => navigate(`/jobs/${job.id}`)}
              >
                {/* Gradient overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                <CardHeader className="relative z-10">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-1 group-hover:text-primary transition-colors">{job.repo_name}</CardTitle>
                      <CardDescription className="text-xs">{job.repo_owner}</CardDescription>
                    </div>
                    <div className="animate-scale-in">
                      {getStatusIcon(job.status)}
                    </div>
                  </div>
                  <Badge variant={getStatusColor(job.status)} className="w-fit">
                    {job.status}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-4 relative z-10">
                  {job.status !== 'completed' && job.status !== 'failed' && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{job.current_stage}</span>
                        <span className="font-medium gradient-text-accent">{Math.round(job.progress_percentage)}%</span>
                      </div>
                      <Progress value={job.progress_percentage} className="h-2" />
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span className="capitalize font-medium">{job.depth_tier}</span>
                    {job.estimated_duration_minutes && (
                      <span className="font-medium">{Math.floor(job.estimated_duration_minutes / 60)}h {job.estimated_duration_minutes % 60}m</span>
                    )}
                  </div>

                  {job.status === 'completed' && (
                    <Button
                      className="w-full bg-gradient-to-r from-primary to-accent hover:scale-105 shadow-[0_0_15px_rgba(138,43,226,0.3)] transition-all duration-300"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/player/${job.id}`);
                      }}
                    >
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Listen Now
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
