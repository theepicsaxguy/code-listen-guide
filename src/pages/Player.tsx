import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useGetAudiobookPlayerDataApiV1PlayerJobIdGet } from '@/lib/api/generated';
import type { GetAudiobookPlayerDataApiV1PlayerJobIdGet200 } from '@/lib/api/generated';
import { PlayerData, Chapter } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { useToast } from '@/hooks/use-toast';
import { 
  Play, Pause, SkipForward, SkipBack, 
  Volume2, VolumeX, Loader2, List, X 
} from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';

export default function Player() {
  const { jobId } = useParams<{ jobId: string }>();
  const { toast } = useToast();
  const audioRef = useRef<HTMLAudioElement>(null);
  
  const { data: playerDataResponse, isLoading } = useGetAudiobookPlayerDataApiV1PlayerJobIdGet(
    jobId || '',
    { query: { enabled: !!jobId } }
  );
  
  const playerData = playerDataResponse as unknown as PlayerData | null;
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      // Auto-advance to next chapter
      if (playerData && currentChapterIndex < playerData.chapters.length - 1) {
        setCurrentChapterIndex(currentChapterIndex + 1);
      }
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [playerData, currentChapterIndex]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const skipTime = (seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(duration, audio.currentTime + seconds));
  };

  const handleSeek = (value: number[]) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = value[0];
    setCurrentTime(value[0]);
  };

  const handleVolumeChange = (value: number[]) => {
    const audio = audioRef.current;
    if (!audio) return;
    const newVolume = value[0];
    audio.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    if (isMuted) {
      audio.volume = volume || 0.5;
      setIsMuted(false);
    } else {
      audio.volume = 0;
      setIsMuted(true);
    }
  };

  const changePlaybackRate = () => {
    const rates = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
    const currentIndex = rates.indexOf(playbackRate);
    const nextIndex = (currentIndex + 1) % rates.length;
    const newRate = rates[nextIndex];
    
    if (audioRef.current) {
      audioRef.current.playbackRate = newRate;
    }
    setPlaybackRate(newRate);
  };

  const jumpToChapter = (index: number) => {
    if (!playerData || !audioRef.current) return;
    const chapter = playerData.metadata.chapters[index];
    if (chapter) {
      audioRef.current.currentTime = chapter.start_time_seconds;
      setCurrentChapterIndex(index);
    }
  };

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!playerData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card>
          <CardContent className="text-center py-12">
            <p>Audiobook not found or not ready yet</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentChapter = playerData.chapters[currentChapterIndex];

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Cover and Info */}
        <div className="flex flex-col md:flex-row gap-8 mb-12">
          <div className="w-full md:w-64 h-64 bg-muted rounded-lg flex items-center justify-center">
            {playerData.cover_url ? (
              <img 
                src={playerData.cover_url} 
                alt="Cover" 
                className="w-full h-full object-cover rounded-lg"
              />
            ) : (
              <span className="text-4xl">🎧</span>
            )}
          </div>
          
          <div className="flex-1 space-y-4">
            <div>
              <h1 className="text-4xl font-bold mb-2">{playerData.metadata.audiobook_title}</h1>
              <p className="text-muted-foreground">{playerData.job_info.repo_url}</p>
            </div>
            
            <div className="flex gap-4 text-sm">
              <span>{playerData.chapters.length} chapters</span>
              <span>•</span>
              <span>{formatTime(playerData.metadata.total_duration_seconds)}</span>
              <span>•</span>
              <span className="capitalize">{playerData.job_info.depth_tier} depth</span>
            </div>

            {currentChapter && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">
                    Chapter {currentChapter.chapter_number}: {currentChapter.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{currentChapter.description}</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Audio Player */}
        <Card>
          <CardContent className="pt-6">
            <audio
              ref={audioRef}
              src={currentChapter?.audio_url}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />

            {/* Progress Bar */}
            <div className="space-y-2 mb-6">
              <Slider
                value={[currentTime]}
                max={duration || 100}
                step={1}
                onValueChange={handleSeek}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-center gap-4 mb-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => skipTime(-10)}
              >
                <SkipBack className="h-5 w-5" />
              </Button>

              <Button
                size="icon"
                className="h-14 w-14"
                onClick={togglePlay}
              >
                {isPlaying ? (
                  <Pause className="h-6 w-6" />
                ) : (
                  <Play className="h-6 w-6 ml-1" />
                )}
              </Button>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => skipTime(10)}
              >
                <SkipForward className="h-5 w-5" />
              </Button>
            </div>

            {/* Additional Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 w-48">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleMute}
                >
                  {isMuted ? (
                    <VolumeX className="h-4 w-4" />
                  ) : (
                    <Volume2 className="h-4 w-4" />
                  )}
                </Button>
                <Slider
                  value={[isMuted ? 0 : volume]}
                  max={1}
                  step={0.01}
                  onValueChange={handleVolumeChange}
                  className="w-24"
                />
              </div>

              <Button variant="outline" size="sm" onClick={changePlaybackRate}>
                {playbackRate}x
              </Button>

              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm">
                    <List className="h-4 w-4 mr-2" />
                    Chapters
                  </Button>
                </SheetTrigger>
                <SheetContent>
                  <SheetHeader>
                    <SheetTitle>Chapters</SheetTitle>
                  </SheetHeader>
                  <div className="mt-6 space-y-2">
                    {playerData.chapters.map((chapter, index) => (
                      <button
                        key={chapter.id}
                        onClick={() => jumpToChapter(index)}
                        className={`w-full text-left p-3 rounded-lg transition-colors ${
                          index === currentChapterIndex
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-muted'
                        }`}
                      >
                        <div className="text-sm font-medium">{chapter.title}</div>
                        <div className="text-xs text-muted-foreground">
                          {chapter.audio_duration_seconds && 
                            `${Math.floor(chapter.audio_duration_seconds / 60)}m`}
                        </div>
                      </button>
                    ))}
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
