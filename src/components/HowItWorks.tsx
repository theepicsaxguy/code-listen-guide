import { Code2, FileText, Headphones, Sparkles } from "lucide-react";

const steps = [
  {
    icon: Code2,
    title: "Repository Analysis",
    description: "We parse your codebase using tree-sitter AST generation, build dependency graphs, and identify key architectural patterns.",
    gradient: "from-blue-500 to-cyan-400",
    iconColor: "text-blue-400"
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
    gradient: "from-purple-500 to-pink-400",
    iconColor: "text-purple-400"
  },
  {
    icon: Headphones,
    title: "Listen & Learn",
    description: "Stream your audiobook with chapter navigation, variable playback speed, and code sync. Learn while you commute, exercise, or relax.",
    gradient: "from-green-400 to-emerald-400",
    iconColor: "text-success"
  }
];

export const HowItWorks = () => {
  return (
    <section className="px-6 py-24 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-4xl md:text-5xl font-bold">
            How It <span className="gradient-text-primary">Works</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From code to comprehension in four seamless steps
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="relative group">
                {/* Enhanced connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-20 left-full w-full h-[2px] bg-gradient-to-r from-primary/40 via-accent/30 to-transparent -z-10" />
                )}

                <div className="space-y-6 hover-lift">
                  {/* Enhanced icon container with glow */}
                  <div className="relative">
                    <div className={`relative w-20 h-20 rounded-2xl bg-gradient-to-br ${step.gradient} p-[2px] hover-glow transition-all duration-300`}>
                      <div className="w-full h-full rounded-2xl bg-background flex items-center justify-center">
                        <Icon className={`w-10 h-10 ${step.iconColor}`} />
                      </div>
                    </div>
                    {/* Enhanced step number badge */}
                    <div className="absolute -top-2 -right-2 w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-sm font-bold shadow-lg shadow-primary/30">
                      {index + 1}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold mb-3 group-hover:text-primary transition-colors duration-300">{step.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
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
