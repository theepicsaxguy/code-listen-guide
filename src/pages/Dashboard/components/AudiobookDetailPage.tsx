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
 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
 </div>
 );
 }

 if (!audiobook || !playerData) {
 return (
 <div className="text-center py-12">
 <h3 className="text-lg font-medium text-muted-foreground mb-2">Audiobook not found</h3>
 <button onClick={onBack} className="text-primary hover:text-primary">
 Go back
 </button>
 </div>
 );
 }

 const chapters = playerData.chapters || [];
 const totalDuration = playerData.metadata?.total_duration_seconds || 0;

 return (
 <div className="space-y-6">
 <button onClick={onBack} className="flex items-center gap-2 text-muted-foreground hover:text-text transition-colors">
 <ChevronRight size={16} className="rotate-180" />
 Back to Audiobooks
 </button>
 <div className="bg-surface rounded-card p-8">
 <div className="flex items-start gap-6">
 <div className="w-32 h-32 bg-surface rounded-card flex items-center justify-center flex-shrink-0">
 <GitBranch className="text-text" size={64} />
 </div>
 <div className="flex-1">
 <div className="flex items-start justify-between mb-3">
 <div>
 <h1 className="text-3xl font-bold text-text mb-2">{audiobook.repo_name}</h1>
 <p className="text-muted-foreground mb-4">{audiobook.repo_url}</p>
 </div>
 <div className="flex items-center gap-2">
 <button onClick={handleCopyUrl} className="p-2 hover:bg-surface/70 rounded-card transition-colors" title="Copy link">
 {copied ? <Check size={20} className="text-success" /> : <Copy size={20} className="text-muted-foreground" />}
 </button>
 <button className="p-2 hover:bg-surface/70 rounded-card transition-colors" title="Share"><Share2 size={20} className="text-muted-foreground" /></button>
 <button className="p-2 hover:bg-surface/70 rounded-card transition-colors" title="Download"><Download size={20} className="text-muted-foreground" /></button>
 </div>
 </div>
 <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
 <span className="flex items-center gap-1"><Clock size={16} />{formatDuration(totalDuration)}</span>
 <span>{chapters.length} chapters</span>
 {audiobook.file_count && <span>{audiobook.file_count} files</span>}
 {audiobook.metadata?.language && <span className="px-2 py-1 bg-surface/60 rounded text-xs">{audiobook.metadata.language}</span>}
 </div>
 {audiobook.metadata?.frameworks && audiobook.metadata.frameworks.length > 0 && (
 <div className="flex flex-wrap gap-2 mt-3">
 {audiobook.metadata.frameworks.map((framework: string, idx: number) => (
 <span key={idx} className="px-3 py-1 bg-primary/20 rounded-full text-xs text-primary">{framework}</span>
 ))}
 </div>
 )}
 </div>
 </div>
 </div>
 {chapters.length > 0 && (
 <>
 <div className="bg-surface rounded-card p-6">
 <div className="flex items-center justify-between mb-4">
 <div>
 <h3 className="text-lg font-semibold text-text mb-1">Chapter {currentChapter + 1}: {chapters[currentChapter].title}</h3>
 <p className="text-sm text-muted-foreground">{chapters[currentChapter].files_covered?.length || 0} files covered</p>
 </div>
 <div className="text-sm text-muted-foreground">
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
 className="w-full h-2 bg-surface/60 rounded-card appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
 />
 </div>
 <div className="flex items-center justify-between">
 <div className="flex items-center gap-4">
 <button
 disabled={currentChapter === 0}
 onClick={() => setCurrentChapter(Math.max(0, currentChapter - 1))}
 className="p-3 hover:bg-surface/70 rounded-card transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
 aria-label="Previous Chapter"
 >
 <SkipBack size={20} className="text-muted-foreground" />
 </button>
 <button onClick={() => setIsPlaying(!isPlaying)} className="p-4 bg-primary hover:bg-primary/90 rounded-full transition-colors" aria-label="Play/Pause">
 {isPlaying ? <Pause size={24} className="text-text" /> : <Play size={24} className="text-text" />}
 </button>
 <button
 disabled={currentChapter >= chapters.length - 1}
 onClick={() => setCurrentChapter(Math.min(chapters.length - 1, currentChapter + 1))}
 className="p-3 hover:bg-surface/70 rounded-card transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
 aria-label="Next Chapter"
 >
 <SkipForward size={20} className="text-muted-foreground" />
 </button>
 </div>
 <div className="flex items-center gap-3">
 <button onClick={() => setIsMuted(!isMuted)} className="p-2 hover:bg-surface/70 rounded-card transition-colors" aria-label="Mute/Unmute">
 {isMuted ? <VolumeX size={20} className="text-muted-foreground" /> : <Volume2 size={20} className="text-muted-foreground" />}
 </button>
 <input
 type="range"
 min="0"
 max="100"
 value={volume}
 onChange={(e) => setVolume(parseInt(e.target.value))}
 className="w-24 h-1 bg-surface/60 rounded-card appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
 />
 <span className="text-sm text-muted-foreground w-12" aria-label="Volume Percentage">{volume}%</span>
 </div>
 </div>
 </div>
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
 <div className="bg-surface rounded-card overflow-hidden">
 <div className="p-6">
 <h3 className="text-lg font-semibold text-text">Chapters</h3>
 </div>
 <div className="divide-y divide-border max-h-96 overflow-y-auto">
 {chapters.map((chapter, idx) => (
 <button
 key={chapter.id}
 onClick={() => setCurrentChapter(idx)}
 className={`w-full p-4 text-left hover:bg-surface/70 transition-colors ${idx === currentChapter ? 'bg-surface/60' : ''}`}
 >
 <div className="flex items-center gap-3">
 <div className={`w-8 h-8 rounded-card flex items-center justify-center ${idx === currentChapter ? 'bg-primary text-text' : 'bg-surface/60 text-muted-foreground'}`}>
 {idx === currentChapter && isPlaying ? <Pause size={16} /> : <Play size={16} />}
 </div>
 <div className="flex-1">
 <div className="font-medium text-text mb-1">{chapter.title}</div>
 <div className="text-sm text-muted-foreground">{formatDuration(chapter.audio_duration_seconds || 0)}</div>
 </div>
 </div>
 </button>
 ))}
 </div>
 </div>
 <div className="bg-surface rounded-card overflow-hidden">
 <div className="p-6">
 <h3 className="text-lg font-semibold text-text">Files Covered</h3>
 </div>
 <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
 {chapters[currentChapter].files_covered?.map((file, idx) => (
 <div key={idx} className="flex items-center gap-3 p-3 bg-surface/60 rounded-card">
 <FileCode size={16} className="text-primary flex-shrink-0" />
 <span className="text-sm text-muted-foreground font-mono truncate">{file}</span>
 </div>
 )) || <p className="text-muted-foreground text-sm">No files information available</p>}
 </div>
 </div>
 </div>
 </>
 )}
 </div>
 );
};
