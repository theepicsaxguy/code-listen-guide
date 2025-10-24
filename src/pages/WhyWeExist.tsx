import { useNavigate } from "react-router-dom";
import { MarketValidation } from "@/components/MarketValidation";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";

const WhyWeExist = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <nav className="fixed top-0 w-full z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Codebase Audiobook</h1>
          <div className="flex gap-4">
            <Button variant="ghost" onClick={() => navigate('/')}>Home</Button>
            <Button onClick={() => navigate('/auth')}>Get Started</Button>
          </div>
        </div>
      </nav>
      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4 space-y-12">
          <header className="text-center space-y-4 max-w-3xl mx-auto">
            <p className="text-sm uppercase tracking-wide text-primary">Why we exist</p>
            <h2 className="text-4xl md:text-5xl font-bold">Audio tours for the repos that matter</h2>
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
