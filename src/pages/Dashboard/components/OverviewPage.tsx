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
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-stat rounded-xl p-6 transition-all border border-border/50 hover-card card-elevation group relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-5 transition-opacity" />
          <div className="flex items-center justify-between mb-4 relative z-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-primary/20 flex items-center justify-center shadow-lg shadow-primary/10">
              <Library className="icon-gradient" size={24} />
            </div>
            <div className="text-sm text-success flex items-center gap-1.5 font-semibold bg-success/10 px-2.5 py-1 rounded-full">
              <CheckCircle size={14} />
              +12%
            </div>
          </div>
          <div className="text-4xl font-bold text-foreground mb-1 relative z-10">{audiobooks.length}</div>
          <div className="text-sm font-semibold text-foreground mb-1 relative z-10">Total Audiobooks</div>
          <div className="text-xs text-muted-foreground relative z-10">{completedBooks.length} completed</div>
        </div>
        <div className="bg-gradient-stat rounded-xl p-6 transition-all border border-border/50 hover-card card-elevation group relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-5 transition-opacity" />
          <div className="flex items-center justify-between mb-4 relative z-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-accent/20 flex items-center justify-center shadow-lg shadow-accent/10">
              <Clock className="icon-gradient-accent" size={24} />
            </div>
          </div>
          <div className="text-4xl font-bold text-foreground mb-1 relative z-10">{totalHours.toFixed(1)}h</div>
          <div className="text-sm font-semibold text-foreground mb-1 relative z-10">Hours Generated</div>
          <div className="text-xs text-muted-foreground relative z-10">Total audio content</div>
        </div>
        <div className="bg-gradient-stat rounded-xl p-6 transition-all border border-border/50 hover-card card-elevation group relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-5 transition-opacity" />
          <div className="flex items-center justify-between mb-4 relative z-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-accent/20 flex items-center justify-center shadow-lg shadow-accent/10">
              <Headphones className="icon-gradient-accent" size={24} />
            </div>
          </div>
          <div className="text-4xl font-bold text-foreground mb-1 relative z-10">{user?.credits_remaining || 0}</div>
          <div className="text-sm font-semibold text-foreground mb-1 relative z-10">Credits Remaining</div>
          <div className="text-xs text-muted-foreground relative z-10">Available to use</div>
        </div>
      </div>
      <div className="bg-gradient-card rounded-xl p-8 border border-border/50 card-elevation">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-xl font-bold text-foreground mb-1">Usage This Week</h3>
            <p className="text-sm text-muted-foreground">Daily audiobook generation activity</p>
          </div>
        </div>
        <div className="flex items-end justify-between gap-4 h-48">
          {usageData.map((data, index) => (
            <div key={index} className="flex-1 flex flex-col items-center gap-4 group">
              <div className="relative w-full flex items-end justify-center">
                <div
                  className="w-full bg-gradient-to-t from-primary via-primary/90 to-accent rounded-t-xl hover:from-primary/95 hover:to-accent/95 transition-all cursor-pointer relative group/bar min-h-[8px] shadow-lg shadow-primary/20"
                  style={{ height: `${(data.count / maxCount) * 100}%`, minHeight: '8px' }}
                >
                  <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-card border border-border/50 text-foreground text-xs font-semibold px-3 py-1.5 rounded-lg opacity-0 group-hover/bar:opacity-100 transition-all whitespace-nowrap shadow-xl card-elevation pointer-events-none z-20">
                    {data.count} audiobooks
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-2 h-2 bg-card border-r border-b border-border/50 rotate-45" />
                  </div>
                </div>
              </div>
              <div className="text-xs font-medium text-muted-foreground">{data.date}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-gradient-card rounded-xl border border-border/50 overflow-hidden card-elevation">
        <div className="p-6 border-b border-border/30 bg-card/50">
          <h2 className="text-xl font-bold text-foreground">Recent Activity</h2>
          <p className="text-sm text-muted-foreground mt-1">Your latest audiobook projects</p>
        </div>
        <div>
          {audiobooks.slice(0, 5).map((job: Job, index: number) => (
            <div
              key={job.id}
              className="p-6 hover:bg-card/50 transition-all cursor-pointer border-b border-border/20 last:border-b-0 group hover-card"
              onClick={() => onNavigateToAudiobook(job.id)}
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-primary rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/20 group-hover:scale-105 transition-transform">
                  <FileCode className="text-primary-foreground" size={28} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <h3 className="font-bold text-foreground truncate text-lg">{job.repo_name}</h3>
                    <StatusBadge status={job.status} />
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
                    <span className="flex items-center gap-1.5 font-medium">
                      <Clock size={14} />
                      {formatDate(job.created_at)}
                    </span>
                    {job.estimated_chapters && (
                      <span className="px-2.5 py-1 bg-muted/50 rounded-md font-medium">
                        {job.estimated_chapters} chapters
                      </span>
                    )}
                    {job.metadata?.language && (
                      <span className="px-2.5 py-1 bg-primary/10 text-primary rounded-md text-xs font-semibold border border-primary/20">
                        {job.metadata.language}
                      </span>
                    )}
                  </div>
                  {job.status !== 'completed' && job.status !== 'failed' && (
                    <div className="mt-4 w-full bg-muted/50 rounded-full h-2.5 overflow-hidden">
                      <div className="bg-gradient-to-r from-primary to-accent h-full rounded-full transition-all duration-500 shadow-sm shadow-primary/30" style={{ width: `${job.progress_percentage}%` }} />
                    </div>
                  )}
                  {job.status === 'failed' && job.error_message && (
                    <div className="mt-3 p-3 bg-destructive/10 border border-destructive/30 rounded-lg">
                      <div className="text-xs text-destructive flex items-center gap-2 font-medium">
                        <AlertCircle size={14} />
                        {job.error_message}
                      </div>
                    </div>
                  )}
                </div>
                <ChevronRight className="text-muted-foreground flex-shrink-0 group-hover:text-foreground group-hover:translate-x-1 transition-all" size={20} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
