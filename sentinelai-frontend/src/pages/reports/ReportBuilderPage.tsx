import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  FileText, Download, BarChart3, Shield, AlertTriangle,
  Server, CheckSquare, ArrowLeft, Loader2, Eye,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { reportService } from '@services/reportService'
import type { ReportType, ReportFormat, ReportResponse } from '@typings/report'

const REPORT_TYPES: { value: ReportType; label: string; icon: typeof FileText; desc: string; color: string }[] = [
  { value: 'executive', label: 'Executive SOC Report', icon: BarChart3, desc: 'High-level SOC KPIs, health score, top risks, MITRE techniques', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  { value: 'threat', label: 'Threat Report', icon: Shield, desc: 'Attack timeline, IOC summary, threat intel, MITRE coverage, heatmaps', color: 'text-red-400 bg-red-500/10 border-red-500/20' },
  { value: 'incident', label: 'Incident Report', icon: AlertTriangle, desc: 'Full incident with timeline, comments, evidence, tasks, AI analysis', color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' },
  { value: 'asset', label: 'Asset Report', icon: Server, desc: 'Asset inventory, criticality, incidents per asset, open risks', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  { value: 'compliance', label: 'Compliance Report', icon: CheckSquare, desc: 'SOC2, ISO27001, NIST, CIS coverage with MITRE mapping', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
]

const FORMATS: { value: ReportFormat; label: string; ext: string }[] = [
  { value: 'pdf', label: 'PDF', ext: '.pdf' },
  { value: 'csv', label: 'CSV', ext: '.csv' },
  { value: 'xlsx', label: 'Excel', ext: '.xlsx' },
  { value: 'json', label: 'JSON', ext: '.json' },
]

export default function ReportBuilderPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedType, setSelectedType] = useState<ReportType>('executive')
  const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('pdf')
  const [reportTitle, setReportTitle] = useState('')
  const [dateStart, setDateStart] = useState('')
  const [dateEnd, setDateEnd] = useState('')
  const [incidentId, setIncidentId] = useState('')
  const [generatedReport, setGeneratedReport] = useState<ReportResponse | null>(null)

  const generateMutation = useMutation({
    mutationFn: () => reportService.generate({
      report_type: selectedType,
      title: reportTitle || `${selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Report`,
      format: selectedFormat,
      date_range_start: dateStart || undefined,
      date_range_end: dateEnd || undefined,
      incident_id: incidentId || undefined,
    }),
    onSuccess: (data) => {
      setGeneratedReport(data)
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })

  const Icon = REPORT_TYPES.find(t => t.value === selectedType)?.icon || FileText

  return (
    <div className="space-y-6">
      <PageHeader
        title="Report Builder"
        description="Design and generate custom reports"
        actions={
          <Button variant="outline" size="sm" onClick={() => navigate('/reports')}>
            <ArrowLeft className="h-4 w-4" /> Back to Reports
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Card className="border-[#00F5FF]/10">
            <CardHeader><CardTitle className="text-sm">1. Select Report Type</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {REPORT_TYPES.map(rt => {
                  const I = rt.icon
                  return (
                    <button
                      key={rt.value}
                      onClick={() => setSelectedType(rt.value)}
                      className={`flex items-start gap-3 p-4 rounded-lg border text-left transition-colors ${
                        selectedType === rt.value
                          ? 'border-[#00F5FF] bg-[#00F5FF]/5'
                          : 'border-border/50 bg-secondary/20 hover:bg-secondary/40'
                      }`}
                    >
                      <div className={`p-2 rounded ${rt.color}`}><I className="h-5 w-5" /></div>
                      <div>
                        <p className="text-sm font-medium">{rt.label}</p>
                        <p className="text-xs text-muted-foreground mt-1">{rt.desc}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="border-[#00F5FF]/10">
            <CardHeader><CardTitle className="text-sm">2. Configure</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Report Title</label>
                <input
                  value={reportTitle}
                  onChange={e => setReportTitle(e.target.value)}
                  placeholder={`${selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Report`}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
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
                    className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm"
                  />
                </div>
              </div>

              {selectedType === 'incident' && (
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Incident ID (required)</label>
                  <input
                    value={incidentId}
                    onChange={e => setIncidentId(e.target.value)}
                    placeholder="Enter incident UUID"
                    className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-[#00F5FF]/10">
            <CardHeader><CardTitle className="text-sm">3. Choose Export Format</CardTitle></CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {FORMATS.map(f => (
                  <button
                    key={f.value}
                    onClick={() => setSelectedFormat(f.value)}
                    className={`px-4 py-2 rounded-lg border text-sm transition-colors ${
                      selectedFormat === f.value
                        ? 'border-[#00F5FF] bg-[#00F5FF]/10 text-[#00F5FF]'
                        : 'border-border/50 bg-secondary/20 hover:bg-secondary/40'
                    }`}
                  >
                    {f.label} {f.ext}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Button
            variant="accent"
            size="lg"
            className="w-full"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending || (selectedType === 'incident' && !incidentId)}
          >
            {generateMutation.isPending ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <FileText className="h-5 w-5" />
            )}
            Generate {REPORT_TYPES.find(t => t.value === selectedType)?.label}
          </Button>
        </div>

        <div className="space-y-4">
          <Card className="border-[#00F5FF]/10">
            <CardHeader><CardTitle className="text-sm">Preview</CardTitle></CardHeader>
            <CardContent>
              {generatedReport ? (
                <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-secondary/20 border border-border/50">
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className="h-4 w-4 text-[#00F5FF]" />
                      <p className="text-sm font-medium">{generatedReport.title}</p>
                    </div>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline" className="text-[10px]">{generatedReport.report_type}</Badge>
                      <Badge variant="outline" className="text-[10px]">{generatedReport.format.toUpperCase()}</Badge>
                      <Badge variant="outline" className="text-[10px]">{generatedReport.status}</Badge>
                    </div>
                    {generatedReport.file_size && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Size: {(generatedReport.file_size / 1024).toFixed(1)} KB
                      </p>
                    )}
                  </div>
                  <Button
                    variant="accent"
                    size="sm"
                    className="w-full"
                    onClick={() => window.open(reportService.downloadUrl(generatedReport.id), '_blank')}
                  >
                    <Download className="h-4 w-4" /> Download
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => navigate('/reports')}
                  >
                    <Eye className="h-4 w-4" /> View All Reports
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Eye className="h-10 w-10 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Configure and generate a report to see preview</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
