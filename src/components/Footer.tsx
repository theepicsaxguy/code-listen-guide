import { Github, Twitter, Mail } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="relative px-6 py-12 bg-surface">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 gap-8 mb-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground">
              Codebase Audiobook
            </h3>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Transform any GitHub repository into a comprehensive technical audiobook
            </p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-foreground">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-primary transition-standard">How It Works</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Pricing</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Samples</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Documentation</a></li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-foreground">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-primary transition-standard">About</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Blog</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Careers</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Contact</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-foreground">Legal</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-primary transition-standard">Privacy</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Terms</a></li>
              <li><a href="#" className="hover:text-primary transition-standard">Licenses</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="flex flex-col gap-4 pt-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-muted-foreground">
            © 2025 Codebase Audiobook. All rights reserved.
          </p>
          
          <div className="flex items-center gap-4">
            <a href="#" className="text-muted-foreground hover:text-primary transition-standard">
              <Github className="w-5 h-5" />
            </a>
            <a href="#" className="text-muted-foreground hover:text-primary transition-standard">
              <Twitter className="w-5 h-5" />
            </a>
            <a href="#" className="text-muted-foreground hover:text-primary transition-standard">
              <Mail className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
