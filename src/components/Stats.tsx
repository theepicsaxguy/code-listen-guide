import { useEffect, useRef, useState } from "react";
import { Code2, BookOpen, Clock, Users } from "lucide-react";

const stats = [
  {
    icon: Code2,
    value: 10000,
    suffix: "+",
    label: "Repositories Converted",
    color: "text-primary"
  },
  {
    icon: Clock,
    value: 500,
    suffix: "+",
    label: "Hours of Learning",
    color: "text-accent"
  },
  {
    icon: BookOpen,
    value: 50000,
    suffix: "+",
    label: "Chapters Generated",
    color: "text-success"
  },
  {
    icon: Users,
    value: 2500,
    suffix: "+",
    label: "Happy Developers",
    color: "text-warning"
  }
];

const CountUp = ({ end, duration = 2000 }: { end: number; duration?: number }) => {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const countRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (countRef.current) {
      observer.observe(countRef.current);
    }

    return () => {
      if (countRef.current) {
        observer.unobserve(countRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Ease out quad
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(easeOut * end));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [end, duration, isVisible]);

  return (
    <div ref={countRef} className="text-5xl font-bold">
      {count.toLocaleString()}
    </div>
  );
};

export const Stats = () => {
  return (
    <section className="px-6 py-24 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/10 via-accent/5 to-transparent" />
      <div className="absolute inset-0 mesh-gradient opacity-30" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-heading md:text-display font-bold">
            Trusted by <span className="gradient-text-primary">Developers</span> Worldwide
          </h2>
          <p className="text-body text-muted-foreground max-w-2xl mx-auto">
            Join thousands of developers learning code through audio
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-surface-secondary p-8 rounded-card shadow-sm hover:shadow-md hover-lift group text-center relative overflow-hidden transition-standard"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Background glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                <div className="relative z-10 space-y-4">
                  {/* Icon */}
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-lg bg-gradient-to-br from-primary/20 to-accent/10 group-hover:scale-110 transition-transform duration-300">
                    <Icon className={`w-8 h-8 ${stat.color}`} />
                  </div>

                  {/* Counter */}
                  <div className="space-y-2">
                    <div className="flex items-baseline justify-center gap-1">
                      <CountUp end={stat.value} />
                      <span className="text-3xl font-bold gradient-text-primary">{stat.suffix}</span>
                    </div>
                    <p className="text-body-sm text-muted-foreground font-medium">{stat.label}</p>
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
