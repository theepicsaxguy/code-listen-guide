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
    <section className="px-6 py-24 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-4xl md:text-5xl font-bold">
            Sample Audiobooks
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Explore professionally generated audiobooks for popular open-source projects
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {samples.map((sample, index) => (
            <Card 
              key={index}
              className="p-6 bg-card/50 backdrop-blur-sm border-border hover:border-primary/50 transition-all duration-300 hover:shadow-glow group"
            >
              <div className="space-y-4">
                {/* Header */}
                <div>
                  <div className={`inline-block px-3 py-1 rounded-lg bg-gradient-to-r ${sample.color} text-sm font-medium mb-3`}>
                    {sample.repo}
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{sample.name}</h3>
                  <p className="text-sm text-muted-foreground">{sample.description}</p>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{sample.duration}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <BookOpen className="w-4 h-4" />
                    <span>{sample.chapters} chapters</span>
                  </div>
                </div>

                {/* Play button */}
                <Button 
                  variant="outline" 
                  className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
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
