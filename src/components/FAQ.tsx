import { useState } from "react";
import { ChevronDown, Search } from "lucide-react";
import { Input } from "@/components/ui/input";

const faqs = [
  {
    question: "How long does it take to generate an audiobook?",
    answer: "Generation time varies by tier: Survey (15-30 min), Standard (25-40 min), Comprehensive (35-50 min). We'll email you when it's ready!",
    category: "general"
  },
  {
    question: "What programming languages do you support?",
    answer: "We support all major languages including JavaScript, TypeScript, Python, Java, Go, Rust, C++, and many more. Our AST parser handles polyglot repositories seamlessly.",
    category: "technical"
  },
  {
    question: "Can I use this for private repositories?",
    answer: "Currently we only support public GitHub repositories. Private repository support is coming soon! Join our waitlist to be notified.",
    category: "technical"
  },
  {
    question: "What's included in the audio?",
    answer: "Each audiobook includes: architectural overview, file-by-file walkthrough, function explanations, design pattern analysis, and key insights about the codebase structure.",
    category: "content"
  },
  {
    question: "Can I download the audiobook?",
    answer: "Yes! All tiers include MP3 downloads. You can listen offline anytime on your favorite audio player.",
    category: "general"
  },
  {
    question: "How accurate is the code analysis?",
    answer: "We use frontier LLMs (GPT-4, Claude) combined with static analysis tools like tree-sitter. Our accuracy is reviewed by senior engineers and continuously improved.",
    category: "technical"
  },
  {
    question: "What if I'm not satisfied?",
    answer: "We offer a 100% satisfaction guarantee. If you're not happy with the quality within 7 days, we'll refund you completely—no questions asked.",
    category: "billing"
  },
  {
    question: "Do you offer team/enterprise plans?",
    answer: "Yes! Contact us for bulk pricing, custom voice options, priority generation, and dedicated support for teams.",
    category: "billing"
  },
  {
    question: "How is this different from reading documentation?",
    answer: "Unlike docs, we explain the actual implementation. You get architectural insights, design decisions, and code flow—all while you're commuting, exercising, or doing chores.",
    category: "content"
  },
  {
    question: "Can I request updates when the repository changes?",
    answer: "Absolutely! You can regenerate audiobooks for the same repo at a 50% discount to stay up-to-date with the latest changes.",
    category: "general"
  }
];

export const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredFaqs = faqs.filter(
    (faq) =>
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <section className="px-6 py-24 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-accent/5" />

      <div className="max-w-4xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-4xl md:text-5xl font-bold">
            Frequently Asked <span className="gradient-text-primary">Questions</span>
          </h2>
          <p className="text-xl text-muted-foreground">
            Everything you need to know about code audiobooks
          </p>
        </div>

        {/* Search */}
        <div className="mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search questions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 h-14 bg-card focus-visible:ring-2 focus-visible:ring-primary/50"
            />
          </div>
        </div>

        {/* FAQ Accordion */}
        <div className="space-y-3">
          {filteredFaqs.length > 0 ? (
            filteredFaqs.map((faq, index) => (
              <div
                key={index}
                className="bg-card rounded-lg overflow-hidden transition-all duration-300"
              >
                <button
                  onClick={() => setOpenIndex(openIndex === index ? null : index)}
                  className="w-full px-6 py-5 flex items-center justify-between gap-4 text-left hover:bg-primary/5 transition-colors"
                >
                  <span className="font-semibold text-foreground">{faq.question}</span>
                  <ChevronDown
                    className={`w-5 h-5 text-primary flex-shrink-0 transition-transform duration-300 ${
                      openIndex === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    openIndex === index ? 'max-h-96' : 'max-h-0'
                  }`}
                >
                  <div className="px-6 pb-5 text-sm text-muted-foreground leading-relaxed">
                    {faq.answer}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              No questions found matching "{searchQuery}"
            </div>
          )}
        </div>

        {/* Still have questions CTA */}
        <div className="mt-12 text-center space-y-4 p-8 bg-card rounded-lg">
          <h3 className="text-2xl font-bold">Still have questions?</h3>
          <p className="text-muted-foreground">
            Can't find the answer you're looking for? Our support team is here to help.
          </p>
          <div className="flex items-center justify-center gap-4 pt-4">
            <a
              href="mailto:support@codebaseaudiobook.com"
              className="px-6 py-3 bg-gradient-to-r from-primary to-accent rounded-lg font-semibold hover-scale transition-all duration-300 shadow-[0_0_20px_rgba(138,43,226,0.3)]"
            >
              Contact Support
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};
