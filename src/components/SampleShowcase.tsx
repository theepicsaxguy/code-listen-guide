import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Clock, BookOpen } from "lucide-react";

const samples = [
  {
    name: "React",
    repo: "facebook/react",
    duration: "18h 32m",
    chapters: 42,
    description: "Deep dive into React's reconciliation algorithm, fiber architecture, and hooks implementation",
    color: "from-blue-500 to-cyan-500"
  },
  {
    name: "Express",
    repo: "expressjs/express",
    duration: "6h 45m",
    chapters: 28,
    description: "Complete walkthrough of middleware pipeline, routing engine, and request handling",
    color: "from-primary to-accent"
  },
  {
    name: "Django",
    repo: "django/django",
    duration: "24h 18m",
    chapters: 56,
    description: "Comprehensive tour of ORM implementation, template engine, and admin interface",
    color: "from-green-500 to-emerald-500"
  }
];

export const SampleShowcase = () => {
  return (
    <section className="px-6 py-24 relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-accent/5 to-transparent" />
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-accent/10 rounded-full blur-[100px] animate-float" style={{ animationDuration: '15s' }} />
      <div className="absolute top-1/4 right-0 w-96 h-96 bg-primary/10 rounded-full blur-[100px] animate-float" style={{ animationDuration: '18s', animationDelay: '2s' }} />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-4xl md:text-5xl font-bold">
            Sample <span className="gradient-text-accent">Audiobooks</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Explore professionally generated audiobooks for popular open-source projects
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {samples.map((sample, index) => (
            <Card
              key={index}
              className="p-8 glass hover:border-primary/50 transition-all duration-300 hover-lift group overflow-hidden relative"
            >
              {/* Gradient overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <div className="space-y-5 relative z-10">
                {/* Header */}
                <div>
                  <div className={`inline-block px-4 py-1.5 rounded-lg bg-gradient-to-r ${sample.color} text-sm font-bold mb-4 shadow-lg`}>
                    {sample.repo}
                  </div>
                  <h3 className="text-2xl font-bold mb-3 group-hover:gradient-text-primary transition-all duration-300">{sample.name}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{sample.description}</p>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-6 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-accent" />
                    <span className="font-medium">{sample.duration}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    <span className="font-medium">{sample.chapters} chapters</span>
                  </div>
                </div>

                {/* Play button */}
                <Button
                  variant="outline"
                  className="w-full group-hover:bg-gradient-to-r group-hover:from-primary group-hover:to-accent group-hover:text-primary-foreground group-hover:border-transparent transition-all duration-300 hover-scale font-semibold"
                >
                  <Play className="w-4 h-4 mr-2 group-hover:animate-pulse" />
                  Listen to Sample
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
