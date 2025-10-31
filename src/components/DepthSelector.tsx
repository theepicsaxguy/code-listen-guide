import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";
import { DepthTier } from "@/lib/types";

const depthTiers = [
  {
    id: "survey" as DepthTier,
    name: "Survey",
    duration: "2-4 hours",
    price: "$69",
    features: ["High-level architecture overview", "Public APIs and interfaces", "Key algorithms and patterns", "Primary data flows", "10-15 chapters"]
  },
  {
    id: "standard" as DepthTier,
    name: "Standard",
    duration: "6-10 hours",
    price: "$149",
    popular: true,
    features: ["All public interfaces explained", "Important private functions", "Design patterns and decisions", "Test structure overview", "25-35 chapters"]
  },
  {
    id: "comprehensive" as DepthTier,
    name: "Comprehensive",
    duration: "15-25 hours",
    price: "$299",
    features: ["Every function explained", "Complete implementation details", "Edge cases and error handling", "Full test coverage walkthrough", "40-60 chapters"]
  }
];

interface DepthSelectorProps {
  selectedDepth: DepthTier;
  onDepthChange: (depth: DepthTier) => void;
}

export function DepthSelector({ selectedDepth, onDepthChange }: DepthSelectorProps) {
  return (
    <div className="grid md:grid-cols-3 gap-6 w-full">
      {depthTiers.map((tier) => (
        <Card key={tier.id} className={`relative hover-scale cursor-pointer transition-all ${tier.popular ? 'shadow-lg' : ''} ${selectedDepth === tier.id ? 'ring-2 ring-primary' : ''}`} onClick={() => onDepthChange(tier.id)}>
          {tier.popular && <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">Most Popular</Badge>}
          <CardHeader>
            <CardTitle className="text-2xl">{tier.name}</CardTitle>
            <CardDescription className="text-lg font-semibold text-foreground">{tier.price}</CardDescription>
            <p className="text-sm text-muted-foreground">{tier.duration}</p>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {tier.features.map((feature, index) => (
                <li key={index} className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                  <span className="text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
