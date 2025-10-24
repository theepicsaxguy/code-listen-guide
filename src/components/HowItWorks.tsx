import { Code2, FileText, Headphones, Sparkles } from "lucide-react";

const steps = [
  {
    icon: Code2,
    title: "Repository Analysis",
    description: "We parse your codebase using tree-sitter AST generation, build dependency graphs, and identify key architectural patterns.",
    gradient: "from-blue-500 to-cyan-500"
  },
  {
    icon: FileText,
    title: "Script Generation",
    description: "Frontier LLMs create comprehensive, technically accurate narratives that explain every class, function, and design decision.",
    gradient: "from-primary to-accent"
  },
  {
    icon: Sparkles,
    title: "Audio Synthesis",
    description: "State-of-the-art TTS models generate professional narration with proper technical pronunciation and natural pacing.",
    gradient: "from-purple-500 to-pink-500"
  },
  {
    icon: Headphones,
    title: "Listen & Learn",
    description: "Stream your audiobook with chapter navigation, variable playback speed, and code sync. Learn while you commute, exercise, or relax.",
    gradient: "from-green-500 to-emerald-500"
  }
];

export const HowItWorks = () => {
  return (
    <section className="px-6 py-24 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-4xl md:text-5xl font-bold">
            How It Works
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From code to comprehension in four seamless steps
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="relative group">
                {/* Connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-border to-transparent -z-10" />
                )}
                
                <div className="space-y-4">
                  <div className={`relative w-16 h-16 rounded-2xl bg-gradient-to-br ${step.gradient} p-0.5`}>
                    <div className="w-full h-full rounded-2xl bg-background flex items-center justify-center">
                      <Icon className="w-8 h-8 text-primary" />
                    </div>
                    <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-secondary border border-border flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-xl font-bold mb-2">{step.title}</h3>
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
