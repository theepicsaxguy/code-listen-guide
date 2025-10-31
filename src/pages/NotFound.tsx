import { useLocation } from "react-router-dom";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold text-foreground">404</h1>
        <p className="text-lg text-muted">Oops! Page not found.</p>
        <Button asChild className="transition-standard">
          <a href="/">Return home</a>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
