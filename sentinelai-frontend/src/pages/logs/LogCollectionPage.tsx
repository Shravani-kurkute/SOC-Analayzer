import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Upload,
  File,
  FileText,
  X,
  CheckCircle2,
  AlertCircle,
  Clock,
  Trash2,
  Database,
  HardDrive,
  Activity,
  RefreshCw,
  FileWarning,
  List,
  Globe,
} from 'lucide-react'
import { cn } from '@utils/cn'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import { Button } from '@components/ui/button'
import { Progress } from '@components/ui/progress'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { logService } from '@services/logService'
import type { LogFile } from '@typings/log'

const ALLOWED_EXTENSIONS = ['.log', '.txt', '.json']
const MAX_FILE_SIZE = 100 * 1024 * 1024
const MAX_FILE_SIZE_MB = 100

const SOURCE_TYPE_MAP: Record<string, string> = {
  'linux-auth': 'Linux Auth',
  'linux-syslog': 'Linux Syslog',
  'apache-access': 'Apache Access',
  nginx: 'Nginx',
  firewall: 'Firewall',
  'cisco-asa': 'Cisco ASA',
  fortinet: 'Fortinet',
  'windows-evtx': 'Windows EVTX',
  'json-log': 'JSON Log',
  generic: 'Generic',
}

const STATUS_VARIANTS: Record<string, 'default' | 'success' | 'warning' | 'critical' | 'info'> = {
  uploaded: 'success',
  processing: 'warning',
  completed: 'success',
  failed: 'critical',
  pending: 'default',
}

function formatBytes(bytes: number): string {
  if (bytes >= 1_073_741_824) return `${(bytes / 1_073_741_824).toFixed(2)} GB`
  if (bytes >= 1_048_576) return `${(bytes / 1_048_576).toFixed(2)} MB`
  if (bytes >= 1_024) return `${(bytes / 1_024).toFixed(2)} KB`
  return `${bytes} B`
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function FilePreview({ content, filename }: { content: string; filename: string }) {
  const lines = content.split('\n').slice(0, 50)
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">Preview ({filename})</span>
        <span className="text-[10px] text-muted-foreground">{lines.length} lines shown</span>
      </div>
      <div className="max-h-48 overflow-auto rounded-lg border border-border/50 bg-black/30 p-3 font-mono text-[11px] leading-relaxed">
        {lines.map((line, i) => (
          <div key={i} className="flex gap-3">
            <span className="w-6 shrink-0 text-right text-muted-foreground/40">{i + 1}</span>
            <span className="text-foreground/80">{line || '\u00A0'}</span>
          </div>
        ))}
        {content.split('\n').length > 50 && (
          <div className="mt-2 text-center text-[10px] text-muted-foreground/60">... {content.split('\n').length - 50} more lines</div>
        )}
      </div>
    </div>
  )
}

