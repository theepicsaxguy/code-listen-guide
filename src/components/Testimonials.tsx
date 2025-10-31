import { Star, Quote } from "lucide-react";
import { Card } from "@/components/ui/card";

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Senior Frontend Engineer",
    company: "Tech Startup",
    avatar: "SC",
    content: "Transformed my commute into learning time. I finally understood React's internals while driving to work. Game changer!",
    rating: 5,
    gradient: "from-blue-500 to-cyan-400"
  },
  {
    name: "Marcus Rodriguez",
    role: "Full Stack Developer",
    company: "Fortune 500",
    avatar: "MR",
    content: "The depth of analysis is incredible. It's like having a senior developer explain the entire codebase to you.",
    rating: 5,
    gradient: "from-primary to-accent"
  },
  {
    name: "Emily Watson",
    role: "DevOps Engineer",
    company: "Cloud Company",
    avatar: "EW",
    content: "I've learned more about Kubernetes internals in my morning jogs than I did reading docs for weeks. Absolutely worth it.",
    rating: 5,
    gradient: "from-purple-500 to-pink-400"
  },
  {
    name: "David Kim",
    role: "Backend Developer",
    company: "E-commerce",
    avatar: "DK",
    content: "As someone who learns better by listening, this is perfect. The code explanations are clear and comprehensive.",
    rating: 5,
    gradient: "from-green-400 to-emerald-400"
  },
  {
    name: "Priya Patel",
    role: "Tech Lead",
    company: "Fintech",
    avatar: "PP",
    content: "Onboarding to our legacy codebase used to take weeks. Now new devs listen to the audiobook on day one. Incredible ROI.",
    rating: 5,
    gradient: "from-orange-500 to-red-400"
  },
  {
    name: "Alex Johnson",
    role: "Mobile Developer",
    company: "Gaming Studio",
    avatar: "AJ",
    content: "Finally a way to learn while my hands are busy. Perfect for gym sessions, cooking, or any time I can't look at a screen.",
    rating: 5,
    gradient: "from-indigo-500 to-blue-400"
  }
];

export const Testimonials = () => {
  return (
    <section className="relative px-6 py-24 overflow-hidden">
      {/* Radial gradient accent */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-3xl font-bold text-foreground leading-tight sm:text-4xl">
            Loved by <span className="text-primary">Developers</span>
          </h2>
          <p className="text-base leading-relaxed text-muted-foreground max-w-2xl mx-auto">
            See what developers are saying about learning code through audio
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <Card
              key={index}
              className="p-6 group relative overflow-hidden transition-standard hover:shadow-xl hover:shadow-primary/10"
            >
              {/* Gradient overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

              {/* Quote icon background */}
              <div className="absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity pointer-events-none">
                <Quote className="w-16 h-16 text-primary" />
              </div>

              <div className="relative z-10 space-y-4">
                {/* Rating */}
                <div className="flex items-center gap-1">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-warning text-warning" />
                  ))}
                </div>

                {/* Content */}
                <p className="text-sm leading-relaxed text-muted-foreground">
                  "{testimonial.content}"
                </p>

                {/* Author */}
                <div className="flex items-center gap-3 pt-2">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center font-bold text-sm text-primary">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-semibold text-sm text-foreground">{testimonial.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {testimonial.role} at {testimonial.company}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Social proof stats */}
        <div className="mt-16 text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <div className="flex -space-x-2">
              {testimonials.slice(0, 5).map((t, i) => (
                <div
                  key={i}
                  className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-xs text-primary border-2 border-background"
                >
                  {t.avatar}
                </div>
              ))}
            </div>
            <p className="text-sm text-muted-foreground">
              Join <span className="font-bold text-foreground">2,500+</span> developers learning through audio
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
