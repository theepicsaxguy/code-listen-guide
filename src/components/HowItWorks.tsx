import { Code2, FileText, Headphones, Sparkles } from "lucide-react";

const steps = [
  {
    icon: Code2,
    title: "Repository Analysis",
    description: "We parse your codebase using tree-sitter AST generation, build dependency graphs, and identify key architectural patterns.",
    gradient: "from-primary to-accent",
    iconColor: "text-primary"
  },
  {
    icon: FileText,
    title: "Script Generation",
    description: "Frontier LLMs create comprehensive, technically accurate narratives that explain every class, function, and design decision.",
    gradient: "from-primary to-accent",
    iconColor: "text-primary"
  },
  {
    icon: Sparkles,
    title: "Audio Synthesis",
    description: "State-of-the-art TTS models generate professional narration with proper technical pronunciation and natural pacing.",
    gradient: "from-secondary to-accent",
    iconColor: "text-secondary"
  },
  {
    icon: Headphones,
    title: "Listen & Learn",
    description: "Stream your audiobook with chapter navigation, variable playback speed, and code sync. Learn while you commute, exercise, or relax.",
    gradient: "from-success to-accent",
    iconColor: "text-success"
  }
];

export const HowItWorks = () => {
  return (
    <section className="relative px-6 py-24 overflow-hidden">
      {/* Radial gradient accent */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-3xl font-bold text-foreground leading-tight sm:text-4xl">
            How It <span className="text-primary">Works</span>
          </h2>
          <p className="text-base leading-relaxed text-muted-foreground max-w-2xl mx-auto">
            From code to comprehension in four seamless steps
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="relative group">
                {/* Connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-20 left-full w-full h-[2px] bg-gradient-to-r from-primary/40 via-transparent to-transparent -z-10" />
                )}

                <div className="space-y-6">
                  {/* Icon container with glow */}
                  <div className="relative">
                    <div className={`relative w-20 h-20 bg-surface p-[2px] shadow-lg shadow-primary/10 hover:shadow-xl hover:shadow-primary/15 transition-standard`}>
                      <div className="w-full h-full bg-background flex items-center justify-center">
                        <Icon className={`w-10 h-10 ${step.iconColor}`} />
                      </div>
                    </div>
                    {/* Step number badge */}
                    <div className="absolute -top-2 -right-2 w-10 h-10 rounded-full bg-primary flex items-center justify-center text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20">
                      {index + 1}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold mb-3 text-foreground group-hover:text-primary transition-standard">{step.title}</h3>
                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
