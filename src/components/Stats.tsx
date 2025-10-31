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
    <div ref={countRef} className="text-4xl font-semibold text-foreground">
      {count.toLocaleString()}
    </div>
  );
};

export const Stats = () => {
  return (
    <section className="px-6 py-24 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center space-y-4 mb-20">
          <h2 className="text-3xl md:text-4xl font-semibold text-foreground leading-tight">
            Trusted by <span className="text-primary">Developers</span> Worldwide
          </h2>
          <p className="text-base text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Join thousands of developers learning code through audio
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-surface p-6 hover:bg-surface-secondary/50 transition-colors group text-center relative"
              >
                <div className="space-y-4">
                  {/* Icon */}
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors">
                    <Icon className="w-6 h-6" />
                  </div>

                  {/* Counter */}
                  <div className="space-y-2">
                    <div className="flex items-baseline justify-center gap-1">
                      <CountUp end={stat.value} />
                      <span className="text-3xl font-semibold text-primary">{stat.suffix}</span>
                    </div>
                    <p className="text-sm text-muted-foreground font-medium uppercase tracking-wide">{stat.label}</p>
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
