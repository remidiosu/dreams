import { Mic, Square, Pause, Play, Trash2, Check } from 'lucide-react'
import { useAudioRecorder } from '@/hooks/useAudioRecorder'
import { Button } from './Button'
import { cn } from '@/lib/utils'

interface VoiceRecorderProps {
  onRecordingComplete: (blob: Blob) => void
  onCancel: () => void
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function VoiceRecorder({ onRecordingComplete, onCancel }: VoiceRecorderProps) {
  const {
    isRecording,
    isPaused,
    duration,
    audioBlob,
    audioUrl,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    clearRecording,
  } = useAudioRecorder()

  const handleUse = () => {
    if (audioBlob) {
      onRecordingComplete(audioBlob)
    }
  }

  const handleDiscard = () => {
    clearRecording()
    onCancel()
  }

  // Error state
  if (error) {
    return (
      <div className="p-4 bg-danger/10 border border-danger/20 rounded-lg">
        <p className="text-sm text-danger mb-3">{error}</p>
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={() => clearRecording()}>
            Try Again
          </Button>
          <Button size="sm" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </div>
    )
  }

  // Review state (recording complete)
  if (audioBlob && audioUrl) {
    return (
      <div className="p-4 bg-surface-2 border border-border rounded-lg space-y-3">
        <div className="flex items-center gap-2 text-sm text-foreground">
          <Mic className="w-4 h-4 text-accent" />
          <span>Recording complete ({formatDuration(duration)})</span>
        </div>
        <audio src={audioUrl} controls className="w-full h-10" />
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={handleDiscard}>
            <Trash2 className="w-3 h-3 mr-1" />
            Discard
          </Button>
          <Button size="sm" onClick={handleUse}>
            <Check className="w-3 h-3 mr-1" />
            Use Recording
          </Button>
        </div>
      </div>
    )
  }

  // Recording state
  if (isRecording) {
    return (
      <div className="p-4 bg-surface-2 border border-border rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn(
              'w-3 h-3 rounded-full',
              isPaused ? 'bg-warning' : 'bg-danger animate-pulse'
            )} />
            <span className="text-sm text-foreground font-medium">
              {isPaused ? 'Paused' : 'Recording...'}
            </span>
            <span className="text-sm text-muted font-mono">{formatDuration(duration)}</span>
          </div>
          <div className="flex gap-2">
            {isPaused ? (
              <button
                onClick={resumeRecording}
                className="p-2 hover:bg-surface rounded-lg transition-colors text-foreground"
                title="Resume"
              >
                <Play className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={pauseRecording}
                className="p-2 hover:bg-surface rounded-lg transition-colors text-foreground"
                title="Pause"
              >
                <Pause className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={stopRecording}
              className="p-2 hover:bg-surface rounded-lg transition-colors text-danger"
              title="Stop"
            >
              <Square className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Idle state
  return (
    <div className="p-4 bg-surface-2 border border-border rounded-lg">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted">Record your dream narration</p>
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button size="sm" onClick={startRecording}>
            <Mic className="w-3 h-3 mr-1" />
            Start Recording
          </Button>
        </div>
      </div>
    </div>
  )
}
