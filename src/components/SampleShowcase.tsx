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
    color: "from-success to-accent"
  }
];

export const SampleShowcase = () => {
  return (
    <section className="relative px-6 py-24 overflow-hidden">
      {/* Radial gradient accents */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-3xl font-bold text-foreground leading-tight sm:text-4xl">
            Sample <span className="text-primary">Audiobooks</span>
          </h2>
          <p className="text-base leading-relaxed text-muted-foreground max-w-2xl mx-auto">
            Explore professionally generated audiobooks for popular open-source projects
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {samples.map((sample, index) => (
            <Card
              key={index}
              className="p-6 group overflow-hidden relative hover:shadow-xl hover:shadow-primary/10 transition-standard"
            >
              {/* Gradient overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

              <div className="space-y-5 relative z-10">
                {/* Header */}
                <div>
                  <div className={`inline-block px-4 py-1.5 bg-surface text-sm font-semibold text-foreground mb-4`}>
                    {sample.repo}
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-foreground group-hover:text-primary transition-standard">{sample.name}</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">{sample.description}</p>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-6 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-primary" />
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
                  className="w-full group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary transition-standard font-semibold"
                >
                  <Play className="w-4 h-4 mr-2" />
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
