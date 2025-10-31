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
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Loading overview…</CardTitle>
            <CardDescription>Fetching the latest audiobooks and metrics.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="h-24 bg-surface-secondary/50" />
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  const maxCount = Math.max(...usageData.map((item) => item.count));

  return (
    <div className="space-y-8">
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-col gap-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wide text-zinc-400">Total audiobooks</CardDescription>
            <CardTitle className="text-4xl font-semibold text-zinc-50">{audiobooks.length}</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between text-sm text-zinc-400">
            <span>{completedBooks.length} completed</span>
            <Library className="h-5 w-5 text-zinc-400" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-col gap-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wide text-zinc-400">Hours generated</CardDescription>
            <CardTitle className="text-4xl font-semibold text-zinc-50">{totalHours.toFixed(1)}h</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between text-sm text-zinc-400">
            <span>Total audio content</span>
            <Clock className="h-5 w-5 text-zinc-400" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-col gap-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wide text-zinc-400">Credits remaining</CardDescription>
            <CardTitle className="text-4xl font-semibold text-zinc-50">{user?.credits_remaining ?? 0}</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between text-sm text-zinc-400">
            <span>Available credits</span>
            <Headphones className="h-5 w-5 text-zinc-400" />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="space-y-2">
          <CardTitle className="text-xl font-semibold text-zinc-50">Usage this week</CardTitle>
          <CardDescription className="text-sm text-zinc-400">Daily audiobook generation activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between gap-4">
            {usageData.map((item) => (
              <div key={item.date} className="flex flex-1 flex-col items-center gap-2">
                <div className="flex w-full flex-1 items-end">
                  <div
                    className="w-full bg-zinc-800"
                    style={{ height: `${(item.count / maxCount) * 100}%`, minHeight: '8px' }}
                  />
                </div>
                <span className="text-xs font-medium text-zinc-400 uppercase tracking-wide">{item.date}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="space-y-2">
          <CardTitle className="text-xl font-semibold text-zinc-50">Recent activity</CardTitle>
          <CardDescription className="text-sm text-zinc-400">Your latest audiobook projects</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {audiobooks.length === 0 ? (
            <div className="bg-zinc-900 px-6 py-8 text-center text-sm text-zinc-400">
              No audiobooks yet. Start by submitting a repository.
            </div>
          ) : (
            <div>
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
                      className="cursor-pointer transition-colors hover:bg-zinc-900/50"
                      onClick={() => onNavigateToAudiobook(job.id)}
                    >
                      <TableCell>
                        <div className="flex items-center gap-4">
                          <div className="flex h-10 w-10 items-center justify-center bg-zinc-900 text-zinc-400">
                            <FileCode className="h-4 w-4" />
                          </div>
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-zinc-50">{job.repo_name}</p>
                            <p className="text-xs text-zinc-400">{job.metadata?.language ?? 'Unknown'}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="align-middle"><StatusBadge status={job.status} /></TableCell>
                      <TableCell className="text-sm text-zinc-400 font-normal">{formatDate(job.created_at)}</TableCell>
                      <TableCell>
                        {job.estimated_chapters ? (
                          <Badge variant="outline" className="text-xs font-medium">
                            {job.estimated_chapters} chapters
                          </Badge>
                        ) : (
                          <span className="text-xs text-zinc-400 font-normal">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right text-sm text-zinc-400 font-normal">
                        {job.estimated_duration_minutes ? (
                          formatDuration(job.estimated_duration_minutes)
                        ) : (
                          <span className="inline-flex items-center gap-1 text-xs text-zinc-400">
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
