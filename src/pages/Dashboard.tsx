import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Menu, X } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';

import { useUser } from './Dashboard/hooks';
import {
  Sidebar,
  OverviewPage,
  AudiobooksPage,
  AudiobookDetailPage,
  SettingsPage,
  BillingPage,
} from './Dashboard/components';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user: authUser, isLoading: isAuthLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [selectedAudiobookId, setSelectedAudiobookId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  // Mobile: collapsed by default, desktop: expanded
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(typeof window !== 'undefined' && window.innerWidth < 768);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const { data: user } = useUser();

  // Check URL params for tab navigation
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    if (tabParam && ['home', 'audiobooks', 'settings', 'billing'].includes(tabParam)) {
      setActiveTab(tabParam);
      // Clean up URL
      params.delete('tab');
      const newSearch = params.toString();
      const newUrl = newSearch ? `?${newSearch}` : window.location.pathname;
      window.history.replaceState({}, '', newUrl);
    }
  }, []);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthLoading && !authUser) {
      navigate('/auth');
    }
  }, [authUser, isAuthLoading, navigate]);

  // Handle mobile sidebar collapse on resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsSidebarCollapsed(true);
        setIsMobileMenuOpen(false);
      } else {
        setIsSidebarCollapsed(false);
      }
    };

    handleResize(); // Set initial state
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Memoize title/description/crumbs BEFORE early returns to ensure hooks order consistency
  const { title, description, crumbs } = useMemo(() => {
    if (activeTab === 'audiobook-detail' && selectedAudiobookId) {
      return {
        title: 'Audiobook Player',
        description: 'Listen to generated chapters and review production notes.',
        crumbs: [
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Audiobooks', href: '#audiobooks' },
        ],
      };
    }

    if (activeTab === 'audiobooks') {
      return {
        title: 'Audiobooks',
        description: 'Manage generated audiobooks and track production status.',
        crumbs: [
          { label: 'Dashboard', href: '/dashboard' },
        ],
      };
    }

    if (activeTab === 'settings') {
      return {
        title: 'Settings',
        description: 'Update account preferences and defaults for new jobs.',
        crumbs: [
          { label: 'Dashboard', href: '/dashboard' },
        ],
      };
    }

    if (activeTab === 'billing') {
      return {
        title: 'Billing',
        description: 'Review your plan, invoices, and usage summary.',
        crumbs: [
          { label: 'Dashboard', href: '/dashboard' },
        ],
      };
    }

    return {
      title: 'Overview',
      description: 'Stay on top of progress across jobs, credits, and usage.',
      crumbs: [
        { label: 'Dashboard', href: '/dashboard' },
      ],
    };
  }, [activeTab, selectedAudiobookId]);

  // Show loading while checking auth
  if (isAuthLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render dashboard if not authenticated
  if (!authUser) {
    return null;
  }

  const handleNavigateToAudiobook = (id: string) => {
    setSelectedAudiobookId(id);
    setActiveTab('audiobook-detail');
  };

  const handleBackToAudiobooks = () => {
    setSelectedAudiobookId(null);
    setActiveTab('audiobooks');
  };

  const handleCreateNewAudiobook = () => {
    // Navigate to the submit page where users can create new audiobooks
    navigate('/submit');
  };

  return (
    <div className="flex h-screen bg-background text-foreground relative anchor-gradient overflow-hidden">
      {/* Reduced gradient opacity - Vercel style (3-5% max) */}
      <div className="fixed inset-0 bg-gradient-to-br from-cyan-400/[0.03] via-transparent to-transparent pointer-events-none" />
      
      {/* Mobile menu overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 rounded-lg bg-sidebar-surface border border-sidebar-border text-sidebar-foreground hover:bg-sidebar-accent/60 transition-colors"
        aria-label="Toggle menu"
      >
        {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <Sidebar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          // Close mobile menu on navigation
          if (window.innerWidth < 768) {
            setIsMobileMenuOpen(false);
          }
        }}
        user={user ?? null}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        isMobileMenuOpen={isMobileMenuOpen}
      />
      <div className="flex-1 overflow-y-auto relative min-w-0">
        <div className="surface-depth mx-auto">
          <div className="mx-auto flex max-w-7xl flex-col gap-8 md:gap-12 px-4 md:px-6 py-12 md:py-24">
            <div className="space-y-8">
              <Breadcrumb>
                <BreadcrumbList>
                  {crumbs.map((crumb, index) => (
                    <React.Fragment key={crumb.label}>
                      <BreadcrumbItem>
                        <BreadcrumbLink href={crumb.href} className="text-muted-foreground hover:text-foreground-muted transition-fast">{crumb.label}</BreadcrumbLink>
                      </BreadcrumbItem>
                      {index < crumbs.length - 1 && <BreadcrumbSeparator />}
                    </React.Fragment>
                  ))}
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage className="text-muted-foreground">{title}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <div className="flex flex-col gap-4 md:gap-6">
                <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl 2xl:text-[4.5rem] font-bold leading-[1.1]">{title}</h1>
                <p className="text-base md:text-lg leading-relaxed text-foreground-muted font-normal max-w-3xl">{description}</p>
              </div>
            </div>
            <div className={cn('flex flex-col gap-4', (activeTab === 'home' || activeTab === 'audiobooks') && 'md:flex-row md:items-center md:justify-between')}>
              {(activeTab === 'home' || activeTab === 'audiobooks') && (
                <div className="w-full md:max-w-sm">
                  <div className="relative">
                    <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      value={searchQuery}
                      onChange={(event) => setSearchQuery(event.target.value)}
                      placeholder="Search repositories or jobs"
                      className="pl-9 bg-surface border-zinc-800"
                      aria-label="Search audiobooks"
                    />
                  </div>
                </div>
              )}
              {activeTab !== 'audiobook-detail' && (
                <div className="flex justify-end">
                  <Button onClick={handleCreateNewAudiobook} className="w-full sm:w-auto min-w-[160px]">
                    <Plus className="h-4 w-4" />
                    <span className="ml-2">New Audiobook</span>
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
        <main className="mx-auto max-w-7xl space-y-8 md:space-y-12 px-4 md:px-6 py-8 md:py-12 relative">
          {activeTab === 'home' && <OverviewPage onNavigateToAudiobook={handleNavigateToAudiobook} />}
          {activeTab === 'audiobooks' && (
            <AudiobooksPage onNavigateToAudiobook={handleNavigateToAudiobook} searchQuery={searchQuery} />
          )}
          {activeTab === 'audiobook-detail' && selectedAudiobookId && (
            <AudiobookDetailPage audiobookId={selectedAudiobookId} onBack={handleBackToAudiobooks} />
          )}
          {activeTab === 'settings' && <SettingsPage />}
          {activeTab === 'billing' && <BillingPage />}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
