import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useGetPlayerData } from "@/lib/api/generated";
import type { PlayerData } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";
import { Play, Pause, SkipForward, SkipBack, Volume2, VolumeX, Loader2, List } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { decodeBase64Audio, decodePcmToAudioBuffer } from "@/lib/audio";

type PlaybackMode = "inline" | "url" | "none";

const playbackRates = [0.75, 1, 1.25, 1.5, 2];

const formatTime = (seconds?: number | null) => {
  if (seconds === undefined || seconds === null || Number.isNaN(seconds) || seconds < 0) {
    return "0:00";
  }
  const totalSeconds = Math.floor(seconds);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  }
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
};

export default function Player() {
  const { jobId } = useParams<{ jobId: string }>();
  const { toast } = useToast();
  const audioRef = useRef<HTMLAudioElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const sourceNodeRef = useRef<AudioBufferSourceNode | null>(null);
  const audioBufferRef = useRef<AudioBuffer | null>(null);
  const startedAtRef = useRef(0);
  const pausedAtRef = useRef(0);
  const offsetRef = useRef(0);
  const rafRef = useRef<number>();

  const { data: playerDataResponse, isLoading } = useGetPlayerData(jobId || "", {
    query: { enabled: !!jobId },
  });

  const playerData = playerDataResponse as unknown as PlayerData | null;
  const chapters = playerData?.chapters ?? [];

  const [mode, setMode] = useState<PlaybackMode>("none");
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isBufferLoading, setIsBufferLoading] = useState(false);

  const currentChapter = chapters[currentChapterIndex];

  const stopInlinePlayback = useCallback(() => {
    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.stop();
      } catch (error) {
        console.error(error);
      }
      sourceNodeRef.current.disconnect();
      sourceNodeRef.current = null;
    }
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = undefined;
    }
  }, []);

  const stopCurrentPlayback = useCallback(() => {
    if (mode === "inline") {
      stopInlinePlayback();
      pausedAtRef.current = 0;
      offsetRef.current = 0;
    }
    if (mode === "url") {
      const element = audioRef.current;
      if (element) {
        element.pause();
        element.currentTime = 0;
      }
    }
    setIsPlaying(false);
  }, [mode, stopInlinePlayback]);

  const changeChapter = useCallback(
    (index: number) => {
      if (index < 0 || index >= chapters.length) {
        return;
      }
      stopCurrentPlayback();
      setCurrentTime(0);
      setDuration(0);
      pausedAtRef.current = 0;
      offsetRef.current = 0;
      setCurrentChapterIndex(index);
      setMode("none");
    },
    [chapters.length, stopCurrentPlayback],
  );

  const handleNext = useCallback(() => {
    if (currentChapterIndex < chapters.length - 1) {
      changeChapter(currentChapterIndex + 1);
    }
  }, [changeChapter, currentChapterIndex, chapters.length]);

  const ensureContext = useCallback(() => {
    if (!audioContextRef.current) {
      const constructor =
        typeof window !== "undefined"
          ? window.AudioContext ?? (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
          : undefined;
      if (!constructor) {
        return null;
      }
      audioContextRef.current = new constructor();
    }
    if (audioContextRef.current && !gainNodeRef.current) {
      const node = audioContextRef.current.createGain();
      node.gain.value = isMuted ? 0 : volume;
      node.connect(audioContextRef.current.destination);
      gainNodeRef.current = node;
    }
    return audioContextRef.current;
  }, [isMuted, volume]);

  const updateInlineProgress = useCallback(() => {
    if (mode === "inline" && isPlaying && audioContextRef.current) {
      const elapsed = (audioContextRef.current.currentTime - startedAtRef.current) * playbackRate;
      const limit = audioBufferRef.current?.duration ?? 0;
      const position = Math.min(offsetRef.current + elapsed, limit);
      setCurrentTime(position);
      if (limit > 0 && position >= limit - 0.05) {
        stopInlinePlayback();
        setIsPlaying(false);
        pausedAtRef.current = 0;
        offsetRef.current = 0;
        handleNext();
        return;
      }
    }
    if (mode === "inline") {
      rafRef.current = requestAnimationFrame(updateInlineProgress);
    }
  }, [handleNext, isPlaying, mode, playbackRate, stopInlinePlayback]);

  const playInline = useCallback(() => {
    if (mode !== "inline") {
      return;
    }
    const context = ensureContext();
    if (!context || !audioBufferRef.current) {
      return;
    }
    stopInlinePlayback();
    const source = context.createBufferSource();
    source.buffer = audioBufferRef.current;
    source.playbackRate.value = playbackRate;
    if (gainNodeRef.current) {
      source.connect(gainNodeRef.current);
    } else {
      source.connect(context.destination);
    }
    const offset = pausedAtRef.current;
    offsetRef.current = offset;
    startedAtRef.current = context.currentTime;
    source.start(0, offset);
    sourceNodeRef.current = source;
    source.onended = () => {
      if (mode !== "inline") {
        return;
      }
      stopInlinePlayback();
      setIsPlaying(false);
      pausedAtRef.current = 0;
      offsetRef.current = 0;
      handleNext();
    };
    setIsPlaying(true);
    rafRef.current = requestAnimationFrame(updateInlineProgress);
  }, [ensureContext, handleNext, mode, playbackRate, stopInlinePlayback, updateInlineProgress]);

  const pauseInline = useCallback(() => {
    if (mode !== "inline" || !audioContextRef.current) {
      return;
    }
    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.stop();
      } catch (error) {
        console.error(error);
      }
      sourceNodeRef.current.disconnect();
      sourceNodeRef.current = null;
    }
    const elapsed = (audioContextRef.current.currentTime - startedAtRef.current) * playbackRate;
    const limit = audioBufferRef.current?.duration ?? 0;
    const position = Math.min(offsetRef.current + elapsed, limit);
    pausedAtRef.current = position;
    offsetRef.current = position;
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = undefined;
    }
    setIsPlaying(false);
  }, [mode, playbackRate]);

  useEffect(() => {
    if (mode === "url") {
      const element = audioRef.current;
      if (element) {
        element.muted = isMuted;
        element.volume = isMuted ? 0 : volume;
      }
    }
    if (mode === "inline" && gainNodeRef.current) {
      gainNodeRef.current.gain.value = isMuted ? 0 : volume;
    }
  }, [isMuted, mode, volume]);

  useEffect(() => {
    if (mode === "url") {
      const element = audioRef.current;
      if (element) {
        element.playbackRate = playbackRate;
      }
    }
    if (mode === "inline" && sourceNodeRef.current) {
      sourceNodeRef.current.playbackRate.value = playbackRate;
    }
  }, [mode, playbackRate]);

  useEffect(() => {
    if (currentChapterIndex >= chapters.length && chapters.length > 0) {
      setCurrentChapterIndex(0);
    }
  }, [chapters.length, currentChapterIndex]);

  useEffect(() => {
    stopInlinePlayback();
    const element = audioRef.current;
    if (element) {
      element.pause();
      element.currentTime = 0;
    }
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    pausedAtRef.current = 0;
    offsetRef.current = 0;

    if (!currentChapter) {
      setMode("none");
      return;
    }

    if (currentChapter.audio_inline_base64) {
      let cancelled = false;
      const load = async () => {
        setIsBufferLoading(true);
        const context = ensureContext();
        if (!context) {
          setIsBufferLoading(false);
          return;
        }
        try {
          const bytes = decodeBase64Audio(currentChapter.audio_inline_base64);
          const buffer = await decodePcmToAudioBuffer(bytes, context, 24000, 1);
          if (cancelled) {
            return;
          }
          audioBufferRef.current = buffer;
          setDuration(buffer.duration);
          setMode("inline");
        } catch {
          audioBufferRef.current = null;
          if (cancelled) {
            return;
          }
          if (currentChapter.audio_url) {
            setMode("url");
          } else {
            setMode("none");
            toast({
              title: "Audio unavailable",
              description: "We couldn't decode audio for this chapter.",
              variant: "destructive",
            });
          }
        } finally {
          if (!cancelled) {
            setIsBufferLoading(false);
          }
        }
      };
      load();
      return () => {
        cancelled = true;
      };
    }

    if (currentChapter.audio_url) {
      setMode("url");
      return;
    }

    setMode("none");
  }, [currentChapter, ensureContext, stopInlinePlayback, toast]);

  useEffect(() => {
    const element = audioRef.current;
    if (!element || mode !== "url") {
      return;
    }

    const handleTimeUpdate = () => setCurrentTime(element.currentTime);
    const handleLoadedMetadata = () => setDuration(element.duration || 0);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      handleNext();
    };

    element.addEventListener("timeupdate", handleTimeUpdate);
    element.addEventListener("loadedmetadata", handleLoadedMetadata);
    element.addEventListener("play", handlePlay);
    element.addEventListener("pause", handlePause);
    element.addEventListener("ended", handleEnded);

    if (element.readyState >= 1) {
      setDuration(element.duration || 0);
    }

    return () => {
      element.removeEventListener("timeupdate", handleTimeUpdate);
      element.removeEventListener("loadedmetadata", handleLoadedMetadata);
      element.removeEventListener("play", handlePlay);
      element.removeEventListener("pause", handlePause);
      element.removeEventListener("ended", handleEnded);
    };
  }, [handleNext, mode]);

  useEffect(() => () => {
    stopInlinePlayback();
    const element = audioRef.current;
    if (element) {
      element.pause();
    }
  }, [stopInlinePlayback]);

  const handleSeek = useCallback(
    (value: number[]) => {
      const target = Math.min(Math.max(value[0], 0), duration > 0 ? duration : 0);
      if (mode === "inline") {
        const wasPlaying = isPlaying;
        pauseInline();
        pausedAtRef.current = target;
        offsetRef.current = target;
        setCurrentTime(target);
        if (wasPlaying) {
          playInline();
        }
        return;
      }
      if (mode === "url") {
        const element = audioRef.current;
        if (!element) {
          return;
        }
        element.currentTime = target;
        setCurrentTime(target);
      }
    },
    [duration, isPlaying, mode, pauseInline, playInline],
  );

  const skipTime = useCallback(
    (seconds: number) => {
      const target = Math.min(Math.max(currentTime + seconds, 0), duration > 0 ? duration : 0);
      handleSeek([target]);
    },
    [currentTime, duration, handleSeek],
  );

  const togglePlay = useCallback(() => {
    if (mode === "inline") {
      if (isPlaying) {
        pauseInline();
      } else if (!isBufferLoading && audioBufferRef.current) {
        playInline();
      }
      return;
    }

    if (mode === "url") {
      const element = audioRef.current;
      if (!element) {
        return;
      }
      if (isPlaying) {
        element.pause();
      } else {
        element
          .play()
          .catch(() =>
            toast({
              title: "Playback failed",
              description: "Unable to start audio for this chapter.",
              variant: "destructive",
            }),
          );
      }
    }
  }, [isBufferLoading, isPlaying, mode, pauseInline, playInline, toast]);

  const handlePrev = useCallback(() => {
    if (currentTime > 3 || currentChapterIndex === 0) {
      handleSeek([0]);
    } else {
      changeChapter(currentChapterIndex - 1);
    }
  }, [changeChapter, currentChapterIndex, currentTime, handleSeek]);

  const jumpToChapter = (index: number) => {
    changeChapter(index);
  };

  const cyclePlaybackRate = () => {
    const currentIndex = playbackRates.indexOf(playbackRate);
    const nextRate = playbackRates[(currentIndex + 1) % playbackRates.length];
    setPlaybackRate(nextRate);
  };

  const handleVolumeChange = (value: number[]) => {
    const nextVolume = value[0];
    setVolume(nextVolume);
    setIsMuted(nextVolume === 0);
  };

  const toggleMute = () => {
    setIsMuted((prev) => !prev);
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

  const script = currentChapter?.script_text?.trim();
  const sliderMax = duration > 0 ? duration : 1;
  const inlineReady = mode !== "inline" || (!!audioBufferRef.current && !isBufferLoading);

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="flex flex-col md:flex-row gap-8 mb-12">
          <div className="w-full md:w-64 h-64 bg-muted rounded-lg flex items-center justify-center">
            {playerData.cover_url ? (
              <img src={playerData.cover_url} alt="Cover" className="w-full h-full object-cover rounded-lg" />
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
              <span>{chapters.length} chapters</span>
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

        <Card>
          <CardContent className="pt-6">
            <audio
              ref={audioRef}
              src={mode === "url" ? currentChapter?.audio_url ?? "" : undefined}
              className="hidden"
              preload="auto"
            />

            <div className="space-y-2 mb-6">
              <Slider value={[currentTime]} max={sliderMax} step={1} onValueChange={handleSeek} className="w-full" />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
              {mode === "inline" && (
                <div className="text-xs text-muted-foreground">
                  {isBufferLoading ? "Preparing chapter audio…" : "Playing inline audio"}
                </div>
              )}
            </div>

            <div className="flex items-center justify-center gap-4 mb-4">
              <Button variant="ghost" size="icon" onClick={() => skipTime(-10)}>
                <SkipBack className="h-5 w-5" />
              </Button>

              <Button
                size="icon"
                className="h-14 w-14"
                onClick={togglePlay}
                disabled={!inlineReady}
              >
                {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6 ml-1" />}
              </Button>

              <Button variant="ghost" size="icon" onClick={() => skipTime(10)}>
                <SkipForward className="h-5 w-5" />
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 w-48">
                <Button variant="ghost" size="icon" onClick={toggleMute}>
                  {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                </Button>
                <Slider
                  value={[isMuted ? 0 : volume]}
                  max={1}
                  step={0.01}
                  onValueChange={handleVolumeChange}
                  className="w-24"
                />
              </div>

              <Button variant="outline" size="sm" onClick={cyclePlaybackRate}>
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
                    {chapters.map((chapter, index) => (
                      <button
                        key={chapter.id}
                        onClick={() => jumpToChapter(index)}
                        className={`w-full text-left p-3 rounded-lg transition-colors ${
                          index === currentChapterIndex
                            ? "bg-primary text-primary-foreground"
                            : "hover:bg-muted"
                        }`}
                      >
                        <div className="text-sm font-medium">{chapter.title}</div>
                        <div className="text-xs text-muted-foreground">
                          {chapter.audio_duration_seconds && `${Math.floor(chapter.audio_duration_seconds / 60)}m`}
                        </div>
                      </button>
                    ))}
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </CardContent>
        </Card>

        {script && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-lg">Transcript</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none whitespace-pre-wrap text-muted-foreground">{script}</div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
