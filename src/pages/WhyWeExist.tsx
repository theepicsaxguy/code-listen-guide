import { useNavigate } from "react-router-dom";
import { MarketValidation } from "@/components/MarketValidation";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";

const WhyWeExist = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <nav className="fixed top-0 w-full z-50 glass supports-[backdrop-filter]:bg-background/70">
        <div className="container mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl sm:text-2xl font-bold gradient-text-primary">
            Codebase Audiobook
          </h1>
          <div className="flex gap-2 sm:gap-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="hover:bg-primary/10 hover:text-primary transition-colors"
            >
              Home
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
      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4 space-y-12">
          <header className="text-center space-y-4 max-w-3xl mx-auto">
            <p className="text-sm uppercase tracking-wide text-primary glow">Why we exist</p>
            <h2 className="text-4xl md:text-5xl font-bold gradient-text-primary">
              Audio tours for the repos that matter
            </h2>
            <p className="text-lg text-muted-foreground">
              We built Codebase Audiobook because developers deserve a way to learn complex systems while living their lives.
              These signals show the opportunity we are chasing.
            </p>
          </header>
          <MarketValidation />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default WhyWeExist;