export default function LogCollectionPage() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [filePreview, setFilePreview] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const statsQuery = useQuery({
    queryKey: ['log-stats'],
    queryFn: logService.getStats,
    refetchInterval: 15_000,
  })

  const filesQuery = useQuery({
    queryKey: ['log-files', page],
    queryFn: () => logService.list(page, 10),
    refetchInterval: 15_000,
  })

  const deleteMutation = useMutation({
    mutationFn: logService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['log-files'] })
      queryClient.invalidateQueries({ queryKey: ['log-stats'] })
    },
  })

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!selectedFile) throw new Error('No file selected')
      return logService.upload(selectedFile, setUploadProgress)
    },
    onSuccess: () => {
      setUploadState('success')
      queryClient.invalidateQueries({ queryKey: ['log-files'] })
      queryClient.invalidateQueries({ queryKey: ['log-stats'] })
    },
    onError: (err: Error) => {
      setUploadState('error')
      setUploadError(err.message)
    },
  })

  const validateFile = useCallback((file: File): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Unsupported file type '${ext}'. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File too large (${formatBytes(file.size)}). Maximum: ${MAX_FILE_SIZE_MB} MB`
    }
    if (file.size === 0) {
      return 'File is empty'
    }
    return null
  }, [])

  const handleFileSelect = useCallback((file: File) => {
    const error = validateFile(file)
    if (error) {
      setUploadError(error)
      setUploadState('error')
      return
    }
    setUploadError(null)
    setUploadState('idle')
    setUploadProgress(0)
    setSelectedFile(file)

    const reader = new FileReader()
    reader.onload = (e) => {
      setFilePreview(e.target?.result as string)
    }
    reader.readAsText(file.slice(0, 50000))
  }, [validateFile])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }, [handleFileSelect])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleBrowse = () => fileInputRef.current?.click()

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFileSelect(file)
    e.target.value = ''
  }

  const handleUpload = () => {
    if (!selectedFile) return
    setUploadState('uploading')
    setUploadProgress(0)
    uploadMutation.mutate()
  }

  const handleReset = () => {
    setSelectedFile(null)
    setFilePreview(null)
    setUploadProgress(0)
    setUploadState('idle')
    setUploadError(null)
  }

  const stats = statsQuery.data

  return (
    <div className="space-y-6">
      <PageHeader
        title="Log Collection"
        description="Upload and manage security log files for analysis"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="accent" size="sm"
              onClick={() => {
                statsQuery.refetch()
                filesQuery.refetch()
              }}
            >
              <RefreshCw className="mr-2 h-4 w-4" />Refresh
            </Button>
          </div>
        }
      />

      {statsQuery.isError && (
        <Card className="border-red-500/30 bg-red-500/5 p-4">
          <p className="text-sm text-red-400">Failed to load statistics: {statsQuery.error?.message}</p>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats ? (
          <>
            <StatCard title="Total Files" value={stats.total_files} description="Uploaded log files" icon={FileText} variant="info" />
            <StatCard title="Storage Used" value={stats.storage_used} description={`${stats.total_files} files stored`} icon={HardDrive} variant="default" />
            <StatCard title="Parsed Entries" value={stats.total_parsed_entries.toLocaleString()} description="Lines processed" icon={Activity} variant="success" />
            <StatCard title="Recent Uploads" value={stats.recent_uploads} description="Last 24 hours" icon={Clock} variant="warning" />
          </>
        ) : (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5"><div className="space-y-3"><Skeleton className="h-3 w-24" /><Skeleton className="h-8 w-16" /></div></Card>
          ))
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Log File</CardTitle>
          <CardDescription>Drag & drop a log file or click to browse. Supported: {ALLOWED_EXTENSIONS.join(', ')} (max {MAX_FILE_SIZE_MB} MB)</CardDescription>
        </CardHeader>
        <CardContent>
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={selectedFile ? undefined : handleBrowse}
            className={cn(
              'relative cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-all duration-200',
              dragOver
                ? 'border-[#00F5FF] bg-[#00F5FF]/5 shadow-[0_0_30px_rgba(0,245,255,0.1)]'
                : selectedFile
                  ? 'border-border/50 bg-card/50'
                  : 'border-border/30 hover:border-[#00F5FF]/50 hover:bg-accent/20',
            )}
          >
            {selectedFile ? (
              <div className="space-y-4" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#00F5FF]/10">
                    <FileText className="h-6 w-6 text-[#00F5FF]" />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-foreground">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">{formatBytes(selectedFile.size)}</p>
                  </div>
                  <Button variant="ghost" size="icon-sm" onClick={handleReset} className="shrink-0">
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {filePreview && <FilePreview content={filePreview} filename={selectedFile.name} />}

                {uploadState === 'idle' && (
                  <div className="flex items-center justify-center gap-3">
                    <Button onClick={handleUpload} disabled={uploadMutation.isPending}>
                      <Upload className="mr-2 h-4 w-4" />Upload File
                    </Button>
                    <Button variant="outline" onClick={handleBrowse}>Change File</Button>
                  </div>
                )}

                {uploadState === 'uploading' && (
                  <div className="mx-auto max-w-md space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Uploading...</span>
                      <span className="font-medium text-foreground">{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} />
                  </div>
                )}

                {uploadState === 'success' && (
                  <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex items-center justify-center gap-2 text-emerald-400">
                    <CheckCircle2 className="h-5 w-5" />
                    <span className="text-sm font-medium">File uploaded successfully!</span>
                  </motion.div>
                )}

                {uploadState === 'error' && (
                  <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="space-y-2">
                    <div className="flex items-center justify-center gap-2 text-red-400">
                      <AlertCircle className="h-5 w-5" />
                      <span className="text-sm font-medium">Upload failed</span>
                    </div>
                    <p className="text-xs text-red-400/80">{uploadError}</p>
                    <Button variant="outline" size="sm" onClick={handleReset}>Try Again</Button>
                  </motion.div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex justify-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#00F5FF]/10">
                    <Upload className="h-8 w-8 text-[#00F5FF]" />
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">
                    <span className="text-[#00F5FF]">Click to browse</span> or drag and drop
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    .log, .txt, .json files up to {MAX_FILE_SIZE_MB} MB
                  </p>
                </div>
              </div>
            )}
          </div>
          <input ref={fileInputRef} type="file" accept=".log,.txt,.json" className="hidden" onChange={handleFileInputChange} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Upload History</CardTitle>
            <CardDescription>Recently uploaded log files</CardDescription>
          </div>
          <Badge variant="outline" className="gap-1">
            <List className="h-3 w-3" />
            {filesQuery.data?.total ?? 0} total
          </Badge>
        </CardHeader>
        <CardContent>
          {filesQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-16 w-full rounded-lg" />)}
            </div>
          ) : filesQuery.isError ? (
            <div className="flex items-center justify-center py-8 text-sm text-red-400">
              Failed to load upload history
            </div>
          ) : filesQuery.data && filesQuery.data.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-sm text-muted-foreground">
              <Upload className="mb-2 h-8 w-8 text-muted-foreground/30" />
              <p>No log files uploaded yet</p>
              <p className="text-xs text-muted-foreground/60">Upload a log file to get started</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filesQuery.data?.items.map((file: LogFile) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="group flex items-center gap-4 rounded-lg border border-border/50 p-3 transition-all hover:border-border hover:bg-accent/30"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#00F5FF]/10">
                    <File className="h-5 w-5 text-[#00F5FF]" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground truncate">{file.original_filename}</span>
                      <Badge variant={STATUS_VARIANTS[file.status] || 'default'} className="text-[10px] h-4 px-1">
                        {file.status}
                      </Badge>
                    </div>
                    <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[11px] text-muted-foreground">
                      <span>{formatBytes(file.size)}</span>
                      <span className="font-mono">{SOURCE_TYPE_MAP[file.source_type] || file.source_type}</span>
                      {file.uploaded_by && <span>{file.uploaded_by}</span>}
                      <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{timeAgo(file.upload_time)}</span>
                      {file.parsed_entries > 0 && <span>{file.parsed_entries} entries</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="hidden sm:block text-[10px] font-mono text-muted-foreground/60 max-w-[80px] truncate" title={file.checksum_sha256}>
                      {file.checksum_sha256.slice(0, 12)}...
                    </span>
                    <Button
                      variant="ghost" size="icon-sm"
                      className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-400"
                      onClick={() => deleteMutation.mutate(file.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {filesQuery.data && filesQuery.data.total > filesQuery.data.page_size && (
            <div className="mt-4 flex items-center justify-center gap-2">
              <Button
                variant="outline" size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-xs text-muted-foreground">
                Page {page} of {Math.ceil(filesQuery.data.total / filesQuery.data.page_size)}
              </span>
              <Button
                variant="outline" size="sm"
                disabled={page >= Math.ceil(filesQuery.data.total / filesQuery.data.page_size)}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#00F5FF]/10 text-[#00F5FF]">
              <Globe className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Supported Formats</p>
              <p className="text-sm font-bold text-foreground">.log .txt .json</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Max File Size</p>
              <p className="text-sm font-bold text-foreground">{MAX_FILE_SIZE_MB} MB</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10 text-purple-400">
              <FileWarning className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Duplicate Detection</p>
              <p className="text-sm font-bold text-foreground">SHA-256</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-500/10 text-orange-400">
              <HardDrive className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Storage</p>
              <p className="text-sm font-bold text-foreground">{stats?.storage_used || 'N/A'}</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Source Types by Status</CardTitle>
          <CardDescription>Breakdown of uploaded files by source type and processing status</CardDescription>
        </CardHeader>
        <CardContent>
          {stats ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(stats.by_source_type).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between rounded-lg border border-border/50 px-3 py-2">
                  <span className="text-sm text-foreground">{SOURCE_TYPE_MAP[type] || type}</span>
                  <Badge variant="outline">{count} files</Badge>
                </div>
              ))}
              {Object.keys(stats.by_source_type).length === 0 && (
                <p className="col-span-full text-center text-sm text-muted-foreground py-4">No files uploaded yet</p>
              )}
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-10 rounded-lg" />)}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
