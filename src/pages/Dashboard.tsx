import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useUser } from './Dashboard/hooks';
import {
  Sidebar,
  OverviewPage,
  AudiobooksPage,
  AudiobookDetailPage,
  SettingsPage,
  BillingPage
} from './Dashboard/components';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user: authUser, isLoading: isAuthLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [selectedAudiobookId, setSelectedAudiobookId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const { data: user } = useUser();

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

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user ?? null}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className="flex-1 overflow-auto">
        <header className="bg-card sticky top-0 z-10">
          <div className="px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <h1 className="text-2xl font-semibold text-foreground">
                {activeTab === 'home' && 'Overview'}
                {activeTab === 'audiobooks' && 'Audiobooks'}
                {activeTab === 'audiobook-detail' && 'Player'}
                {activeTab === 'settings' && 'Settings'}
                {activeTab === 'billing' && 'Billing'}
              </h1>
              {(activeTab === 'home' || activeTab === 'audiobooks') && (
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
                  <input
                    type="text"
                    placeholder="Search repositories..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-input border-input rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
              )}
            </div>
            {activeTab !== 'audiobook-detail' && (
              <button
                onClick={handleCreateNewAudiobook}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2.5 rounded-lg font-medium flex items-center gap-2 transition-all shadow-lg"
                aria-label="Create New Audiobook"
              >
                <Plus size={18} />
                New Audiobook
              </button>
            )}
          </div>
        </header>
        <main className="p-8">
          {activeTab === 'home' && <OverviewPage onNavigateToAudiobook={handleNavigateToAudiobook} />}
          {activeTab === 'audiobooks' && <AudiobooksPage onNavigateToAudiobook={handleNavigateToAudiobook} />}
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
