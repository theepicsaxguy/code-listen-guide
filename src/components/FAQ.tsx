import { useState } from "react";
import { ChevronDown, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const faqs = [
  {
    question: "How long does it take to generate an audiobook?",
    answer:
      "Generation time varies by tier: Survey (15-30 min), Standard (25-40 min), Comprehensive (35-50 min). We'll email you when it's ready!",
    category: "general",
  },
  {
    question: "What programming languages do you support?",
    answer:
      "We support all major languages including JavaScript, TypeScript, Python, Java, Go, Rust, C++, and many more. Our AST parser handles polyglot repositories seamlessly.",
    category: "technical",
  },
  {
    question: "Can I use this for private repositories?",
    answer:
      "Currently we only support public GitHub repositories. Private repository support is coming soon! Join our waitlist to be notified.",
    category: "technical",
  },
  {
    question: "What's included in the audio?",
    answer:
      "Each audiobook includes: architectural overview, file-by-file walkthrough, function explanations, design pattern analysis, and key insights about the codebase structure.",
    category: "content",
  },
  {
    question: "Can I download the audiobook?",
    answer:
      "Yes! All tiers include MP3 downloads. You can listen offline anytime on your favorite audio player.",
    category: "general",
  },
  {
    question: "How accurate is the code analysis?",
    answer:
      "We use frontier LLMs (GPT-4, Claude) combined with static analysis tools like tree-sitter. Our accuracy is reviewed by senior engineers and continuously improved.",
    category: "technical",
  },
  {
    question: "What if I'm not satisfied?",
    answer:
      "We offer a 100% satisfaction guarantee. If you're not happy with the quality within 7 days, we'll refund you completely—no questions asked.",
    category: "billing",
  },
  {
    question: "Do you offer team/enterprise plans?",
    answer:
      "Yes! Contact us for bulk pricing, custom voice options, priority generation, and dedicated support for teams.",
    category: "billing",
  },
  {
    question: "How is this different from reading documentation?",
    answer:
      "Unlike docs, we explain the actual implementation. You get architectural insights, design decisions, and code flow—all while you're commuting, exercising, or doing chores.",
    category: "content",
  },
  {
    question: "Can I request updates when the repository changes?",
    answer:
      "Absolutely! You can regenerate audiobooks for the same repo at a 50% discount to stay up-to-date with the latest changes.",
    category: "general",
  },
];

export const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredFaqs = faqs.filter(
    (faq) =>
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <section className="relative px-6 py-24 overflow-hidden">
      {/* Radial gradient accent */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="mx-auto max-w-content px-4 sm:px-6 relative z-10">
        <div className="mb-12 space-y-4 text-center">
          <h2 className="text-balance text-3xl font-bold text-foreground leading-tight sm:text-4xl">Frequently asked questions</h2>
          <p className="mx-auto max-w-2xl text-base leading-relaxed text-muted-foreground">
            Everything you need to know about how Codebase Audiobook works and what to expect.
          </p>
        </div>

        <div className="mb-8">
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted" aria-hidden="true" />
            <Input
              type="text"
              placeholder="Search questions"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12"
            />
          </div>
        </div>

        <div className="space-y-3">
          {filteredFaqs.length > 0 ? (
            filteredFaqs.map((faq, index) => {
              const isOpen = openIndex === index;
              return (
                <Card key={faq.question} className="transition-standard hover:shadow-xl hover:shadow-primary/10">
                  <button
                    type="button"
                    onClick={() => setOpenIndex(isOpen ? null : index)}
                    className="flex w-full items-center justify-between gap-4 px-6 py-4 text-left transition-standard hover:bg-surface-secondary"
                    aria-expanded={isOpen}
                  >
                    <span className="text-base font-semibold text-foreground">{faq.question}</span>
                    <ChevronDown
                      className={`h-5 w-5 text-primary transition-standard shrink-0 ${isOpen ? "rotate-180" : ""}`}
                      aria-hidden="true"
                    />
                  </button>
                  {isOpen ? (
                    <div className="px-6 pb-4 text-sm leading-relaxed text-muted-foreground">
                      {faq.answer}
                    </div>
                  ) : null}
                </Card>
              );
            })
          ) : (
            <Card className="px-6 py-12 text-center">
              <p className="text-base text-muted-foreground">
                No questions found matching "{searchQuery}"
              </p>
            </Card>
          )}
        </div>

        <Card className="mt-12 p-8 text-center hover:shadow-xl hover:shadow-primary/10 transition-standard">
          <h3 className="text-xl font-semibold text-foreground">Still have questions?</h3>
          <p className="mt-2 text-base text-muted-foreground">
            Can't find the answer you're looking for? Our support team is ready to help.
          </p>
          <Button asChild variant="outline" className="mt-4">
            <a href="mailto:support@codebaseaudiobook.com">Contact support</a>
          </Button>
        </Card>
      </div>
    </section>
  );
};
