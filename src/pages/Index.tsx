import { useNavigate } from "react-router-dom";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { SampleShowcase } from "@/components/SampleShowcase";
import { Stats } from "@/components/Stats";
import { Testimonials } from "@/components/Testimonials";
import { Pricing } from "@/components/Pricing";
import { FAQ } from "@/components/FAQ";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <nav className="fixed top-0 w-full z-50 bg-card">
        <div className="container mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl sm:text-2xl font-bold gradient-text-primary">
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
              className="bg-gradient-to-r from-primary to-accent hover:scale-105 shadow-[0_0_20px_rgba(138,43,226,0.3)] hover:shadow-[0_0_30px_rgba(0,255,255,0.4)] transition-all duration-300"
            >
              Get Started
            </Button>
          </div>
        </div>
      </nav>
      <div className="pt-16">
        <Hero />
        <Stats />
        <HowItWorks />
        <SampleShowcase />
        <Testimonials />
        <Pricing />
        <FAQ />
        <Footer />
      </div>
    </div>
  );
};

export default Index;
