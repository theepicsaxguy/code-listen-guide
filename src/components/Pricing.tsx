import { Check, Crown, Sparkles, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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
      "Baseline code analysis",
      "1-2 hour audio length",
      "Downloadable MP3",
    ],
    popular: false,
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
      "Downloadable MP3",
      "Chapter navigation",
      "Variable playback speed",
    ],
    popular: true,
  },
  {
    name: "Comprehensive",
    icon: Crown,
    price: 69,
    description: "Ultimate deep dive into complex projects",
    features: [
      "35-50 min generation time",
      "40-60 chapters",
      "Expert voice talent",
      "Expert-level analysis",
      "6-10 hour audio length",
      "Downloadable MP3",
      "Chapter navigation",
      "Variable playback speed",
      "Code synchronization",
      "Priority generation",
    ],
    popular: false,
  },
];

export const Pricing = () => {
  const navigate = useNavigate();

  return (
    <section className="section-spacing bg-background">
      <div className="mx-auto max-w-content px-4 sm:px-6">
        <div className="mb-12 space-y-4 text-center">
          <h2 className="text-balance text-heading font-semibold">Simple, transparent pricing</h2>
          <p className="mx-auto max-w-2xl text-body text-muted-foreground">
            Choose the depth that matches your learning goals. Every plan includes high quality narration and downloadable audio files.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {tiers.map((tier) => {
            const Icon = tier.icon;
            return (
              <Card
                key={tier.name}
                className={`flex h-full flex-col gap-6 p-6 transition-standard ${tier.popular ? "shadow-lg border-2 border-primary/20" : "shadow-sm hover:shadow-md"}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-secondary shadow-sm">
                      <Icon className="h-6 w-6 text-primary" aria-hidden="true" />
                    </span>
                    <div>
                      <h3 className="text-subheading font-semibold text-foreground">{tier.name}</h3>
                      <p className="text-body-sm text-muted-foreground">{tier.description}</p>
                    </div>
                  </div>
                  {tier.popular ? <Badge variant="outline">Most popular</Badge> : null}
                </div>

                <div className="flex items-baseline gap-2">
                  <span className="text-display font-bold text-foreground">${tier.price}</span>
                  <span className="text-body-sm text-muted-foreground">per audiobook</span>
                </div>

                <ul className="flex flex-1 flex-col gap-3 text-body-sm text-muted-foreground">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-left">
                      <Check className="mt-0.5 h-5 w-5 text-success" aria-hidden="true" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => navigate("/auth")}
                  className="w-full transition-standard"
                  variant={tier.popular ? "default" : "secondary"}
                >
                  Get started
                </Button>
              </Card>
            );
          })}
        </div>

        <div className="mt-12 space-y-4 text-center">
          <p className="text-body-sm text-muted-foreground">All plans include unlimited access to your generated audiobooks.</p>
          <div className="flex flex-wrap items-center justify-center gap-4 text-caption text-muted-foreground">
            <span className="flex items-center gap-2">
              <Check className="h-4 w-4 text-success" aria-hidden="true" />
              No monthly fees
            </span>
            <span className="flex items-center gap-2">
              <Check className="h-4 w-4 text-success" aria-hidden="true" />
              Pay per audiobook
            </span>
            <span className="flex items-center gap-2">
              <Check className="h-4 w-4 text-success" aria-hidden="true" />
              Lifetime access
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
