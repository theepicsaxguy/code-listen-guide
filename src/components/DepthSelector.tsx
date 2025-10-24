import { Check } from "lucide-react";
import { Card } from "@/components/ui/card";

const depths = [
  {
    name: "Survey",
    duration: "2-4 hours",
    price: "$19",
    description: "High-level architecture, public APIs, key algorithms, primary data flows",
    features: [
      "Core architecture overview",
      "Public API documentation",
      "Key design patterns",
      "Main data flows"
    ],
    gradient: "from-blue-500/20 to-cyan-500/20"
  },
  {
    name: "Standard",
    duration: "6-10 hours",
    price: "$49",
    description: "All public interfaces, important private functions, design patterns, test structure",
    features: [
      "Complete public interfaces",
      "Important private functions",
      "Design pattern analysis",
      "Testing strategies",
      "Integration points"
    ],
    gradient: "from-primary/20 to-accent/20",
    popular: true
  },
  {
    name: "Comprehensive",
    duration: "15-25 hours",
    price: "$99",
    description: "Every function, every class, implementation details, edge cases, full test coverage",
    features: [
      "Complete code coverage",
      "Every function explained",
      "Implementation details",
      "Edge case handling",
      "Full test analysis",
      "Performance insights"
    ],
    gradient: "from-purple-500/20 to-pink-500/20"
  }
];

export const DepthSelector = () => {
  return (
    <section className="px-6 py-24 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-4xl md:text-5xl font-bold">
            Choose Your Depth
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From high-level overviews to comprehensive deep-dives, pick the level that matches your learning goals
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {depths.map((depth, index) => (
            <Card 
              key={index}
              className={`relative p-8 bg-card/50 backdrop-blur-sm border-border hover:border-primary/50 transition-all duration-300 hover:shadow-glow ${
                depth.popular ? 'scale-105 border-primary/50' : ''
              }`}
            >
              {depth.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-primary to-accent rounded-full text-sm font-medium">
                  Most Popular
                </div>
              )}
              
              <div className={`absolute inset-0 bg-gradient-to-br ${depth.gradient} rounded-xl opacity-50`} />
              
              <div className="relative space-y-6">
                <div>
                  <h3 className="text-2xl font-bold mb-2">{depth.name}</h3>
                  <div className="flex items-baseline gap-2 mb-4">
                    <span className="text-4xl font-bold text-primary">{depth.price}</span>
                    <span className="text-muted-foreground">/ {depth.duration}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{depth.description}</p>
                </div>

                <ul className="space-y-3">
                  {depth.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
