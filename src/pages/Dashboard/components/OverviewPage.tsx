import React from 'react';
import {
  Library,
  Clock,
  Headphones,
  CheckCircle,
  FileCode,
  ChevronRight,
  AlertCircle
} from 'lucide-react';
import { useAudiobooks, useUser } from '../hooks';
import { StatusBadge } from './StatusBadge';
import { formatDate, formatDuration, calculateTotalHours } from '../utils';
import type { Job } from '../../../lib/types';

interface OverviewPageProps {
  onNavigateToAudiobook: (id: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigateToAudiobook }) => {
  const { data: audiobooksData, isLoading } = useAudiobooks();
  const { data: user } = useUser();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const audiobooks = audiobooksData?.jobs || [];
  const completedBooks = audiobooks.filter((a: Job) => a.status === 'completed');
  const totalHours = calculateTotalHours(completedBooks);

  // Mock usage data - replace with real analytics when available
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

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border border-border rounded-xl p-6 hover:border-border/80 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <div className="text-muted-foreground">
              <Library size={24} />
            </div>
            <div className="text-sm text-success flex items-center gap-1">
              <CheckCircle size={14} />
              +12%
            </div>
          </div>
          <div className="text-3xl font-bold text-foreground mb-1">{audiobooks.length}</div>
          <div className="text-sm text-muted-foreground">Total Audiobooks</div>
          <div className="text-xs text-muted-foreground/70 mt-1">{completedBooks.length} completed</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-6 hover:border-border/80 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <div className="text-muted-foreground">
              <Clock size={24} />
            </div>
          </div>
          <div className="text-3xl font-bold text-foreground mb-1">{totalHours.toFixed(1)}h</div>
          <div className="text-sm text-muted-foreground">Hours Generated</div>
          <div className="text-xs text-muted-foreground/70 mt-1">Total audio content</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-6 hover:border-border/80 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <div className="text-muted-foreground">
              <Headphones size={24} />
            </div>
          </div>
          <div className="text-3xl font-bold text-foreground mb-1">{user?.credits_remaining || 0}</div>
          <div className="text-sm text-muted-foreground">Credits Remaining</div>
          <div className="text-xs text-muted-foreground/70 mt-1">Available to use</div>
        </div>
      </div>
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">Usage This Week</h3>
        <div className="flex items-end justify-between gap-3 h-40">
          {usageData.map((data, index) => (
            <div key={index} className="flex-1 flex flex-col items-center gap-3">
              <div
                className="w-full bg-gradient-to-t from-primary to-accent rounded-t hover:from-primary/90 hover:to-accent/90 transition-all cursor-pointer relative group"
                style={{ height: `${(data.count / maxCount) * 100}%`, minHeight: '12px' }}
              >
                <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-card border border-border text-foreground text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-xl">
                  {data.count} audiobooks
                </div>
              </div>
              <div className="text-xs text-muted-foreground">{data.date}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="p-6 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Recent Activity</h2>
        </div>
        <div className="divide-y divide-border">
          {audiobooks.slice(0, 5).map((job: Job) => (
            <div
              key={job.id}
              className="p-6 hover:bg-muted/30 transition-colors cursor-pointer"
              onClick={() => onNavigateToAudiobook(job.id)}
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileCode className="text-primary-foreground" size={24} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-medium text-foreground truncate">{job.repo_name}</h3>
                    <StatusBadge status={job.status} />
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      {formatDate(job.created_at)}
                    </span>
                    {job.estimated_chapters && <span>{job.estimated_chapters} chapters</span>}
                    {job.metadata?.language && <span className="px-2 py-0.5 bg-muted rounded text-xs">{job.metadata.language}</span>}
                  </div>
                  {job.status !== 'completed' && job.status !== 'failed' && (
                    <div className="mt-3 w-full bg-muted rounded-full h-2">
                      <div className="bg-gradient-to-r from-primary to-accent h-2 rounded-full transition-all duration-300" style={{ width: `${job.progress_percentage}%` }} />
                    </div>
                  )}
                  {job.status === 'failed' && job.error_message && (
                    <div className="mt-2 text-xs text-destructive flex items-center gap-1">
                      <AlertCircle size={12} />
                      {job.error_message}
                    </div>
                  )}
                </div>
                <ChevronRight className="text-muted-foreground flex-shrink-0" size={20} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
