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
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">Your Audiobooks</h2>
            <p className="text-muted-foreground">Manage and listen to your generated audiobooks</p>
          </div>
          <Button onClick={() => navigate('/submit')} size="lg">
            <Plus className="mr-2 h-5 w-5" />
            New Audiobook
          </Button>
        </div>

        {jobs.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-muted-foreground mb-4">No audiobooks yet</p>
              <Button onClick={() => navigate('/submit')}>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Audiobook
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <Card key={job.id} className="hover-scale cursor-pointer" onClick={() => navigate(`/jobs/${job.id}`)}>
                <CardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-1">{job.repo_name}</CardTitle>
                      <CardDescription className="text-xs">{job.repo_owner}</CardDescription>
                    </div>
                    {getStatusIcon(job.status)}
                  </div>
                  <Badge variant={getStatusColor(job.status)} className="w-fit">
                    {job.status}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-4">
                  {job.status !== 'completed' && job.status !== 'failed' && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{job.current_stage}</span>
                        <span className="font-medium">{Math.round(job.progress_percentage)}%</span>
                      </div>
                      <Progress value={job.progress_percentage} />
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span className="capitalize">{job.depth_tier}</span>
                    {job.estimated_duration_minutes && (
                      <span>{Math.floor(job.estimated_duration_minutes / 60)}h {job.estimated_duration_minutes % 60}m</span>
                    )}
                  </div>

                  {job.status === 'completed' && (
                    <Button 
                      className="w-full" 
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
