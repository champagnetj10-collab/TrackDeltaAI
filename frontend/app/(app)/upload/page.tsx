'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useRouter } from 'next/navigation'
import { UploadCloud, FileCheck2, CheckCircle2 } from 'lucide-react'
import { requestUploadUrl, uploadFileToS3, notifyUploadComplete, getSessionStatus } from '@/lib/api'
import { cn } from '@/lib/utils'
import type { SessionStatus } from '@/types'
import { Button } from '@/components/ui/Button'
import { FormError } from '@/components/ui/Input'

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

const PIPELINE_STEPS: { key: UploadStep; label: string }[] = [
  { key: 'uploading', label: 'Upload' },
  { key: 'parsing', label: 'Parse' },
  { key: 'extracting', label: 'Analyze' },
  { key: 'coaching', label: 'Coach' },
]

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

      // 2. Upload file directly to S3
      await uploadFileToS3(presigned_url, file)

      // 3. Notify API — start processing
      await notifyUploadComplete(session_id, driverNote || undefined)

      // 4. Poll for status
      setStep('parsing')
      const hintInterval = setInterval(() => {
        setHintIndex((h) => (h + 1) % PIPELINE_HINTS.length)
      }, 4000)

      const poll = setInterval(async () => {
        try {
          const { status, processing_error } = await getSessionStatus(session_id)

          const statusMap: Record<SessionStatus, UploadStep> = {
            pending:    'uploading',
            parsing:    'parsing',
            extracting: 'extracting',
            coaching:   'coaching',
            completed:  'complete',
            failed:     'error',
          }
          setStep(statusMap[status] ?? 'error')

          if (status === 'completed') {
            clearInterval(poll)
            clearInterval(hintInterval)
            setTimeout(() => router.push(`/sessions/${session_id}`), 800)
          }

          if (status === 'failed') {
            clearInterval(poll)
            clearInterval(hintInterval)
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
  const activeStepIndex = PIPELINE_STEPS.findIndex((s) => s.key === step)

  return (
    <div className="max-w-xl mx-auto px-6 py-10 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">New session</h1>
        <p className="text-delta-400 mt-1 text-sm">Upload your iRacing .ibt telemetry file.</p>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200',
          isDragActive
            ? 'border-delta-500 bg-delta-900 scale-[1.01]'
            : file
            ? 'border-emerald-600/60 bg-emerald-500/5'
            : 'border-delta-800 hover:border-delta-600/60 bg-delta-900/50',
          isProcessing && 'pointer-events-none opacity-60'
        )}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="animate-scale-in">
            <FileCheck2 size={28} className="mx-auto mb-3 text-emerald-400" />
            <p className="text-emerald-400 font-medium">{file.name}</p>
            <p className="text-delta-500 text-sm mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
          </div>
        ) : (
          <div>
            <UploadCloud size={28} className="mx-auto mb-3 text-delta-500" />
            <p className="text-steel font-medium text-sm">
              {isDragActive ? 'Drop it here' : 'Drag your .ibt file here, or click to browse'}
            </p>
            <p className="text-delta-500 text-sm mt-2">
              Find it at: <code className="bg-delta-950 border border-delta-800 px-1.5 py-0.5 rounded text-delta-400">Documents → iRacing → telemetry</code>
            </p>
          </div>
        )}
      </div>

      {/* Session note */}
      {!isProcessing && (
        <div>
          <label htmlFor="driverNote" className="block text-sm font-medium text-delta-300 mb-1.5">
            Session note <span className="text-delta-600 font-normal">(optional)</span>
          </label>
          <textarea
            id="driverNote"
            value={driverNote}
            onChange={(e) => setDriverNote(e.target.value)}
            maxLength={280}
            rows={2}
            placeholder="What were you working on? How did it feel?"
            className="w-full px-4 py-2.5 bg-delta-950 border border-delta-700 rounded-lg text-white placeholder-delta-600 focus:outline-none focus:ring-2 focus:ring-delta-500 resize-none text-sm transition-colors"
          />
          <p className="text-xs text-delta-600 mt-1">{driverNote.length}/280</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div>
          <FormError message={error} />
          <button
            onClick={() => { setError(null); setStep('idle') }}
            className="text-delta-400 text-xs mt-2 hover:text-white transition-colors"
          >
            Try again
          </button>
        </div>
      )}

      {/* Processing state */}
      {isProcessing && step !== 'complete' && (
        <div className="bg-delta-900 border border-delta-800 rounded-2xl p-6 space-y-6 animate-fade-in">
          {/* Stepper */}
          <div className="flex items-center">
            {PIPELINE_STEPS.map((s, i) => (
              <div key={s.key} className="flex items-center flex-1 last:flex-none">
                <div className="flex flex-col items-center gap-2">
                  <div
                    className={cn(
                      'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors duration-300',
                      i < activeStepIndex
                        ? 'bg-delta-600 border-delta-600 text-white'
                        : i === activeStepIndex
                        ? 'border-delta-500 text-delta-400 animate-pulse-slow'
                        : 'border-delta-800 text-delta-700'
                    )}
                  >
                    {i < activeStepIndex ? <CheckCircle2 size={14} /> : i + 1}
                  </div>
                  <span className={cn('text-[11px] font-medium', i <= activeStepIndex ? 'text-delta-300' : 'text-delta-700')}>
                    {s.label}
                  </span>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div className="flex-1 h-0.5 mx-1 -mt-5 bg-delta-800 overflow-hidden rounded-full">
                    <div
                      className="h-full bg-delta-600 transition-all duration-500"
                      style={{ width: i < activeStepIndex ? '100%' : '0%' }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="text-center space-y-2">
            <p className="text-white font-medium text-sm">{STEP_MESSAGES[step]}</p>
            <p className="text-delta-500 text-sm">{PIPELINE_HINTS[hintIndex]}</p>
          </div>
        </div>
      )}

      {/* Upload button */}
      {!isProcessing && (
        <Button onClick={handleUpload} disabled={!file} fullWidth size="lg">
          Analyze with Delta
        </Button>
      )}
    </div>
  )
}
