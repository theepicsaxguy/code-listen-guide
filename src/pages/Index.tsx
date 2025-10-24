import { Hero } from "@/components/Hero";
import { DepthSelector } from "@/components/DepthSelector";
import { HowItWorks } from "@/components/HowItWorks";
import { SampleShowcase } from "@/components/SampleShowcase";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Hero />
      <SampleShowcase />
      <DepthSelector />
      <HowItWorks />
      <Footer />
    </div>
  );
};

export default Index;
