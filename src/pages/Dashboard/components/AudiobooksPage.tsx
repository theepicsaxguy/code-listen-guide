import React, { useMemo, useState } from 'react';
import { Clock, Library, GitBranch, AlertCircle, Play } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';

import { useAudiobooks } from '../hooks';
import { StatusBadge } from './StatusBadge';
import { formatDuration } from '../utils';
import type { Job } from '../../../lib/types';

interface AudiobooksPageProps {
 onNavigateToAudiobook: (id: string) => void;
 searchQuery: string;
}

export const AudiobooksPage: React.FC<AudiobooksPageProps> = ({ onNavigateToAudiobook, searchQuery }) => {
 const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');
 const [sortBy, setSortBy] = useState<'date' | 'name' | 'duration'>('date');

 const { data: audiobooksData, isLoading } = useAudiobooks();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-32" />
          ))}
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Audiobooks</CardTitle>
            <CardDescription>Loading your most recent jobs…</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-20" />
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

 const audiobooks = audiobooksData?.jobs || [];

 const filteredAudiobooks = useMemo(() => {
 return audiobooks
 .filter((book: Job) => {
 const matchesSearch = book.repo_name.toLowerCase().includes(searchQuery.toLowerCase());
 const matchesFilter =
 filterStatus === 'all' ||
 (filterStatus === 'processing' && !['completed', 'failed'].includes(book.status)) ||
 book.status === filterStatus;
 return matchesSearch && matchesFilter;
 })
 .sort((a: Job, b: Job) => {
 if (sortBy === 'date') {
 return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
 }
 if (sortBy === 'name') {
 return a.repo_name.localeCompare(b.repo_name);
 }
 if (sortBy === 'duration') {
 return (b.estimated_duration_minutes || 0) - (a.estimated_duration_minutes || 0);
 }
 return 0;
 });
 }, [audiobooks, filterStatus, searchQuery, sortBy]);

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <CardTitle className="text-xl font-semibold text-foreground">Filters</CardTitle>
            <CardDescription>Refine the list of generated audiobooks.</CardDescription>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Select value={filterStatus} onValueChange={(value) => setFilterStatus(value as typeof filterStatus)}>
              <SelectTrigger className="h-10 w-full">
                <SelectValue placeholder="Filter status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={(value) => setSortBy(value as typeof sortBy)}>
              <SelectTrigger className="h-10 w-full">
                <SelectValue placeholder="Sort" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Newest first</SelectItem>
                <SelectItem value="name">Alphabetical</SelectItem>
                <SelectItem value="duration">Longest duration</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              Showing {filteredAudiobooks.length} of {audiobooks.length} audiobooks
            </p>
          </div>
        </CardContent>
      </Card>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {filteredAudiobooks.map((book: Job) => (
          <Card
            key={book.id}
            className="group h-full cursor-pointer transition-colors hover:bg-zinc-900/30"
            onClick={() => onNavigateToAudiobook(book.id)}
          >
            <CardHeader className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center bg-zinc-900">
                  <GitBranch className="h-5 w-5 text-zinc-500 hover:text-zinc-100" />
                </div>
                <div className="min-w-0">
                  <CardTitle className="truncate text-base font-semibold text-zinc-50">{book.repo_name}</CardTitle>
                  <CardDescription className="text-sm text-zinc-500">
                    {book.metadata?.language || 'Language unknown'}
                  </CardDescription>
                </div>
              </div>
              <StatusBadge status={book.status} />
            </CardHeader>
            <CardContent className="space-y-4">
              {book.metadata?.frameworks && book.metadata.frameworks.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {book.metadata.frameworks.map((framework: string) => (
                    <Badge key={`${book.id}-${framework}`} variant="outline" className="text-xs">
                      {framework}
                    </Badge>
                  ))}
                </div>
              )}
              {book.status !== 'completed' && book.status !== 'failed' && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs text-zinc-500">
                    <span>Processing</span>
                    <span className="font-semibold text-zinc-50">{book.progress_percentage}%</span>
                  </div>
                  <div className="h-2 bg-zinc-900">
                    <div
                      className="h-full bg-zinc-700 transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]"
                      style={{ width: `${book.progress_percentage}%` }}
                    />
                  </div>
                </div>
              )}
              <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-zinc-300">
                <div className="flex flex-wrap items-center gap-4">
                  {book.estimated_duration_minutes && (
                    <span className="inline-flex items-center gap-1 font-semibold text-zinc-50">
                      <Clock className="h-4 w-4" />
                      {formatDuration(book.estimated_duration_minutes)}
                    </span>
                  )}
                  {book.estimated_chapters && (
                    <Badge variant="outline" className="text-xs">
                      {book.estimated_chapters} chapters
                    </Badge>
                  )}
                  {book.repo_size_bytes && <span>{(book.repo_size_bytes / (1024 * 1024)).toFixed(0)} MB</span>}
                </div>
                {book.status === 'completed' && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(event) => {
                      event.stopPropagation();
                      onNavigateToAudiobook(book.id);
                    }}
                    aria-label="Play audiobook"
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                )}
              </div>
              {book.status === 'failed' && book.error_message && (
                <div className="border border-zinc-800 bg-zinc-900/50 px-4 py-3 text-xs text-zinc-300">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="mt-0.5 h-4 w-4 text-zinc-500" />
                    <span>{book.error_message}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
      {filteredAudiobooks.length === 0 && (
        <Card className="text-center">
          <CardContent className="space-y-4 py-12">
            <div className="mx-auto flex h-16 w-16 items-center justify-center bg-muted/10">
              <Library className="h-8 w-8 text-muted-foreground" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-foreground">No audiobooks found</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">Try a different search term or adjust the filters.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
