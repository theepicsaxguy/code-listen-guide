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
    <section className="section-spacing bg-background">
      <div className="mx-auto max-w-content px-4 sm:px-6">
        <div className="mb-12 space-y-4 text-center">
          <h2 className="text-balance text-3xl font-semibold sm:text-4xl">Frequently asked questions</h2>
          <p className="mx-auto max-w-2xl text-muted">
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
                <div key={faq.question} className="rounded-lg border-default bg-surface">
                  <button
                    type="button"
                    onClick={() => setOpenIndex(isOpen ? null : index)}
                    className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-standard hover:bg-surface-subtle"
                    aria-expanded={isOpen}
                  >
                    <span className="text-base font-semibold text-foreground">{faq.question}</span>
                    <ChevronDown
                      className={`h-5 w-5 text-primary transition-standard ${isOpen ? "rotate-180" : ""}`}
                      aria-hidden="true"
                    />
                  </button>
                  {isOpen ? (
                    <div className="border-t border-border px-5 py-4 text-sm leading-relaxed text-muted">
                      {faq.answer}
                    </div>
                  ) : null}
                </div>
              );
            })
          ) : (
            <div className="rounded-lg border-default bg-surface px-6 py-12 text-center text-muted">
              No questions found matching "{searchQuery}"
            </div>
          )}
        </div>

        <div className="mt-12 rounded-lg border-default bg-surface p-8 text-center">
          <h3 className="text-2xl font-semibold text-foreground">Still have questions?</h3>
          <p className="mt-2 text-muted">
            Can't find the answer you're looking for? Our support team is ready to help.
          </p>
          <Button asChild variant="secondary" className="mt-4">
            <a href="mailto:support@codebaseaudiobook.com">Contact support</a>
          </Button>
        </div>
      </div>
    </section>
  );
};
