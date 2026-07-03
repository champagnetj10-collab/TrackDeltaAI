'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useRouter } from 'next/navigation'
import { requestUploadUrl, uploadFileToS3, notifyUploadComplete, getSessionStatus } from '@/lib/api'
import { cn } from '@/lib/utils'
import type { SessionStatus } from '@/types'

type UploadStep = 'idle' | 'uploading' | 'parsing' | 'extracting' | 'coaching' | 'complete' | 'error'

const STEP_MESSAGES: Record<UploadStep, string> = {
  idle:       '',
  uploading:  'Uploading your session...',
  parsing:    'Reading session data...',
  extracting: 'Delta is analyzing your driving...',
  coaching:   'Delta is preparing your coaching debrief...',
  complete:   'Your coaching debrief is ready.',
  error:      '',
}

const PIPELINE_HINTS = [
  'Delta is looking at your braking zones, throttle application, and corner exits.',
  'Driver DNA is updating based on what Delta finds in this session.',
  'Delta only shares recommendations it can support with data from your laps.',
  'Every corner is an opportunity to find time.',
]

export default function UploadPage() {
  const router = useRouter()
  const [step, setStep] = useState<UploadStep>('idle')
  const [file, setFile] = useState<File | null>(null)
  const [driverNote, setDriverNote] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [hintIndex, setHintIndex] = useState(0)
  const [sessionId, setSessionId] = useState<string | null>(null)

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/octet-stream': ['.ibt'] },
    maxFiles: 1,
    maxSize: 250 * 1024 * 1024, // 250 MB
    onDropRejected: (rejections) => {
      const r = rejections[0]
      if (r.errors[0]?.code === 'file-too-large') {
        setError('This file is larger than 250 MB. Try uploading the most recent portion of your session.')
      } else {
        setError("This doesn't look like an iRacing telemetry file. Look for a .ibt file in Documents → iRacing → telemetry.")
      }
    },
  })

  async function handleUpload() {
    if (!file) return
    setError(null)

    try {
      // 1. Request presigned URL
      setStep('uploading')
      const { session_id, presigned_url } = await requestUploadUrl(file.name)
      setSessionId(session_id)

      // 2. Upload file directly to S3
      await uploadFileToS3(presigned_url, file)

      // 3. Notify API — start processing
      await notifyUploadComplete(session_id, driverNote || undefined)

      // 4. Poll for status
      setStep('parsing')
      let hint = 0
      const interval = setInterval(() => {
        setHintIndex((h) => (h + 1) % PIPELINE_HINTS.length)
        hint++
      }, 4000)

      const poll = setInterval(async () => {
        try {
          const { status, processing_error } = await getSessionStatus(session_id)

          // Map API status to UI step
          const statusMap: Record<SessionStatus, UploadStep> = {
            pending:    'uploading',
            uploading:  'uploading',
            parsing:    'parsing',
            extracting: 'extracting',
            coaching:   'coaching',
            complete:   'complete',
            failed:     'error',
          }
          setStep(statusMap[status] ?? 'error')

          if (status === 'complete') {
            clearInterval(poll)
            clearInterval(interval)
            setTimeout(() => router.push(`/sessions/${session_id}`), 800)
          }

          if (status === 'failed') {
            clearInterval(poll)
            clearInterval(interval)
            setError(processing_error ?? 'Something went wrong during analysis. Please try again.')
          }
        } catch {
          // transient error — keep polling
        }
      }, 3000)

    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed. Please try again.'
      setError(message)
      setStep('error')
    }
  }

  const isProcessing = !['idle', 'error'].includes(step)

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">New Session</h1>
        <p className="text-slate-400 mt-1">Upload your iRacing .ibt telemetry file.</p>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-delta-500 bg-delta-950'
            : file
            ? 'border-green-700 bg-green-950'
            : 'border-slate-700 hover:border-slate-500 bg-slate-900',
          isProcessing && 'pointer-events-none opacity-60'
        )}
      >
        <input {...getInputProps()} />
        {file ? (
          <div>
            <p className="text-green-400 font-medium">{file.name}</p>
            <p className="text-slate-500 text-sm mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
          </div>
        ) : (
          <div>
            <p className="text-slate-300 font-medium">
              {isDragActive ? 'Drop it here' : 'Drag your .ibt file here, or click to browse'}
            </p>
            <p className="text-slate-500 text-sm mt-2">
              Find it at: <code className="bg-slate-800 px-1.5 py-0.5 rounded">Documents → iRacing → telemetry</code>
            </p>
          </div>
        )}
      </div>

      {/* Session note */}
      {!isProcessing && (
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            Session note <span className="text-slate-500 font-normal">(optional)</span>
          </label>
          <textarea
            value={driverNote}
            onChange={(e) => setDriverNote(e.target.value)}
            maxLength={280}
            rows={2}
            placeholder="What were you working on? How did it feel?"
            className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-delta-500 resize-none text-sm"
          />
          <p className="text-xs text-slate-600 mt-1">{driverNote.length}/280</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-950 border border-red-800 rounded-lg px-4 py-3">
          <p className="text-red-400 text-sm">{error}</p>
          <button
            onClick={() => { setError(null); setStep('idle') }}
            className="text-red-300 text-xs mt-1 hover:text-red-200"
          >
            Try again
          </button>
        </div>
      )}

      {/* Processing state */}
      {isProcessing && step !== 'complete' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center space-y-3">
          <div className="flex justify-center gap-1.5">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 rounded-full bg-delta-500 animate-bounce"
                style={{ animationDelay: `${i * 150}ms` }}
              />
            ))}
          </div>
          <p className="text-white font-medium">{STEP_MESSAGES[step]}</p>
          <p className="text-slate-500 text-sm">{PIPELINE_HINTS[hintIndex]}</p>
        </div>
      )}

      {/* Upload button */}
      {!isProcessing && (
        <button
          onClick={handleUpload}
          disabled={!file}
          className="w-full py-3 bg-delta-600 hover:bg-delta-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
        >
          Analyze with Delta
        </button>
      )}
    </div>
  )
}
