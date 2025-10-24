import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Github, Sparkles } from "lucide-react";

export const Hero = () => {
  const [repoUrl, setRepoUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Handle repository URL submission
    console.log("Repository URL:", repoUrl);
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 py-24 overflow-hidden">
      {/* Gradient background effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10" />
      <div className="absolute top-1/4 -left-48 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 -right-48 w-96 h-96 bg-accent/20 rounded-full blur-3xl" />
      
      <div className="relative z-10 max-w-4xl mx-auto text-center space-y-8">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 border border-border backdrop-blur-sm">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="text-sm text-muted-foreground">Transform any GitHub repo into an audiobook</span>
        </div>

        {/* Main headline */}
        <h1 className="text-5xl md:text-7xl font-bold leading-tight">
          <span className="bg-gradient-to-r from-foreground via-foreground to-muted-foreground bg-clip-text text-transparent">
            Understand Code
          </span>
          <br />
          <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
            While You Commute
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Professional audiobooks that walk through every class, function, and design decision in any public repository. Learn deeply without screen time.
        </p>

        {/* GitHub URL input */}
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
          <div className="flex flex-col sm:flex-row gap-3 p-3 bg-secondary/30 backdrop-blur-sm border border-border rounded-2xl shadow-soft">
            <div className="flex-1 relative">
              <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="url"
                placeholder="https://github.com/username/repository"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="pl-12 h-12 bg-background/50 border-border/50 focus-visible:ring-primary"
              />
            </div>
            <Button 
              type="submit" 
              size="lg"
              className="h-12 px-8 bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-opacity"
            >
              Generate Audiobook
            </Button>
          </div>
        </form>

        {/* Trust indicators */}
        <div className="flex flex-wrap items-center justify-center gap-8 pt-8 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span>15-45 min generation</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span>20-50 chapters per book</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span>From $19</span>
          </div>
        </div>
      </div>
    </section>
  );
};
