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
      <nav className="fixed top-0 w-full z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Codebase Audiobook</h1>
          <div className="flex gap-4">
            <Button variant="ghost" onClick={() => navigate('/auth')}>Login</Button>
            <Button onClick={() => navigate('/auth')}>Get Started</Button>
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
