import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const stats = [
  {
    value: "26.3M+",
    label: "Professional developers worldwide"
  },
  {
    value: "~500M",
    label: "People who regularly listen to podcasts"
  },
  {
    value: "16-26%",
    label: "Average lift in test scores from audio learning studies"
  }
];

const sections = [
  {
    title: "Market Demand for Codebase Audiobook",
    description:
      "Developers spend hours each week parsing unfamiliar repositories and juggling documentation tabs. Audio tours let them keep learning while commuting, exercising, or handling life outside the keyboard.",
    bullets: [
      "Developers already adopt on-the-go learning habits through podcasts and audiobooks.",
      "Visual-first tutorials do not translate to screen-free situations, leaving a gap that a dedicated code audiobook can fill.",
      "Narrated walkthroughs can deliver architecture, patterns, and implementation details without requiring a monitor."
    ]
  },
  {
    title: "Developer Learning Pain Points",
    description:
      "Onboarding documents drift out of date and video walkthroughs force constant screen time. Teams crave a reliable, passive way to hear how codebases actually fit together.",
    bullets: [
      "Engineers regularly cite code comprehension as their slowest onboarding task.",
      "Documentation generators focus on API references instead of storytelling across modules.",
      "Audio lets teams absorb repository structure while doing everyday tasks."
    ]
  },
  {
    title: "Audio Learning Trends",
    description:
      "Podcasting has matured into a mainstream medium with proven educational impact, even for highly technical audiences.",
    bullets: [
      "Millions of shows now serve audiences that expect polished, serialized content.",
      "Medical education research shows listeners can retain up to 100% of the presented material.",
      "Developers are already comfortable with podcasts for news and deep dives, making the format familiar."
    ]
  },
  {
    title: "Market Size & Segments",
    description:
      "A small slice of the global developer population represents a massive audience for narrated code tours.",
    bullets: [
      "Senior engineers onboarding to new repos and platform teams reviewing partner code.",
      "Students and bootcamp graduates seeking real-world examples that go beyond toy projects.",
      "Any public GitHub repository can become a new title, giving the library endless room to expand."
    ]
  },
  {
    title: "Competitive Landscape",
    description:
      "No incumbent offers structured, audio-first journeys through codebases, leaving room for a differentiated product.",
    bullets: [
      "Static docs and READMEs explain APIs but skip narrative context.",
      "Video walkthroughs demand full attention and are hard to revisit while on the move.",
      "AI chatbots answer point questions yet cannot deliver cohesive, multi-hour tours." 
    ]
  },
  {
    title: "Conclusion",
    description:
      "Audio-native explanations unlock a new way to understand complex software. Codebase Audiobook can meet developers where they already learn and fit into their real lives.",
    bullets: [
      "The pool of potential listeners is enormous and under-served.",
      "Audio learning is already trusted to deliver technical material.",
      "Launching now positions the product as the first mover in an open niche."
    ]
  }
];

export const MarketValidation = () => {
  return (
    <section className="px-6 py-24 bg-secondary/10">
      <div className="max-w-6xl mx-auto space-y-16">
        <div className="text-center space-y-6">
          <div className="inline-flex flex-wrap items-center justify-center gap-3">
            {stats.map((stat) => (
              <Badge key={stat.label} variant="secondary" className="px-4 py-2 text-sm">
                <span className="font-semibold text-foreground">{stat.value}</span>
                <span className="ml-2 text-muted-foreground">{stat.label}</span>
              </Badge>
            ))}
          </div>
          <div className="space-y-4">
            <h2 className="text-4xl md:text-5xl font-bold">Why Developers Want Audio Tours</h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Each data point tells the same story: developers need a screen-free way to absorb new repositories. These insights explain why Codebase Audiobook exists and how we shape the roadmap.
            </p>
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {sections.map((section) => (
            <Card key={section.title} className="p-6 h-full flex flex-col gap-4 bg-card/70">
              <div>
                <h3 className="text-2xl font-semibold mb-2">{section.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{section.description}</p>
              </div>
              <ul className="space-y-3 text-sm text-foreground/80">
                {section.bullets.map((bullet) => (
                  <li key={bullet} className="flex gap-2">
                    <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" />
                    <span className="leading-relaxed">{bullet}</span>
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

