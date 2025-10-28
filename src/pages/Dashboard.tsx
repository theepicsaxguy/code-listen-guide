import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, 
  Pause,
  SkipForward, 
  SkipBack,
  Volume2,
  VolumeX,
  Download, 
  RefreshCw,
  Search,
  Plus,
  Settings,
  CreditCard,
  Clock,
  CheckCircle,
  XCircle,
  Loader,
  ChevronRight,
  Mic,
  Home,
  Library,
  FileCode,
  GitBranch,
  AlertCircle,
  Share2,
  Copy,
  Check,
  Headphones,
  Calendar,
} from 'lucide-react';

// Types (duplicated locally for this mock dashboard; real code should import from central types)
interface AudiobookJob {
  id: string;
  repositoryName: string;
  repositoryUrl: string;
  status: 'processing' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
  duration: string;
  chapterCount: number;
  progress?: number;
  fileSize?: string;
  language?: string;
  frameworks?: string[];
  errorMessage?: string;
}

interface Chapter {
  id: string;
  title: string;
  duration: string;
  timestamp: number;
  files: string[];
}

interface AudiobookDetail extends AudiobookJob {
  chapters: Chapter[];
  description: string;
  totalFiles: number;
  linesOfCode: number;
}

interface UserProfile {
  name: string;
  email: string;
  plan: 'free' | 'pro' | 'enterprise';
  createdAt: string;
  is_admin?: boolean;
}

interface BillingInfo {
  plan: string;
  price: number;
  interval: 'month' | 'year';
  creditsUsed: number;
  creditsTotal: number;
  nextBillingDate: string;
  paymentMethod?: {
    type: 'card';
    last4: string;
    brand: string;
    expiryMonth: number;
    expiryYear: number;
  };
}

// Mock Data
const mockUser: UserProfile = {
  name: 'John Developer',
  email: 'john@example.com',
  plan: 'pro',
  createdAt: '2024-09-15T10:00:00Z',
  is_admin: false // Set to true to test admin link visibility
};

const mockBilling: BillingInfo = {
  plan: 'Pro',
  price: 29,
  interval: 'month',
  creditsUsed: 24,
  creditsTotal: 100,
  nextBillingDate: '2025-11-28T00:00:00Z',
  paymentMethod: {
    type: 'card',
    last4: '4242',
    brand: 'Visa',
    expiryMonth: 12,
    expiryYear: 2026
  }
};

const mockAudiobooks: AudiobookJob[] = [
  {
    id: '1',
    repositoryName: 'facebook/react',
    repositoryUrl: 'https://github.com/facebook/react',
    status: 'completed',
    createdAt: '2025-10-27T14:30:00Z',
    completedAt: '2025-10-27T16:45:00Z',
    duration: '2h 34m',
    chapterCount: 12,
    fileSize: '156 MB',
    language: 'JavaScript',
    frameworks: ['React', 'JSX']
  },
  {
    id: '2',
    repositoryName: 'microsoft/typescript',
    repositoryUrl: 'https://github.com/microsoft/typescript',
    status: 'processing',
    createdAt: '2025-10-28T09:15:00Z',
    duration: '0h 0m',
    chapterCount: 0,
    progress: 67,
    language: 'TypeScript'
  },
  {
    id: '3',
    repositoryName: 'tensorflow/tensorflow',
    repositoryUrl: 'https://github.com/tensorflow/tensorflow',
    status: 'completed',
    createdAt: '2025-10-26T11:20:00Z',
    completedAt: '2025-10-26T18:30:00Z',
    duration: '4h 12m',
    chapterCount: 18,
    fileSize: '324 MB',
    language: 'Python',
    frameworks: ['TensorFlow', 'Keras']
  },
  {
    id: '4',
    repositoryName: 'vercel/next.js',
    repositoryUrl: 'https://github.com/vercel/next.js',
    status: 'failed',
    createdAt: '2025-10-25T16:45:00Z',
    duration: '0h 0m',
    chapterCount: 0,
    language: 'TypeScript',
    errorMessage: 'Repository parsing failed: timeout after 10 minutes'
  },
  {
    id: '5',
    repositoryName: 'django/django',
    repositoryUrl: 'https://github.com/django/django',
    status: 'completed',
    createdAt: '2025-10-24T08:00:00Z',
    completedAt: '2025-10-24T12:15:00Z',
    duration: '3h 28m',
    chapterCount: 15,
    fileSize: '198 MB',
    language: 'Python',
    frameworks: ['Django', 'ORM']
  },
  {
    id: '6',
    repositoryName: 'golang/go',
    repositoryUrl: 'https://github.com/golang/go',
    status: 'completed',
    createdAt: '2025-10-23T13:30:00Z',
    completedAt: '2025-10-23T17:00:00Z',
    duration: '2h 56m',
    chapterCount: 14,
    fileSize: '187 MB',
    language: 'Go'
  }
];

