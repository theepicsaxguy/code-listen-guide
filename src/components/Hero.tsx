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
      {/* Modern mesh gradient background */}
      <div className="absolute inset-0 mesh-gradient" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/25 via-transparent to-background" />

      {/* Animated floating orbs with vibrant colors */}
      <div className="absolute top-1/4 -left-64 w-[32rem] h-[32rem] bg-primary/40 rounded-full blur-[128px] animate-float" style={{ animationDelay: '0s', animationDuration: '8s' }} />
      <div className="absolute bottom-1/4 -right-64 w-[32rem] h-[32rem] bg-accent/35 rounded-full blur-[128px] animate-float" style={{ animationDelay: '2s', animationDuration: '10s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40rem] h-[40rem] bg-gradient-to-br from-primary/15 to-accent/15 rounded-full blur-[120px] animate-pulse" style={{ animationDuration: '6s' }} />

      {/* Additional accent orbs for depth */}
      <div className="absolute top-3/4 left-1/4 w-[24rem] h-[24rem] bg-success/20 rounded-full blur-[96px] animate-float" style={{ animationDelay: '4s', animationDuration: '12s' }} />
      <div className="absolute top-1/3 right-1/4 w-[28rem] h-[28rem] bg-warning/15 rounded-full blur-[100px] animate-float" style={{ animationDelay: '1s', animationDuration: '9s' }} />

      <div className="relative z-10 max-w-5xl mx-auto text-center space-y-10 animate-slide-up">
        {/* Enhanced Badge with glow */}
        <div className="inline-flex items-center gap-2.5 px-6 py-3 rounded-full glass hover-glow transition-all duration-300">
          <Sparkles className="w-4 h-4 text-accent animate-pulse" />
          <span className="text-sm font-medium gradient-text-accent">Transform any GitHub repo into an audiobook</span>
        </div>

        {/* Enhanced Main headline with vibrant gradients */}
        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-[1.1] tracking-tight px-4">
          <span className="block bg-gradient-to-br from-foreground via-foreground to-foreground/90 bg-clip-text text-transparent">
            Understand Code
          </span>
          <span className="block mt-3 gradient-text-accent animate-gradient bg-[length:200%_auto] drop-shadow-[0_0_30px_rgba(0,255,255,0.3)]">
            While You Commute
          </span>
        </h1>

        {/* Enhanced Subtitle with better contrast */}
        <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed px-4">
          Professional audiobooks that walk through every class, function, and design decision in any public repository. <span className="text-foreground font-medium">Learn deeply without screen time.</span>
        </p>

        {/* Enhanced GitHub URL input with modern styling */}
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-4">
          <div className="group flex flex-col sm:flex-row gap-3 p-2 glass rounded-2xl hover-glow transition-all duration-300">
            <div className="flex-1 relative">
              <Github className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-hover:text-accent transition-colors duration-300" />
              <Input
                type="url"
                placeholder="https://github.com/username/repository"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="pl-14 pr-4 h-16 bg-background/90 border-0 focus-visible:ring-2 focus-visible:ring-accent/50 rounded-xl text-base placeholder:text-muted-foreground/60"
              />
            </div>
            <Button
              type="submit"
              size="lg"
              className="h-16 px-12 bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_auto] hover:bg-right-bottom transition-all duration-500 shadow-[0_0_30px_rgba(138,43,226,0.4)] hover:shadow-[0_0_50px_rgba(0,255,255,0.5)] hover:scale-105 font-bold rounded-xl relative overflow-hidden group/btn"
            >
              <span className="relative z-10 flex items-center gap-2">
                Generate Audiobook
                <Sparkles className="w-4 h-4 group-hover/btn:animate-spin" />
              </span>
            </Button>
          </div>
        </form>

        {/* Enhanced Trust indicators with vibrant colors */}
        <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-12 pt-8 text-sm sm:text-base px-4">
          <div className="flex items-center gap-3 group hover-scale cursor-default">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-primary animate-pulse shadow-[0_0_10px_rgba(138,43,226,0.5)]" />
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-primary animate-ping opacity-75" />
            </div>
            <span className="text-muted-foreground group-hover:text-foreground transition-colors duration-300 font-medium">15-45 min generation</span>
          </div>
          <div className="flex items-center gap-3 group hover-scale cursor-default">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-accent animate-pulse shadow-[0_0_10px_rgba(0,255,255,0.5)]" style={{ animationDelay: '1s' }} />
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-accent animate-ping opacity-75" style={{ animationDelay: '1s' }} />
            </div>
            <span className="text-muted-foreground group-hover:text-foreground transition-colors duration-300 font-medium">20-50 chapters per book</span>
          </div>
          <div className="flex items-center gap-3 group hover-scale cursor-default">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-success animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]" style={{ animationDelay: '2s' }} />
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-success animate-ping opacity-75" style={{ animationDelay: '2s' }} />
            </div>
            <span className="text-foreground font-bold gradient-text-primary group-hover:scale-110 transition-transform duration-300">From $19</span>
          </div>
        </div>
      </div>
    </section>
  );
};
