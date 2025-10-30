import React, { useState } from 'react';
import { Search, Clock, Library, GitBranch, AlertCircle, Play } from 'lucide-react';
import { useAudiobooks } from '../hooks';
import { StatusBadge } from './StatusBadge';
import { formatDuration } from '../utils';
import type { Job } from '../../../lib/types';

interface AudiobooksPageProps {
  onNavigateToAudiobook: (id: string) => void;
}

export const AudiobooksPage: React.FC<AudiobooksPageProps> = ({ onNavigateToAudiobook }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'duration'>('date');

  const { data: audiobooksData, isLoading } = useAudiobooks();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const audiobooks = audiobooksData?.jobs || [];

  const filteredAudiobooks = audiobooks
    .filter((book: Job) => {
      const matchesSearch = book.repo_name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter =
        filterStatus === 'all' ||
        (filterStatus === 'processing' && !['completed', 'failed'].includes(book.status)) ||
        book.status === filterStatus;
      return matchesSearch && matchesFilter;
    })
    .sort((a: Job, b: Job) => {
      if (sortBy === 'date') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      if (sortBy === 'name') return a.repo_name.localeCompare(b.repo_name);
      return 0;
    });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
          <input
            type="text"
            placeholder="Search audiobooks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-card border border-border/50 rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all hover:border-border"
          />
        </div>
        <div className="flex gap-3">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-4 py-3 bg-card border border-border/50 rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all hover:border-border"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-4 py-3 bg-card border border-border/50 rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all hover:border-border"
          >
            <option value="date">Sort by Date</option>
            <option value="name">Sort by Name</option>
            <option value="duration">Sort by Duration</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredAudiobooks.map((book: Job) => (
          <div
            key={book.id}
            className="bg-gradient-card border border-border/50 rounded-xl p-6 transition-all cursor-pointer group hover-card card-elevation relative overflow-hidden"
            onClick={() => onNavigateToAudiobook(book.id)}
          >
            <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-3 transition-opacity" />
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 group-hover:scale-105 transition-transform">
                    <GitBranch className="text-primary-foreground" size={28} />
                  </div>
                  <div>
                    <h3 className="font-bold text-foreground text-lg group-hover:text-primary transition-colors mb-1">{book.repo_name}</h3>
                    <p className="text-sm text-muted-foreground font-medium">{book.metadata?.language || 'Unknown'}</p>
                  </div>
                </div>
                <StatusBadge status={book.status} />
              </div>
              {book.metadata?.frameworks && book.metadata.frameworks.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {book.metadata.frameworks.map((framework: string, idx: number) => (
                    <span key={idx} className="px-2.5 py-1 bg-muted/50 rounded-md text-xs font-semibold text-muted-foreground border border-border/30">{framework}</span>
                  ))}
                </div>
              )}
              {book.status !== 'completed' && book.status !== 'failed' && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2 text-sm">
                    <span className="text-muted-foreground font-medium">Processing...</span>
                    <span className="text-foreground font-bold">{book.progress_percentage}%</span>
                  </div>
                  <div className="w-full bg-muted/50 rounded-full h-2.5 overflow-hidden">
                    <div className="bg-gradient-to-r from-primary to-accent h-full rounded-full transition-all duration-500 shadow-sm shadow-primary/30" style={{ width: `${book.progress_percentage}%` }} />
                  </div>
                </div>
              )}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-4 text-muted-foreground flex-wrap">
                  {book.estimated_duration_minutes && (
                    <span className="flex items-center gap-1.5 font-medium">
                      <Clock size={14} />
                      {Math.floor(book.estimated_duration_minutes / 60)}h {book.estimated_duration_minutes % 60}m
                    </span>
                  )}
                  {book.estimated_chapters && (
                    <span className="px-2.5 py-1 bg-muted/50 rounded-md font-medium">
                      {book.estimated_chapters} chapters
                    </span>
                  )}
                  {book.repo_size_bytes && (
                    <span className="text-xs">
                      {(book.repo_size_bytes / (1024 * 1024)).toFixed(0)} MB
                    </span>
                  )}
                </div>
                {book.status === 'completed' && (
                  <button 
                    className="p-2.5 hover:bg-accent/20 rounded-xl transition-all group/play hover:scale-110" 
                    aria-label="Play audiobook"
                    onClick={(e) => {
                      e.stopPropagation();
                      onNavigateToAudiobook(book.id);
                    }}
                  >
                    <Play size={18} className="text-primary group-hover/play:text-accent transition-colors" />
                  </button>
                )}
              </div>
              {book.status === 'failed' && book.error_message && (
                <div className="mt-4 p-3 bg-destructive/10 border border-destructive/30 rounded-lg">
                  <p className="text-xs text-destructive flex items-center gap-2 font-medium">
                    <AlertCircle size={14} />
                    {book.error_message}
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      {filteredAudiobooks.length === 0 && (
        <div className="text-center py-16 bg-gradient-card border border-border/50 rounded-xl card-elevation">
          <div className="w-20 h-20 bg-muted/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <Library size={40} className="text-muted-foreground" />
          </div>
          <h3 className="text-xl font-bold text-foreground mb-2">No audiobooks found</h3>
          <p className="text-sm text-muted-foreground">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
};
