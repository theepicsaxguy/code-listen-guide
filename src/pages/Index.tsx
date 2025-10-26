import { useNavigate } from "react-router-dom";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { SampleShowcase } from "@/components/SampleShowcase";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <nav className="fixed top-0 w-full z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/70">
        <div className="container mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
            Codebase Audiobook
          </h1>
          <div className="flex gap-2 sm:gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/why-we-exist')}
              className="hover:bg-primary/10 hover:text-primary transition-colors"
            >
              Why we exist
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/auth')}
              className="hidden sm:inline-flex hover:bg-primary/10 hover:text-primary transition-colors"
            >
              Login
            </Button>
            <Button
              onClick={() => navigate('/auth')}
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90 shadow-lg shadow-primary/20 transition-all hover:shadow-xl hover:shadow-primary/30"
            >
              Get Started
            </Button>
          </div>
        </div>
      </nav>
      <div className="pt-16">
        <Hero />
        <SampleShowcase />
        <HowItWorks />
        <Footer />
      </div>
    </div>
  );
};

export default Index;
