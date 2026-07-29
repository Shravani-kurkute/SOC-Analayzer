import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  FileText, Download, Trash2, RefreshCw, BarChart3, Shield, AlertTriangle,
  Server, CheckSquare, Loader2, Clock, Calendar,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Skeleton } from '@components/ui/skeleton'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@components/ui/dialog'
import { reportService } from '@services/reportService'
import type { ReportListItem, ReportType, ReportFormat } from '@typings/report'

const REPORT_TYPES: { value: ReportType; label: string; icon: typeof FileText; desc: string }[] = [
  { value: 'executive', label: 'Executive SOC Report', icon: BarChart3, desc: 'High-level SOC overview with KPIs and health score' },
  { value: 'threat', label: 'Threat Report', icon: Shield, desc: 'Attack timeline, IOC summary, MITRE coverage' },
  { value: 'incident', label: 'Incident Report', icon: AlertTriangle, desc: 'Full incident details, timeline, evidence, AI analysis' },
  { value: 'asset', label: 'Asset Report', icon: Server, desc: 'Asset inventory, criticality, incidents by asset' },
  { value: 'compliance', label: 'Compliance Report', icon: CheckSquare, desc: 'SOC2, ISO27001, NIST, CIS coverage' },
]

const FORMATS: { value: ReportFormat; label: string }[] = [
  { value: 'json', label: 'JSON' },
  { value: 'csv', label: 'CSV' },
  { value: 'xlsx', label: 'Excel' },
  { value: 'pdf', label: 'PDF' },
]

const TYPE_BG: Record<string, string> = {
  executive: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  threat: 'text-red-400 bg-red-500/10 border-red-500/20',
  incident: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  asset: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  compliance: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
}

function formatBytes(bytes?: number): string {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return new Date(ts).toLocaleDateString()
}

