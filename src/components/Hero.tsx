import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Github, Sparkles } from "lucide-react";

export const Hero = () => {
  const [repoUrl, setRepoUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Repository URL:", repoUrl);
  };

  return (
    <section className="section-spacing">
      <div className="mx-auto flex max-w-content flex-col items-center gap-10 px-4 text-center sm:px-6">
        <div className="inline-flex items-center gap-2 rounded-full border-default bg-surface px-4 py-2 text-sm text-muted transition-standard">
          <Sparkles className="h-4 w-4 text-accent" aria-hidden="true" />
          <span className="font-medium text-foreground">Transform any GitHub repo into an audiobook</span>
        </div>

        <div className="space-y-4">
          <h1 className="text-balance text-4xl font-bold sm:text-5xl">Understand complex codebases without staring at a screen</h1>
          <p className="mx-auto max-w-2xl text-lg text-muted">
            Professional audiobooks that walk through every class, function, and design decision in any public repository. Learn deeply while you commute, walk the dog, or cook dinner.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="w-full max-w-2xl">
          <div className="flex flex-col gap-3 rounded-card border-default bg-surface p-4 elevation-flat sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Github className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted" aria-hidden="true" />
              <Input
                type="url"
                placeholder="https://github.com/username/repository"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="pl-11"
              />
            </div>
            <Button type="submit" size="lg" className="w-full sm:w-auto transition-standard">
              Generate Audiobook
            </Button>
          </div>
        </form>

        <dl className="grid w-full max-w-3xl grid-cols-1 gap-6 text-left sm:grid-cols-3">
          <div className="rounded-card border-default bg-surface p-4">
            <dt className="text-sm text-muted">Production time</dt>
            <dd className="mt-2 text-2xl font-semibold text-foreground">15–45 minutes</dd>
          </div>
          <div className="rounded-card border-default bg-surface p-4">
            <dt className="text-sm text-muted">Chapters per book</dt>
            <dd className="mt-2 text-2xl font-semibold text-foreground">20–50 chapters</dd>
          </div>
          <div className="rounded-card border-default bg-surface p-4">
            <dt className="text-sm text-muted">Pricing starts at</dt>
            <dd className="mt-2 text-2xl font-semibold text-primary">$19</dd>
          </div>
        </dl>
      </div>
    </section>
  );
};
