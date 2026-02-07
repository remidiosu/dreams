import { useState, useRef, useCallback } from 'react'
import { ImagePlus, X, Upload } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface UploadedImage {
  file: File
  preview: string
  caption: string
}

interface ImageUploadProps {
  onImagesChange: (images: UploadedImage[]) => void
  images: UploadedImage[]
  maxImages?: number
}

const MAX_FILE_SIZE = 20 * 1024 * 1024 // 20MB
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export function ImageUpload({ onImagesChange, images, maxImages = 3 }: ImageUploadProps) {
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateAndAdd = useCallback((files: FileList | File[]) => {
    setError(null)
    const newImages: UploadedImage[] = [...images]

    for (const file of Array.from(files)) {
      if (newImages.length >= maxImages) {
        setError(`Maximum ${maxImages} images allowed`)
        break
      }
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setError(`Invalid file type: ${file.name}. Accepted: JPEG, PNG, WEBP`)
        continue
      }
      if (file.size > MAX_FILE_SIZE) {
        setError(`File too large: ${file.name}. Maximum 20MB per image`)
        continue
      }
      newImages.push({
        file,
        preview: URL.createObjectURL(file),
        caption: '',
      })
    }

    onImagesChange(newImages)
  }, [images, maxImages, onImagesChange])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length) {
      validateAndAdd(e.dataTransfer.files)
    }
  }, [validateAndAdd])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const removeImage = (index: number) => {
    const updated = [...images]
    URL.revokeObjectURL(updated[index].preview)
    updated.splice(index, 1)
    onImagesChange(updated)
    setError(null)
  }

  const updateCaption = (index: number, caption: string) => {
    const updated = [...images]
    updated[index] = { ...updated[index], caption }
    onImagesChange(updated)
  }

  return (
    <div className="space-y-3">
      {/* Image previews */}
      {images.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {images.map((img, i) => (
            <div key={i} className="relative group">
              <img
                src={img.preview}
                alt={img.caption || `Dream image ${i + 1}`}
                className="w-full h-32 object-cover rounded-lg border border-border"
              />
              <button
                onClick={() => removeImage(i)}
                className="absolute top-1 right-1 p-1 bg-black/60 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-3 h-3" />
              </button>
              <input
                type="text"
                placeholder="Caption (optional)"
                value={img.caption}
                onChange={(e) => updateCaption(i, e.target.value)}
                className="mt-1 w-full text-xs px-2 py-1 bg-surface-2 border border-border rounded text-foreground placeholder:text-muted"
              />
            </div>
          ))}
        </div>
      )}

      {/* Drop zone */}
      {images.length < maxImages && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => inputRef.current?.click()}
          className={cn(
            'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
            dragOver
              ? 'border-accent bg-accent/5'
              : 'border-border hover:border-accent/50 hover:bg-surface-2'
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_TYPES.join(',')}
            multiple
            onChange={(e) => {
              if (e.target.files?.length) {
                validateAndAdd(e.target.files)
              }
              e.target.value = ''
            }}
            className="hidden"
          />
          <div className="flex flex-col items-center gap-2">
            {dragOver ? (
              <Upload className="w-6 h-6 text-accent" />
            ) : (
              <ImagePlus className="w-6 h-6 text-muted" />
            )}
            <p className="text-sm text-muted">
              {dragOver ? 'Drop images here' : 'Click or drag images here'}
            </p>
            <p className="text-xs text-muted/60">
              JPEG, PNG, WEBP up to 20MB ({images.length}/{maxImages})
            </p>
          </div>
        </div>
      )}

      {error && (
        <p className="text-xs text-danger">{error}</p>
      )}
    </div>
  )
}
