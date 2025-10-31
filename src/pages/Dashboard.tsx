import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus } from 'lucide-react';

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
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

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

  return (
    <div className="flex min-h-screen bg-background text-text">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user ?? null}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className="flex-1 overflow-hidden">
        <div className="border-b border-border bg-surface/60 backdrop-blur">
          <div className="mx-auto flex max-w-[1280px] flex-col gap-6 px-6 py-6">
            <div className="space-y-3">
              <Breadcrumb>
                <BreadcrumbList>
                  {crumbs.map((crumb, index) => (
                    <React.Fragment key={crumb.label}>
                      <BreadcrumbItem>
                        <BreadcrumbLink href={crumb.href}>{crumb.label}</BreadcrumbLink>
                      </BreadcrumbItem>
                      {index < crumbs.length - 1 && <BreadcrumbSeparator />}
                    </React.Fragment>
                  ))}
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>{title}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <div className="flex flex-col gap-2">
                <h1 className="text-4xl font-semibold text-text">{title}</h1>
                <p className="text-sm text-muted-foreground">{description}</p>
              </div>
            </div>
            <div className={cn('flex flex-col gap-3', (activeTab === 'home' || activeTab === 'audiobooks') && 'md:flex-row md:items-center md:justify-between')}>
              {(activeTab === 'home' || activeTab === 'audiobooks') && (
                <div className="w-full md:max-w-sm">
                  <div className="relative">
                    <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      value={searchQuery}
                      onChange={(event) => setSearchQuery(event.target.value)}
                      placeholder="Search repositories or jobs"
                      className="pl-9"
                      aria-label="Search audiobooks"
                    />
                  </div>
                </div>
              )}
              {activeTab !== 'audiobook-detail' && (
                <div className="flex justify-end">
                  <Button onClick={handleCreateNewAudiobook} className="min-w-[160px]">
                    <Plus className="h-4 w-4" />
                    <span className="ml-2">New Audiobook</span>
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
        <main className="mx-auto max-w-[1280px] space-y-6 px-6 py-6">
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
