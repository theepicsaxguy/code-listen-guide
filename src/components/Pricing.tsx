import { Check, Sparkles, Zap, Crown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

const tiers = [
  {
    name: "Survey",
    icon: Sparkles,
    price: 19,
    description: "Perfect for exploring new codebases",
    features: [
      "15-30 min generation time",
      "10-20 chapters",
      "Standard voice quality",
      "Basic code analysis",
      "1-2 hour audio length",
      "Download MP3"
    ],
    gradient: "from-blue-500 to-cyan-400",
    popular: false
  },
  {
    name: "Standard",
    icon: Zap,
    price: 39,
    description: "Best for comprehensive understanding",
    features: [
      "25-40 min generation time",
      "25-40 chapters",
      "Premium voice quality",
      "Deep code analysis",
      "3-5 hour audio length",
      "Download MP3",
      "Chapter navigation",
      "Variable playback speed"
    ],
    gradient: "from-primary to-accent",
    popular: true
  },
  {
    name: "Comprehensive",
    icon: Crown,
    price: 69,
    description: "Ultimate deep dive into complex projects",
    features: [
      "35-50 min generation time",
      "40-60 chapters",
      "Ultra premium voices",
      "Expert-level analysis",
      "6-10 hour audio length",
      "Download MP3",
      "Chapter navigation",
      "Variable playback speed",
      "Code synchronization",
      "Priority generation"
    ],
    gradient: "from-purple-500 to-pink-400",
    popular: false
  }
];

export const Pricing = () => {
  const navigate = useNavigate();

  return (
    <section className="px-6 py-24 relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/10 to-transparent" />
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] animate-float" style={{ animationDuration: '20s' }} />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/15 rounded-full blur-[120px] animate-float" style={{ animationDuration: '25s', animationDelay: '3s' }} />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-4xl md:text-5xl font-bold">
            Simple, <span className="gradient-text-accent">Transparent</span> Pricing
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose the depth that matches your learning goals
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {tiers.map((tier, index) => {
            const Icon = tier.icon;
            return (
              <Card
                key={index}
                className={`p-8 bg-card transition-all duration-500 hover-lift relative overflow-hidden group ${
                  tier.popular ? 'scale-105' : ''
                }`}
              >
                {/* Popular badge */}
                {tier.popular && (
                  <div className="absolute top-0 right-0 bg-gradient-to-r from-primary to-accent px-6 py-2 rounded-bl-2xl">
                    <span className="text-xs font-bold text-primary-foreground">MOST POPULAR</span>
                  </div>
                )}

                {/* Hover gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="relative z-10 space-y-6">
                  {/* Icon & Name */}
                  <div className="space-y-4">
                    <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${tier.gradient} p-[2px] hover:shadow-lg`}>
                      <div className="w-full h-full rounded-lg bg-background flex items-center justify-center">
                        <Icon className="w-8 h-8 text-primary" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                      <p className="text-sm text-muted-foreground">{tier.description}</p>
                    </div>
                  </div>

                  {/* Price */}
                  <div className="py-4">
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-bold gradient-text-primary">${tier.price}</span>
                      <span className="text-muted-foreground">/ audiobook</span>
                    </div>
                  </div>

                  {/* Features */}
                  <ul className="space-y-3">
                    {tier.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-3">
                        <div className="mt-0.5">
                          <Check className="w-5 h-5 text-success" />
                        </div>
                        <span className="text-sm text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <Button
                    onClick={() => navigate('/auth')}
                    className={`w-full h-12 font-bold transition-all duration-300 ${
                      tier.popular
                        ? 'bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_auto] hover:bg-right-bottom shadow-[0_0_30px_rgba(138,43,226,0.4)] hover:shadow-[0_0_50px_rgba(0,255,255,0.5)] hover:scale-105'
                        : 'bg-secondary hover:bg-gradient-to-r hover:from-primary hover:to-accent hover-scale'
                    }`}
                  >
                    Get Started
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Additional info */}
        <div className="text-center mt-12 space-y-4">
          <p className="text-sm text-muted-foreground">
            All plans include unlimited access to your generated audiobooks
          </p>
          <div className="flex items-center justify-center gap-6 text-xs text-muted-foreground">
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4 text-success" />
              No monthly fees
            </span>
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4 text-success" />
              Pay per audiobook
            </span>
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4 text-success" />
              Lifetime access
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
