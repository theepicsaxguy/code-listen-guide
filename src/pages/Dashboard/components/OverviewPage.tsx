import React, { useMemo } from 'react';
import { Library, Clock, Headphones, FileCode, AlertCircle } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

import { useAudiobooks, useUser } from '../hooks';
import { StatusBadge } from './StatusBadge';
import { formatDate, formatDuration, calculateTotalHours } from '../utils';
import type { Job } from '../../../lib/types';

interface OverviewPageProps {
 onNavigateToAudiobook: (id: string) => void;
}

const usageData = [
 { date: 'Oct 21', count: 2 },
 { date: 'Oct 22', count: 3 },
 { date: 'Oct 23', count: 4 },
 { date: 'Oct 24', count: 3 },
 { date: 'Oct 25', count: 5 },
 { date: 'Oct 26', count: 4 },
 { date: 'Oct 27', count: 3 },
];

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigateToAudiobook }) => {
 const { data: audiobooksData, isLoading } = useAudiobooks();
 const { data: user } = useUser();

 const audiobooks = audiobooksData?.jobs || [];
 const completedBooks = useMemo(
 () => audiobooks.filter((item: Job) => item.status === 'completed'),
 [audiobooks],
 );
 const totalHours = calculateTotalHours(completedBooks);

 if (isLoading) {
 return (
 <div className="space-y-4">
 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader>
 <CardTitle className="text-lg">Loading overview…</CardTitle>
 <CardDescription>Fetching the latest audiobooks and metrics.</CardDescription>
 </CardHeader>
 <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
 {Array.from({ length: 3 }).map((_, index) => (
 <div key={index} className="h-24 rounded-lg bg-muted/20" />
 ))}
 </CardContent>
 </Card>
 </div>
 );
 }

 const maxCount = Math.max(...usageData.map((item) => item.count));

 return (
 <div className="space-y-6">
 <div className="grid gap-4 md:grid-cols-3">
 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader className="flex flex-col gap-1">
 <CardDescription>Total audiobooks</CardDescription>
 <CardTitle className="text-2xl font-semibold text-text">{audiobooks.length}</CardTitle>
 </CardHeader>
 <CardContent className="flex items-center justify-between text-xs text-muted-foreground">
 <span>{completedBooks.length} completed</span>
 <Library className="h-5 w-5 text-muted-foreground" />
 </CardContent>
 </Card>
 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader className="flex flex-col gap-1">
 <CardDescription>Hours generated</CardDescription>
 <CardTitle className="text-2xl font-semibold text-text">{totalHours.toFixed(1)}h</CardTitle>
 </CardHeader>
 <CardContent className="flex items-center justify-between text-xs text-muted-foreground">
 <span>Total audio content</span>
 <Clock className="h-5 w-5 text-muted-foreground" />
 </CardContent>
 </Card>
 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader className="flex flex-col gap-1">
 <CardDescription>Credits remaining</CardDescription>
 <CardTitle className="text-2xl font-semibold text-text">{user?.credits_remaining ?? 0}</CardTitle>
 </CardHeader>
 <CardContent className="flex items-center justify-between text-xs text-muted-foreground">
 <span>Available credits</span>
 <Headphones className="h-5 w-5 text-muted-foreground" />
 </CardContent>
 </Card>
 </div>

 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader className="space-y-1">
 <CardTitle className="text-lg font-semibold text-text">Usage this week</CardTitle>
 <CardDescription>Daily audiobook generation activity</CardDescription>
 </CardHeader>
 <CardContent>
 <div className="flex items-end justify-between gap-3">
 {usageData.map((item) => (
 <div key={item.date} className="flex flex-1 flex-col items-center gap-2">
 <div className="flex w-full flex-1 items-end">
 <div
 className="w-full rounded-md bg-primary/25"
 style={{ height: `${(item.count / maxCount) * 100}%`, minHeight: '8px' }}
 />
 </div>
 <span className="text-xs font-medium text-muted-foreground">{item.date}</span>
 </div>
 ))}
 </div>
 </CardContent>
 </Card>

 <Card className="rounded-lg border border-border bg-surface">
 <CardHeader className="space-y-1">
 <CardTitle className="text-lg font-semibold text-text">Recent activity</CardTitle>
 <CardDescription>Your latest audiobook projects</CardDescription>
 </CardHeader>
 <CardContent className="space-y-4">
 {audiobooks.length === 0 ? (
 <div className="rounded-lg border border-border bg-muted/10 px-4 py-6 text-center text-sm text-muted-foreground">
 No audiobooks yet. Start by submitting a repository.
 </div>
 ) : (
 <div className="rounded-lg border border-border">
 <Table>
 <TableHeader>
 <TableRow>
 <TableHead className="w-1/3">Repository</TableHead>
 <TableHead>Status</TableHead>
 <TableHead>Created</TableHead>
 <TableHead>Chapters</TableHead>
 <TableHead className="text-right">Duration</TableHead>
 </TableRow>
 </TableHeader>
 <TableBody>
 {audiobooks.slice(0, 5).map((job: Job) => (
 <TableRow
 key={job.id}
 className="cursor-pointer transition-colors hover:bg-accent/30"
 onClick={() => onNavigateToAudiobook(job.id)}
 >
 <TableCell>
 <div className="flex items-center gap-3">
 <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
 <FileCode className="h-4 w-4" />
 </div>
 <div className="min-w-0">
 <p className="truncate text-sm font-semibold text-text">{job.repo_name}</p>
 <p className="text-xs text-muted-foreground">{job.metadata?.language ?? 'Unknown'}</p>
 </div>
 </div>
 </TableCell>
 <TableCell className="align-middle"><StatusBadge status={job.status} /></TableCell>
 <TableCell className="text-sm text-muted-foreground">{formatDate(job.created_at)}</TableCell>
 <TableCell>
 {job.estimated_chapters ? (
 <Badge variant="outline" className="rounded-md text-xs">
 {job.estimated_chapters} chapters
 </Badge>
 ) : (
 <span className="text-xs text-muted-foreground">—</span>
 )}
 </TableCell>
 <TableCell className="text-right text-sm text-muted-foreground">
 {job.estimated_duration_minutes ? (
 formatDuration(job.estimated_duration_minutes)
 ) : (
 <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
 <AlertCircle className="h-3 w-3" />
 Pending
 </span>
 )}
 </TableCell>
 </TableRow>
 ))}
 </TableBody>
 </Table>
 </div>
 )}
 </CardContent>
 </Card>
 </div>
 );
};