export default function ReportsPage() {
  const queryClient = useQueryClient()
  const [showGenerator, setShowGenerator] = useState(false)
  const [selectedType, setSelectedType] = useState<ReportType>('executive')
  const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('pdf')
  const [reportTitle, setReportTitle] = useState('')
  const [dateStart, setDateStart] = useState('')
  const [dateEnd, setDateEnd] = useState('')

  const reportsQuery = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportService.list(100, 0),
    refetchInterval: 30000,
  })

  const statsQuery = useQuery({
    queryKey: ['report-stats'],
    queryFn: () => reportService.getStats(),
    refetchInterval: 30000,
  })

  const generateMutation = useMutation({
    mutationFn: () => reportService.generate({
      report_type: selectedType,
      title: reportTitle || `${selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Report`,
      format: selectedFormat,
      date_range_start: dateStart || undefined,
      date_range_end: dateEnd || undefined,
    }),
    onSuccess: () => {
      setShowGenerator(false)
      setReportTitle('')
      setDateStart('')
      setDateEnd('')
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['report-stats'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => reportService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['report-stats'] })
    },
  })

  const downloadMutation = useMutation({
    mutationFn: async (id: string) => {
      const report = reportsQuery.data?.items.find((r: ReportListItem) => r.id === id)
      if (report) {
        window.open(reportService.downloadUrl(id), '_blank')
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['report-stats'] })
    },
  })

  const deleteReport = (id: string) => {
    if (window.confirm('Delete this report?')) {
      deleteMutation.mutate(id)
    }
  }

  const stats = statsQuery.data
  const reports = reportsQuery.data?.items || []

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports"
        description="Generate and manage enterprise reports"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => reportsQuery.refetch()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="accent" size="sm" onClick={() => setShowGenerator(true)}>
              <FileText className="h-4 w-4" /> Generate Report
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-[#00F5FF]/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#00F5FF]/10"><FileText className="h-5 w-5 text-[#00F5FF]" /></div>
              <div>
                <p className="text-2xl font-bold">{stats ? stats.total_reports : <Skeleton className="h-7 w-12" />}</p>
                <p className="text-xs text-muted-foreground">Total Reports</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-[#00F5FF]/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10"><Calendar className="h-5 w-5 text-emerald-400" /></div>
              <div>
                <p className="text-2xl font-bold">{stats ? stats.reports_today : <Skeleton className="h-7 w-12" />}</p>
                <p className="text-xs text-muted-foreground">Generated Today</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-[#00F5FF]/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-orange-500/10"><Download className="h-5 w-5 text-orange-400" /></div>
              <div>
                <p className="text-2xl font-bold">
                  {stats ? stats.most_downloaded.reduce((s: number, r: ReportListItem) => s + (r.download_count || 0), 0) : <Skeleton className="h-7 w-12" />}
                </p>
                <p className="text-xs text-muted-foreground">Total Downloads</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-[#00F5FF]/10">
        <CardContent className="p-4">
          {reportsQuery.isLoading ? (
            <div className="space-y-3">
              {[1,2,3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : reports.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-muted-foreground">No reports generated yet.</p>
              <Button variant="accent" size="sm" className="mt-3" onClick={() => setShowGenerator(true)}>
                Generate your first report
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {reports.map((report: ReportListItem) => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg bg-secondary/30 border border-border/50 hover:bg-secondary/50 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`p-1.5 rounded ${TYPE_BG[report.report_type] || 'text-gray-400 bg-gray-500/10'}`}>
                      {(() => {
                        const t = REPORT_TYPES.find(rt => rt.value === report.report_type)
                        const Icon = t?.icon || FileText
                        return <Icon className="h-4 w-4" />
                      })()}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium truncate">{report.title}</p>
                        <Badge variant="outline" className="text-[10px] h-4 px-1">{report.format.toUpperCase()}</Badge>
                        <Badge variant="outline" className="text-[10px] h-4 px-1">{report.report_type}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5">
                        <Clock className="h-3 w-3" />
                        {timeAgo(report.created_at)}
                        {report.file_size ? ` · ${formatBytes(report.file_size)}` : ''}
                        {report.download_count > 0 ? ` · ${report.download_count} downloads` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <Button size="icon-sm" variant="ghost" onClick={() => downloadMutation.mutate(report.id)}>
                      <Download className="h-3.5 w-3.5" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => deleteReport(report.id)}>
                      <Trash2 className="h-3.5 w-3.5 text-red-400" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showGenerator} onOpenChange={setShowGenerator}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Generate Report</DialogTitle>
            <DialogDescription>Choose report type, format, and filters</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Report Type</label>
              <div className="grid grid-cols-1 gap-2">
                {REPORT_TYPES.map(rt => {
                  const Icon = rt.icon
                  return (
                    <button
                      key={rt.value}
                      onClick={() => setSelectedType(rt.value)}
                      className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-colors ${
                        selectedType === rt.value
                          ? 'border-[#00F5FF] bg-[#00F5FF]/5'
                          : 'border-border/50 bg-secondary/20 hover:bg-secondary/40'
                      }`}
                    >
                      <div className={`p-1.5 rounded mt-0.5 ${TYPE_BG[rt.value]}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{rt.label}</p>
                        <p className="text-xs text-muted-foreground">{rt.desc}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">Title</label>
              <input
                value={reportTitle}
                onChange={e => setReportTitle(e.target.value)}
                placeholder={`${selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Report`}
                className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Format</label>
                <select
                  value={selectedFormat}
                  onChange={e => setSelectedFormat(e.target.value as ReportFormat)}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
                >
                  {FORMATS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Date Range Start</label>
                <input
                  type="date"
                  value={dateStart}
                  onChange={e => setDateStart(e.target.value)}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Date Range End</label>
                <input
                  type="date"
                  value={dateEnd}
                  onChange={e => setDateEnd(e.target.value)}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setShowGenerator(false)}>Cancel</Button>
              <Button variant="accent" size="sm" onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
                {generateMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
                Generate
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
