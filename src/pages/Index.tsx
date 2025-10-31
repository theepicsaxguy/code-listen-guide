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
    <div className="min-h-screen bg-background">
      <nav className="fixed inset-x-0 top-0 z-50 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-content items-center justify-between px-4 py-4 sm:px-6">
          <p className="text-lg font-semibold text-foreground">Codebase Audiobook</p>
          <div className="flex items-center gap-2 sm:gap-3">
            <Button variant="ghost" onClick={() => navigate('/why-we-exist')} className="hidden sm:inline-flex">
              Why we exist
            </Button>
            <Button variant="ghost" onClick={() => navigate('/auth')} className="hidden sm:inline-flex">
              Login
            </Button>
            <Button onClick={() => navigate('/auth')} className="transition-standard">
              Get started
            </Button>
          </div>
        </div>
      </nav>
      <div className="pt-20">
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
