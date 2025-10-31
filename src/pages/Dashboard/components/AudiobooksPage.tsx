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
 <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
 {Array.from({ length: 3 }).map((_, index) => (
 <Skeleton key={index} className="h-32 rounded-lg" />
 ))}
 </div>
 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader>
 <CardTitle className="text-lg">Audiobooks</CardTitle>
 <CardDescription>Loading your most recent jobs…</CardDescription>
 </CardHeader>
 <CardContent className="space-y-4">
 {Array.from({ length: 3 }).map((_, index) => (
 <Skeleton key={index} className="h-20 rounded-md" />
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
 <div className="space-y-6">
 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
 <div>
 <CardTitle className="text-lg">Filters</CardTitle>
 <CardDescription>Refine the list of generated audiobooks.</CardDescription>
 </div>
 <div className="grid gap-3 sm:grid-cols-2">
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
 <p className="text-xs text-muted-foreground">
 Showing {filteredAudiobooks.length} of {audiobooks.length} audiobooks
 </p>
 </div>
 </CardContent>
 </Card>
 <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
 {filteredAudiobooks.map((book: Job) => (
 <Card
 key={book.id}
 className="group h-full cursor-pointer rounded-lg border border-border bg-surface transition-colors hover:bg-surface/70"
 onClick={() => onNavigateToAudiobook(book.id)}
 >
 <CardHeader className="flex items-start justify-between gap-4">
 <div className="flex items-center gap-3">
 <div className="flex h-12 w-12 items-center justify-center rounded-md bg-primary/10 text-primary">
 <GitBranch className="h-5 w-5" />
 </div>
 <div className="min-w-0">
 <CardTitle className="truncate text-base font-semibold text-text">{book.repo_name}</CardTitle>
 <CardDescription className="text-sm text-muted-foreground">
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
 <Badge key={`${book.id}-${framework}`} variant="outline" className="rounded-md text-xs">
 {framework}
 </Badge>
 ))}
 </div>
 )}
 {book.status !== 'completed' && book.status !== 'failed' && (
 <div className="space-y-2">
 <div className="flex items-center justify-between text-xs text-muted-foreground">
 <span>Processing</span>
 <span className="font-medium text-text">{book.progress_percentage}%</span>
 </div>
 <div className="h-2 rounded-full bg-border/50">
 <div
 className="h-full rounded-full bg-primary"
 style={{ width: `${book.progress_percentage}%` }}
 />
 </div>
 </div>
 )}
 <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-muted-foreground">
 <div className="flex flex-wrap items-center gap-4">
 {book.estimated_duration_minutes && (
 <span className="inline-flex items-center gap-1 font-medium text-text">
 <Clock className="h-4 w-4" />
 {formatDuration(book.estimated_duration_minutes)}
 </span>
 )}
 {book.estimated_chapters && (
 <Badge variant="outline" className="rounded-md text-xs">
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
 <div className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-xs text-danger">
 <div className="flex items-start gap-2">
 <AlertCircle className="mt-0.5 h-4 w-4" />
 <span>{book.error_message}</span>
 </div>
 </div>
 )}
 </CardContent>
 </Card>
 ))}
 </div>
 {filteredAudiobooks.length === 0 && (
 <Card className="rounded-lg border border-border bg-surface text-center">
 <CardContent className="space-y-4 py-12">
 <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-muted/20">
 <Library className="h-8 w-8 text-muted-foreground" />
 </div>
 <div className="space-y-2">
 <h3 className="text-lg font-semibold text-text">No audiobooks found</h3>
 <p className="text-sm text-muted-foreground">Try a different search term or adjust the filters.</p>
 </div>
 </CardContent>
 </Card>
 )}
 </div>
 );
};
