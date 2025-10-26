import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Github, Sparkles } from "lucide-react";

export const Hero = () => {
  const [repoUrl, setRepoUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Note: Wire this up to jobs API when backend is ready
    console.log("Repository URL:", repoUrl);
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 py-24 pt-32 md:pt-24 overflow-hidden">
      {/* Enhanced gradient background effects */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />
      <div className="absolute top-1/4 -left-64 w-[32rem] h-[32rem] bg-primary/30 rounded-full blur-[128px] animate-pulse" style={{ animationDuration: '8s' }} />
      <div className="absolute bottom-1/4 -right-64 w-[32rem] h-[32rem] bg-accent/25 rounded-full blur-[128px] animate-pulse" style={{ animationDuration: '10s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40rem] h-[40rem] bg-gradient-to-br from-primary/10 to-accent/10 rounded-full blur-[120px]" />

      <div className="relative z-10 max-w-5xl mx-auto text-center space-y-10">
        {/* Enhanced Badge */}
        <div className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full bg-card/80 border border-primary/20 backdrop-blur-md shadow-lg shadow-primary/10 hover:shadow-xl hover:shadow-primary/20 transition-all duration-300">
          <Sparkles className="w-4 h-4 text-primary animate-pulse" />
          <span className="text-sm font-medium bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">Transform any GitHub repo into an audiobook</span>
        </div>

        {/* Enhanced Main headline with better typography */}
        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-[1.1] tracking-tight px-4">
          <span className="block bg-gradient-to-br from-foreground via-foreground/95 to-foreground/80 bg-clip-text text-transparent">
            Understand Code
          </span>
          <span className="block mt-2 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
            While You Commute
          </span>
        </h1>

        {/* Enhanced Subtitle with better contrast */}
        <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground/90 max-w-3xl mx-auto leading-relaxed px-4 font-light">
          Professional audiobooks that walk through every class, function, and design decision in any public repository. <span className="text-foreground/80 font-normal">Learn deeply without screen time.</span>
        </p>

        {/* Enhanced GitHub URL input */}
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-4">
          <div className="group flex flex-col sm:flex-row gap-3 p-1.5 bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl shadow-2xl shadow-primary/5 hover:shadow-primary/10 hover:border-primary/30 transition-all duration-300">
            <div className="flex-1 relative">
              <Github className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors duration-300" />
              <Input
                type="url"
                placeholder="https://github.com/username/repository"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="pl-14 pr-4 h-14 bg-background/80 border-0 focus-visible:ring-2 focus-visible:ring-primary/50 rounded-xl text-base placeholder:text-muted-foreground/60"
              />
            </div>
            <Button
              type="submit"
              size="lg"
              className="h-14 px-10 bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_auto] hover:bg-right-bottom transition-all duration-500 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/40 hover:scale-[1.02] font-semibold rounded-xl"
            >
              Generate Audiobook
            </Button>
          </div>
        </form>

        {/* Enhanced Trust indicators */}
        <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-10 pt-6 text-sm sm:text-base px-4">
          <div className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-primary animate-ping opacity-75" />
            </div>
            <span className="text-muted-foreground group-hover:text-foreground transition-colors duration-300">15-45 min generation</span>
          </div>
          <div className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse" style={{ animationDelay: '1s' }} />
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-accent animate-ping opacity-75" style={{ animationDelay: '1s' }} />
            </div>
            <span className="text-muted-foreground group-hover:text-foreground transition-colors duration-300">20-50 chapters per book</span>
          </div>
          <div className="flex items-center gap-3 group">
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" style={{ animationDelay: '2s' }} />
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-primary animate-ping opacity-75" style={{ animationDelay: '2s' }} />
            </div>
            <span className="text-foreground/90 font-semibold group-hover:text-primary transition-colors duration-300">From $19</span>
          </div>
        </div>
      </div>
    </section>
  );
};
