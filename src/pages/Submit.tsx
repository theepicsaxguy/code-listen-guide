import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { ArrowLeft, Github, Loader2 } from 'lucide-react';
import { DepthSelector } from '@/components/DepthSelector';
import { DepthTier } from '@/lib/types';

export default function Submit() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [gitRef, setGitRef] = useState('main');
  const [selectedDepth, setSelectedDepth] = useState<DepthTier>('standard');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user) {
      navigate('/auth');
      return;
    }

    // Navigate to repository preview instead of creating job directly
    navigate('/repository-preview', {
      state: {
        repoUrl,
        gitRef,
        selectedDepth,
      },
    });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Radial gradient accent */}
      <div className="fixed inset-0 bg-linear-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <header className="relative z-10 bg-surface">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl relative z-10">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-4 text-foreground sm:text-4xl">Create New Audiobook</h1>
          <p className="text-base leading-relaxed text-muted-foreground">
            Transform any GitHub repository into a comprehensive audio walkthrough
          </p>
        </div>

        <Card className="hover:shadow-xl hover:shadow-primary/10 transition-standard">
          <CardHeader>
            <CardTitle className="text-xl font-semibold">Repository Details</CardTitle>
            <CardDescription className="text-sm text-muted-foreground">Enter the GitHub repository you want to convert</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-8">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="repo-url" className="text-sm font-medium text-foreground">
                    <Github className="inline mr-2 h-4 w-4" />
                    Repository URL
                  </Label>
                  <Input
                    id="repo-url"
                    placeholder="https://github.com/owner/repository"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    required
                  />
                  <p className="text-sm text-muted-foreground">
                    Public GitHub repositories only
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="git-ref" className="text-sm font-medium text-foreground">Branch / Tag / Commit (optional)</Label>
                  <Input
                    id="git-ref"
                    placeholder="main"
                    value={gitRef}
                    onChange={(e) => setGitRef(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <Label className="text-sm font-medium text-foreground">Select Depth Tier</Label>
                <DepthSelector selectedDepth={selectedDepth} onDepthChange={setSelectedDepth} />
              </div>

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => navigate('/dashboard')}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button type="submit" className="flex-1" disabled={isLoading || !repoUrl}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    'Preview Repository'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