const mockDetailedAudiobook: AudiobookDetail = {
  ...mockAudiobooks[0],
  description: 'A comprehensive walkthrough of React\'s core architecture, component system, and reconciliation algorithm.',
  totalFiles: 487,
  linesOfCode: 125000,
  chapters: [
    {
      id: 'ch1',
      title: 'Introduction and Project Overview',
      duration: '12m 34s',
      timestamp: 0,
      files: ['README.md', 'CONTRIBUTING.md', 'package.json']
    },
    {
      id: 'ch2',
      title: 'Core Architecture and Reconciliation',
      duration: '18m 45s',
      timestamp: 754,
      files: ['packages/react-reconciler/src/ReactFiber.js', 'packages/react-reconciler/src/ReactFiberWorkLoop.js']
    },
    {
      id: 'ch3',
      title: 'Component Lifecycle and Hooks',
      duration: '22m 18s',
      timestamp: 1879,
      files: ['packages/react/src/ReactHooks.js', 'packages/react-reconciler/src/ReactFiberHooks.js']
    },
    {
      id: 'ch4',
      title: 'Virtual DOM Implementation',
      duration: '16m 52s',
      timestamp: 3217,
      files: ['packages/react-dom/src/client/ReactDOM.js']
    },
    {
      id: 'ch5',
      title: 'Event System',
      duration: '14m 28s',
      timestamp: 4229,
      files: ['packages/react-dom/src/events/DOMPluginEventSystem.js']
    }
  ]
};

const mockInvoices = [
  { id: 'inv_001', date: '2025-10-01', amount: 29.00, status: 'paid' },
  { id: 'inv_002', date: '2025-09-01', amount: 29.00, status: 'paid' },
  { id: 'inv_003', date: '2025-08-01', amount: 29.00, status: 'paid' },
  { id: 'inv_004', date: '2025-07-01', amount: 0.00, status: 'paid' }
];

// Utility Components
const StatusBadge: React.FC<{ status: AudiobookJob['status'] }> = ({ status }) => {
  const styles = {
    processing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30'
  } as const;

  const icons = {
    processing: <Loader size={12} className="animate-spin" />,
    completed: <CheckCircle size={12} />,
    failed: <XCircle size={12} />
  } as const;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${styles[status]}`}>
      {icons[status]}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

const PlanBadge: React.FC<{ plan: string }> = ({ plan }) => {
  const styles = {
    free: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    pro: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    enterprise: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  } as const;

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${styles[plan.toLowerCase() as keyof typeof styles]}`}>
      {plan}
    </span>
  );
};

