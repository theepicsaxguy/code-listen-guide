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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
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
        {filteredAudiobooks.map((book: Job) => (
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
                  <h3 className="font-semibold text-white group-hover:text-purple-400 transition-colors">{book.repo_name}</h3>
                  <p className="text-sm text-gray-400">{book.metadata?.language || 'Unknown'}</p>
                </div>
              </div>
              <StatusBadge status={book.status} />
            </div>
            {book.metadata?.frameworks && book.metadata.frameworks.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {book.metadata.frameworks.map((framework: string, idx: number) => (
                  <span key={idx} className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">{framework}</span>
                ))}
              </div>
            )}
            {book.status !== 'completed' && book.status !== 'failed' && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2 text-sm">
                  <span className="text-gray-400">Processing...</span>
                  <span className="text-white font-medium">{book.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300" style={{ width: `${book.progress_percentage}%` }} />
                </div>
              </div>
            )}
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-4 text-gray-400">
                {book.estimated_duration_minutes && (
                  <span className="flex items-center gap-1"><Clock size={14} />{Math.floor(book.estimated_duration_minutes / 60)}h {book.estimated_duration_minutes % 60}m</span>
                )}
                {book.estimated_chapters && <span>{book.estimated_chapters} chapters</span>}
                {book.repo_size_bytes && <span>{(book.repo_size_bytes / (1024 * 1024)).toFixed(0)} MB</span>}
              </div>
              {book.status === 'completed' && (
                <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Play audiobook">
                  <Play size={16} className="text-purple-400" />
                </button>
              )}
            </div>
            {book.status === 'failed' && book.error_message && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-xs text-red-400 flex items-center gap-2"><AlertCircle size={14} />{book.error_message}</p>
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
