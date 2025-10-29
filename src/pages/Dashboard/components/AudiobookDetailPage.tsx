import React, { useState } from 'react';
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  Volume2,
  VolumeX,
  Download,
  ChevronRight,
  GitBranch,
  Clock,
  Copy,
  Check,
  Share2,
  FileCode
} from 'lucide-react';
import { useAudiobook, useAudiobookChapters } from '../hooks';
import { formatTime, formatDuration } from '../utils';
import { copyToClipboard } from '@/lib/error-utils';

interface AudiobookDetailPageProps {
  audiobookId: string;
  onBack: () => void;
}

export const AudiobookDetailPage: React.FC<AudiobookDetailPageProps> = ({ audiobookId, onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentChapter, setCurrentChapter] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(75);
  const [isMuted, setIsMuted] = useState(false);
  const [copied, setCopied] = useState(false);

  const { data: audiobook, isLoading: isLoadingJob } = useAudiobook(audiobookId);
  const { data: playerData, isLoading: isLoadingChapters } = useAudiobookChapters(audiobookId);

  const handleCopyUrl = async () => {
    if (typeof window !== 'undefined') {
      const success = await copyToClipboard(window.location.href);
      if (success) {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    }
  };

  if (isLoadingJob || isLoadingChapters) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (!audiobook || !playerData) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-400 mb-2">Audiobook not found</h3>
        <button onClick={onBack} className="text-purple-400 hover:text-purple-300">
          Go back
        </button>
      </div>
    );
  }

  const chapters = playerData.chapters || [];
  const totalDuration = playerData.metadata?.total_duration_seconds || 0;

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
                <h1 className="text-3xl font-bold text-white mb-2">{audiobook.repo_name}</h1>
                <p className="text-gray-400 mb-4">{audiobook.repo_url}</p>
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
              <span className="flex items-center gap-1"><Clock size={16} />{formatDuration(totalDuration)}</span>
              <span>{chapters.length} chapters</span>
              {audiobook.file_count && <span>{audiobook.file_count} files</span>}
              {audiobook.metadata?.language && <span className="px-2 py-1 bg-gray-700 rounded text-xs">{audiobook.metadata.language}</span>}
            </div>
            {audiobook.metadata?.frameworks && audiobook.metadata.frameworks.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {audiobook.metadata.frameworks.map((framework: string, idx: number) => (
                  <span key={idx} className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs text-purple-400">{framework}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      {chapters.length > 0 && (
        <>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">Chapter {currentChapter + 1}: {chapters[currentChapter].title}</h3>
                <p className="text-sm text-gray-400">{chapters[currentChapter].files_covered?.length || 0} files covered</p>
              </div>
              <div className="text-sm text-gray-400">
                {formatTime(currentTime)} / {formatDuration(chapters[currentChapter].audio_duration_seconds || 0)}
              </div>
            </div>
            <div className="mb-6">
              <input
                type="range"
                min="0"
                max="100"
                value={(currentTime / (chapters[currentChapter].audio_duration_seconds || 1)) * 100}
                onChange={(e) => setCurrentTime((parseInt(e.target.value) / 100) * (chapters[currentChapter].audio_duration_seconds || 0))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-purple-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  disabled={currentChapter === 0}
                  onClick={() => setCurrentChapter(Math.max(0, currentChapter - 1))}
                  className="p-3 hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Previous Chapter"
                >
                  <SkipBack size={20} className="text-gray-400" />
                </button>
                <button onClick={() => setIsPlaying(!isPlaying)} className="p-4 bg-purple-500 hover:bg-purple-600 rounded-full transition-colors" aria-label="Play/Pause">
                  {isPlaying ? <Pause size={24} className="text-white" /> : <Play size={24} className="text-white" />}
                </button>
                <button
                  disabled={currentChapter >= chapters.length - 1}
                  onClick={() => setCurrentChapter(Math.min(chapters.length - 1, currentChapter + 1))}
                  className="p-3 hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Next Chapter"
                >
                  <SkipForward size={20} className="text-gray-400" />
                </button>
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
                {chapters.map((chapter, idx) => (
                  <button
                    key={chapter.id}
                    onClick={() => setCurrentChapter(idx)}
                    className={`w-full p-4 text-left hover:bg-gray-750 transition-colors ${idx === currentChapter ? 'bg-gray-750' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${idx === currentChapter ? 'bg-purple-500 text-white' : 'bg-gray-700 text-gray-400'}`}>
                        {idx === currentChapter && isPlaying ? <Pause size={16} /> : <Play size={16} />}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-white mb-1">{chapter.title}</div>
                        <div className="text-sm text-gray-400">{formatDuration(chapter.audio_duration_seconds || 0)}</div>
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
                {chapters[currentChapter].files_covered?.map((file, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-gray-750 rounded-lg">
                    <FileCode size={16} className="text-purple-400 flex-shrink-0" />
                    <span className="text-sm text-gray-300 font-mono truncate">{file}</span>
                  </div>
                )) || <p className="text-gray-400 text-sm">No files information available</p>}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