// Sidebar Component
const Sidebar: React.FC<{ activeTab: string; setActiveTab: (tab: string) => void }> = ({ activeTab, setActiveTab }) => {
  const navigate = useNavigate();
  
  const navItems = [
    { id: 'home', label: 'Overview', icon: <Home size={20} /> },
    { id: 'audiobooks', label: 'Audiobooks', icon: <Library size={20} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
    { id: 'billing', label: 'Billing', icon: <CreditCard size={20} /> },
    ...(mockUser.is_admin ? [{ id: 'admin', label: 'Admin', icon: <Settings size={20} /> }] : [])
  ];
  
  const handleNavClick = (itemId: string) => {
    if (itemId === 'admin') {
      navigate('/admin');
    } else {
      setActiveTab(itemId);
    }
  };

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 h-screen flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
            <Mic className="text-white" size={24} />
          </div>
          <div>
            <div className="font-semibold text-white">Codebase Audio</div>
            <div className="text-xs text-gray-400">Dashboard</div>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleNavClick(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-all ${
              activeTab === item.id 
                ? 'bg-gray-800 text-white shadow-lg' 
                : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800/50">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-sm font-medium text-white">
            {mockUser.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">{mockUser.name}</div>
            <div className="text-xs text-gray-400">{mockUser.plan} Plan</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Overview Page
const OverviewPage: React.FC<{ onNavigateToAudiobook: (id: string) => void }> = ({ onNavigateToAudiobook }) => {
  const completedBooks = mockAudiobooks.filter(a => a.status === 'completed');
  const totalHours = completedBooks.reduce((sum, book) => {
    const parts = book.duration.split('h ');
    if (parts.length < 2) return sum;
    const hours = parseInt(parts[0]);
    const mins = parseInt(parts[1]);
    return sum + hours + mins / 60;
  }, 0);

  const usageData = [
    { date: 'Oct 21', count: 2 },
    { date: 'Oct 22', count: 3 },
    { date: 'Oct 23', count: 4 },
    { date: 'Oct 24', count: 3 },
    { date: 'Oct 25', count: 5 },
    { date: 'Oct 26', count: 4 },
    { date: 'Oct 27', count: 3 }
  ];

  const maxCount = Math.max(...usageData.map(d => d.count));

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:border-gray-600 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <div className="text-gray-400">
              <Library size={24} />
            </div>
            <div className="text-sm text-green-400 flex items-center gap-1">
              <CheckCircle size={14} />
              +12%
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">{mockAudiobooks.length}</div>
          <div className="text-sm text-gray-400">Total Audiobooks</div>
          <div className="text-xs text-gray-500 mt-1">{completedBooks.length} completed</div>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:border-gray-600 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <div className="text-gray-400">
              <Clock size={24} />
            </div>
          </div>
            <div className="text-3xl font-bold text-white mb-1">{totalHours.toFixed(1)}h</div>
            <div className="text-sm text-gray-400">Hours Generated</div>
            <div className="text-xs text-gray-500 mt-1">Total audio content</div>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:border-gray-600 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <div className="text-gray-400">
              <Headphones size={24} />
            </div>
          </div>
          <div className="text-3xl font-bold text-white mb-1">{mockBilling.creditsUsed}/{mockBilling.creditsTotal}</div>
          <div className="text-sm text-gray-400">Credits Used</div>
          <div className="text-xs text-gray-500 mt-1">Resets soon</div>
        </div>
      </div>
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Usage This Week</h3>
        <div className="flex items-end justify-between gap-3 h-40">
          {usageData.map((data, index) => (
            <div key={index} className="flex-1 flex flex-col items-center gap-3">
              <div 
                className="w-full bg-gradient-to-t from-purple-500 to-blue-500 rounded-t hover:from-purple-600 hover:to-blue-600 transition-all cursor-pointer relative group"
                style={{ height: `${(data.count / maxCount) * 100}%`, minHeight: '12px' }}
              >
                <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-900 border border-gray-700 text-white text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-xl">
                  {data.count} audiobooks
                </div>
              </div>
              <div className="text-xs text-gray-400">{data.date}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Recent Activity</h2>
        </div>
        <div className="divide-y divide-gray-700">
          {mockAudiobooks.slice(0, 5).map((job) => (
            <div 
              key={job.id}
              className="p-6 hover:bg-gray-750 transition-colors cursor-pointer"
              onClick={() => onNavigateToAudiobook(job.id)}
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileCode className="text-white" size={24} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-medium text-white truncate">{job.repositoryName}</h3>
                    <StatusBadge status={job.status} />
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      {formatDate(job.createdAt)}
                    </span>
                    {job.chapterCount > 0 && <span>{job.chapterCount} chapters</span>}
                    {job.duration !== '0h 0m' && <span>{job.duration}</span>}
                    {job.language && <span className="px-2 py-0.5 bg-gray-700 rounded text-xs">{job.language}</span>}
                  </div>
                  {job.status === 'processing' && job.progress && (
                    <div className="mt-3 w-full bg-gray-700 rounded-full h-2">
                      <div className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300" style={{ width: `${job.progress}%` }} />
                    </div>
                  )}
                  {job.status === 'failed' && job.errorMessage && (
                    <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
                      <AlertCircle size={12} />
                      {job.errorMessage}
                    </div>
                  )}
                </div>
                <ChevronRight className="text-gray-600 flex-shrink-0" size={20} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Audiobooks Library Page
const AudiobooksPage: React.FC<{ onNavigateToAudiobook: (id: string) => void }> = ({ onNavigateToAudiobook }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'duration'>('date');

  const filteredAudiobooks = mockAudiobooks
    .filter(book => {
      const matchesSearch = book.repositoryName.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filterStatus === 'all' || book.status === filterStatus;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      if (sortBy === 'date') return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      if (sortBy === 'name') return a.repositoryName.localeCompare(b.repositoryName);
      return 0;
    });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search audiobooks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        <div className="flex gap-3">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="date">Sort by Date</option>
            <option value="name">Sort by Name</option>
            <option value="duration">Sort by Duration</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredAudiobooks.map((book) => (
          <div
            key={book.id}
            className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:border-gray-600 transition-all cursor-pointer group"
            onClick={() => onNavigateToAudiobook(book.id)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                  <GitBranch className="text-white" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-white group-hover:text-purple-400 transition-colors">{book.repositoryName}</h3>
                  <p className="text-sm text-gray-400">{book.language}</p>
                </div>
              </div>
              <StatusBadge status={book.status} />
            </div>
            {book.frameworks && book.frameworks.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {book.frameworks.map((framework, idx) => (
                  <span key={idx} className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">{framework}</span>
                ))}
              </div>
            )}
            {book.status === 'processing' && book.progress && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2 text-sm">
                  <span className="text-gray-400">Processing...</span>
                  <span className="text-white font-medium">{book.progress}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300" style={{ width: `${book.progress}%` }} />
                </div>
              </div>
            )}
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-4 text-gray-400">
                {book.duration !== '0h 0m' && (
                  <span className="flex items-center gap-1"><Clock size={14} />{book.duration}</span>
                )}
                {book.chapterCount > 0 && <span>{book.chapterCount} chapters</span>}
                {book.fileSize && <span>{book.fileSize}</span>}
              </div>
              {book.status === 'completed' && (
                <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Play audiobook">
                  <Play size={16} className="text-purple-400" />
                </button>
              )}
            </div>
            {book.status === 'failed' && book.errorMessage && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-xs text-red-400 flex items-center gap-2"><AlertCircle size={14} />{book.errorMessage}</p>
              </div>
            )}
          </div>
        ))}
      </div>
      {filteredAudiobooks.length === 0 && (
        <div className="text-center py-12">
          <Library size={48} className="text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">No audiobooks found</h3>
          <p className="text-sm text-gray-500">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
};

// Audiobook Player/Detail Page
const AudiobookDetailPage: React.FC<{ audiobookId: string; onBack: () => void }> = ({ audiobookId, onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentChapter, setCurrentChapter] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(75);
  const [isMuted, setIsMuted] = useState(false);
  const [copied, setCopied] = useState(false);

  const audiobook = mockDetailedAudiobook;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleCopyUrl = () => {
    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <button onClick={onBack} className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
        <ChevronRight size={16} className="rotate-180" />
        Back to Audiobooks
      </button>
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
        <div className="flex items-start gap-6">
          <div className="w-32 h-32 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center flex-shrink-0">
            <GitBranch className="text-white" size={64} />
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">{audiobook.repositoryName}</h1>
                <p className="text-gray-400 mb-4">{audiobook.description}</p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={handleCopyUrl} className="p-2 hover:bg-gray-700 rounded-lg transition-colors" title="Copy link">
                  {copied ? <Check size={20} className="text-green-400" /> : <Copy size={20} className="text-gray-400" />}
                </button>
                <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors" title="Share"><Share2 size={20} className="text-gray-400" /></button>
                <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors" title="Download"><Download size={20} className="text-gray-400" /></button>
              </div>
            </div>
            <div className="flex flex-wrap gap-4 text-sm text-gray-400">
              <span className="flex items-center gap-1"><Clock size={16} />{audiobook.duration}</span>
              <span>{audiobook.chapterCount} chapters</span>
              <span>{audiobook.totalFiles} files</span>
              <span>{audiobook.linesOfCode.toLocaleString()} lines of code</span>
              {audiobook.language && <span className="px-2 py-1 bg-gray-700 rounded text-xs">{audiobook.language}</span>}
            </div>
            {audiobook.frameworks && audiobook.frameworks.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {audiobook.frameworks.map((framework, idx) => (
                  <span key={idx} className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs text-purple-400">{framework}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">Chapter {currentChapter + 1}: {audiobook.chapters[currentChapter].title}</h3>
            <p className="text-sm text-gray-400">{audiobook.chapters[currentChapter].files.length} files covered</p>
          </div>
          <div className="text-sm text-gray-400">{formatTime(currentTime)} / {audiobook.chapters[currentChapter].duration}</div>
        </div>
        <div className="mb-6">
          <input
            type="range"
            min="0"
            max="100"
            value={(currentTime / 754) * 100}
            onChange={(e) => setCurrentTime((parseInt(e.target.value) / 100) * 754)}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-purple-500"
          />
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="p-3 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Previous Chapter"><SkipBack size={20} className="text-gray-400" /></button>
            <button onClick={() => setIsPlaying(!isPlaying)} className="p-4 bg-purple-500 hover:bg-purple-600 rounded-full transition-colors" aria-label="Play/Pause">
              {isPlaying ? <Pause size={24} className="text-white" /> : <Play size={24} className="text-white" />}
            </button>
            <button className="p-3 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Next Chapter"><SkipForward size={20} className="text-gray-400" /></button>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => setIsMuted(!isMuted)} className="p-2 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Mute/Unmute">
              {isMuted ? <VolumeX size={20} className="text-gray-400" /> : <Volume2 size={20} className="text-gray-400" />}
            </button>
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(parseInt(e.target.value))}
              className="w-24 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-purple-500"
            />
            <span className="text-sm text-gray-400 w-12" aria-label="Volume Percentage">{volume}%</span>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Chapters</h3>
          </div>
          <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
            {audiobook.chapters.map((chapter, idx) => (
              <button
                key={chapter.id}
                onClick={() => setCurrentChapter(idx)}
                className={`w-full p-4 text-left hover:bg-gray-750 transition-colors ${idx === currentChapter ? 'bg-gray-750' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${idx === currentChapter ? 'bg-purple-500 text-white' : 'bg-gray-700 text-gray-400'}`}>{idx === currentChapter && isPlaying ? <Pause size={16} /> : <Play size={16} />}</div>
                  <div className="flex-1">
                    <div className="font-medium text-white mb-1">{chapter.title}</div>
                    <div className="text-sm text-gray-400">{chapter.duration}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Files Covered</h3>
          </div>
          <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
            {audiobook.chapters[currentChapter].files.map((file, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-gray-750 rounded-lg">
                <FileCode size={16} className="text-purple-400 flex-shrink-0" />
                <span className="text-sm text-gray-300 font-mono truncate">{file}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Settings Page
const SettingsPage: React.FC = () => {
  const [name, setName] = useState(mockUser.name);
  const [email, setEmail] = useState(mockUser.email);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [processingNotifications, setProcessingNotifications] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700"><h2 className="text-xl font-semibold text-white">Profile Settings</h2></div>
        <div className="p-6 space-y-6">
          <div><label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label><input type="text" value={name} onChange={(e) => setName(e.target.value)} className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500" /></div>
          <div><label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500" /></div>
          <div className="flex items-center justify-between">
            <div><div className="text-sm font-medium text-gray-300 mb-1">Current Plan</div><PlanBadge plan={mockUser.plan} /></div>
            <div className="text-sm text-gray-400">Member since {new Date(mockUser.createdAt).toLocaleDateString()}</div>
          </div>
        </div>
      </div>
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700"><h2 className="text-xl font-semibold text-white">Notification Preferences</h2></div>
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div><div className="text-sm font-medium text-white mb-1">Email Notifications</div><div className="text-xs text-gray-400">Receive updates about your account</div></div>
            <button onClick={() => setEmailNotifications(!emailNotifications)} className={`relative w-12 h-6 rounded-full transition-colors ${emailNotifications ? 'bg-purple-500' : 'bg-gray-700'}`}><div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${emailNotifications ? 'translate-x-7' : 'translate-x-1'}`} /></button>
          </div>
          <div className="flex items-center justify-between">
            <div><div className="text-sm font-medium text-white mb-1">Processing Notifications</div><div className="text-xs text-gray-400">Get notified when audiobooks are complete</div></div>
            <button onClick={() => setProcessingNotifications(!processingNotifications)} className={`relative w-12 h-6 rounded-full transition-colors ${processingNotifications ? 'bg-purple-500' : 'bg-gray-700'}`}><div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${processingNotifications ? 'translate-x-7' : 'translate-x-1'}`} /></button>
          </div>
        </div>
      </div>
      <div className="flex justify-end"><button onClick={handleSave} className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">{saved ? (<><Check size={18} />Saved!</>) : 'Save Changes'}</button></div>
    </div>
  );
};

// Billing Page
const BillingPage: React.FC = () => {
  const daysUntilReset = Math.ceil((new Date(mockBilling.nextBillingDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
  const usagePercentage = (mockBilling.creditsUsed / mockBilling.creditsTotal) * 100;
  return (
    <div className="max-w-4xl space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
        <div className="flex items-start justify-between mb-6">
          <div><h2 className="text-2xl font-bold text-white mb-2">{mockBilling.plan} Plan</h2><p className="text-gray-400">${mockBilling.price}/{mockBilling.interval} • Next billing on {new Date(mockBilling.nextBillingDate).toLocaleDateString()}</p></div>
          <button className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors">Upgrade Plan</button>
        </div>
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3"><span className="text-sm font-medium text-gray-300">Credits Used</span><span className="text-sm text-white font-medium">{mockBilling.creditsUsed} / {mockBilling.creditsTotal}</span></div>
          <div className="w-full bg-gray-700 rounded-full h-3"><div className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300" style={{ width: `${usagePercentage}%` }} /></div>
          <p className="text-xs text-gray-400 mt-2">Resets in {daysUntilReset} days</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-900 rounded-lg"><div className="text-2xl font-bold text-white mb-1">100</div><div className="text-sm text-gray-400">Credits per month</div></div>
          <div className="p-4 bg-gray-900 rounded-lg"><div className="text-2xl font-bold text-white mb-1">Unlimited</div><div className="text-sm text-gray-400">Private repositories</div></div>
          <div className="p-4 bg-gray-900 rounded-lg"><div className="text-2xl font-bold text-white mb-1">Priority</div><div className="text-sm text-gray-400">Processing queue</div></div>
        </div>
      </div>
      {mockBilling.paymentMethod && (
        <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-gray-700"><h3 className="text-lg font-semibold text-white">Payment Method</h3></div>
          <div className="p-6">
            <div className="flex items-center justify-between p-4 bg-gray-900 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center"><CreditCard size={24} className="text-gray-400" /></div>
                <div>
                  <div className="text-sm font-medium text-white mb-1">{mockBilling.paymentMethod.brand} •••• {mockBilling.paymentMethod.last4}</div>
                  <div className="text-xs text-gray-400">Expires {mockBilling.paymentMethod.expiryMonth}/{mockBilling.paymentMethod.expiryYear}</div>
                </div>
              </div>
              <button className="px-4 py-2 text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors">Update</button>
            </div>
          </div>
        </div>
      )}
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700"><h3 className="text-lg font-semibold text-white">Billing History</h3></div>
        <div className="divide-y divide-gray-700">
          {mockInvoices.map((invoice) => (
            <div key={invoice.id} className="p-6 flex items-center justify-between hover:bg-gray-750 transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center"><Calendar size={20} className="text-gray-400" /></div>
                <div>
                  <div className="text-sm font-medium text-white mb-1">{invoice.id}</div>
                  <div className="text-xs text-gray-400">{new Date(invoice.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-sm font-medium text-white">${invoice.amount.toFixed(2)}</div>
                <span className="px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-full text-xs text-green-400">{invoice.status}</span>
                <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Download Invoice"><Download size={16} className="text-gray-400" /></button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedAudiobookId, setSelectedAudiobookId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleNavigateToAudiobook = (id: string) => {
    setSelectedAudiobookId(id);
    setActiveTab('audiobook-detail');
  };

  const handleBackToAudiobooks = () => {
    setSelectedAudiobookId(null);
    setActiveTab('audiobooks');
  };

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 overflow-auto">
        <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-10 backdrop-blur-sm bg-gray-900/95">
          <div className="px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <h1 className="text-2xl font-semibold text-white">
                {activeTab === 'home' && 'Overview'}
                {activeTab === 'audiobooks' && 'Audiobooks'}
                {activeTab === 'audiobook-detail' && 'Player'}
                {activeTab === 'settings' && 'Settings'}
                {activeTab === 'billing' && 'Billing'}
              </h1>
              {(activeTab === 'home' || activeTab === 'audiobooks') && (
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    placeholder="Search repositories..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              )}
            </div>
            {activeTab !== 'audiobook-detail' && (
              <button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white px-6 py-2.5 rounded-lg font-medium flex items-center gap-2 transition-all shadow-lg shadow-purple-500/25" aria-label="Create New Audiobook">
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
