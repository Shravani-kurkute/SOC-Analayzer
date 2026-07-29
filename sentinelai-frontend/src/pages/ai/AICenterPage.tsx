import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, Search, Activity, Clock, Copy, Check, Download,
  AlertTriangle, ChevronDown, ChevronUp, RefreshCw, Trash2,
  Shield, Target, FileText, ExternalLink, Zap, Loader2,
  Gauge, Hash, Server, AlertCircle,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { aiService } from '@services/aiService'
import { incidentService } from '@services/incidentService'
import type { AIInvestigation, Recommendation, HuntingQuery, TimelineEvent } from '@typings/ai'
import type { Incident } from '@typings/incident'

const PROVIDERS = [
  { value: 'gemini', label: 'Google Gemini', icon: Brain },
  { value: 'openai', label: 'OpenAI GPT', icon: Brain },
  { value: 'ollama', label: 'Ollama', icon: Server },
]

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `${days}d ago`
  return new Date(ts).toLocaleDateString()
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

function ConfidenceGauge({ value, label }: { value: number; label: string }) {
  const color = value >= 0.7 ? '#34D399' : value >= 0.4 ? '#FBBF24' : '#F87171'
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-24 w-24">
        <svg className="h-24 w-24 -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="52" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
          <motion.circle
            cx="60" cy="60" r="52" fill="none"
            stroke={color} strokeWidth="8" strokeLinecap="round"
            strokeDasharray={`${Math.min(value * 100, 100) / 100 * 326.726} 326.726`}
            initial={{ strokeDasharray: '0 326.726' }}
            animate={{ strokeDasharray: `${Math.min(value * 100, 100) / 100 * 326.726} 326.726` }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold" style={{ color }}>{(value * 100).toFixed(0)}%</span>
        </div>
      </div>
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  )
}

function CopyButton({ value, label = 'Copy' }: { value: string; label?: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }, [value])
  return (
    <button onClick={handleCopy} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-[#00F5FF] transition-colors" title={label}>
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? 'Copied' : label}
    </button>
  )
}

function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="prose prose-invert max-w-none prose-headings:text-foreground prose-p:text-muted-foreground prose-strong:text-foreground prose-code:text-[#00F5FF] prose-code:bg-secondary/50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-pre:bg-secondary/50 prose-pre:border prose-pre:border-border prose-a:text-[#00F5FF] prose-ul:text-muted-foreground prose-ol:text-muted-foreground prose-li:text-muted-foreground prose-hr:border-border">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}

function SectionCard({ title, icon: Icon, iconColor, children, defaultOpen = true }: {
  title: string; icon: React.ElementType; iconColor?: string; children: React.ReactNode; defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <Card className="border-[#00F5FF]/10">
      <CardHeader className="cursor-pointer py-3" onClick={() => setOpen(!open)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4" style={iconColor ? { color: iconColor } : undefined} />
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
          </div>
          {open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
        </div>
      </CardHeader>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}>
            <CardContent className="pt-0 pb-4">{children}</CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}

function TimelineCard({ events }: { events: TimelineEvent[] }) {
  if (!events || events.length === 0) return <p className="text-sm text-muted-foreground">No timeline data available</p>
  return (
    <div className="relative space-y-0">
      {events.map((ev, i) => (
        <div key={i} className="flex gap-4 pb-4 last:pb-0">
          <div className="flex flex-col items-center">
            <div className="h-2.5 w-2.5 rounded-full bg-[#00F5FF] mt-1.5" />
            {i < events.length - 1 && <div className="w-px flex-1 bg-border" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{ev.timestamp ? timeAgo(ev.timestamp) : 'Unknown'}</span>
              <Badge variant="outline" className="text-[10px] h-4 px-1">{ev.source}</Badge>
            </div>
            <p className="text-sm font-medium text-foreground mt-0.5">{ev.event}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{ev.detail}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

function RecommendationsList({ items }: { items: Recommendation[] }) {
  if (!items || items.length === 0) return <p className="text-sm text-muted-foreground">No recommendations</p>
  return (
    <div className="space-y-2">
      {items.map((rec, i) => (
        <div key={i} className="rounded-lg border border-border/50 p-3">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className={`text-[10px] h-4 px-1 ${PRIORITY_COLORS[rec.priority] || ''}`}>
              {rec.priority}
            </Badge>
            <span className="text-sm font-medium text-foreground">{rec.action}</span>
          </div>
          <p className="text-xs text-muted-foreground">{rec.details}</p>
        </div>
      ))}
    </div>
  )
}

function HuntingQueriesList({ queries }: { queries: HuntingQuery[] }) {
  if (!queries || queries.length === 0) return <p className="text-sm text-muted-foreground">No hunting queries</p>
  return (
    <div className="space-y-2">
      {queries.map((hq, i) => (
        <div key={i} className="rounded-lg border border-border/50 p-3">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-[10px] h-4 px-1">{hq.type}</Badge>
              <span className="text-sm font-medium text-foreground">{hq.description}</span>
            </div>
            <CopyButton value={hq.query} />
          </div>
          <pre className="text-xs font-mono bg-secondary/30 rounded p-2 mt-1 overflow-x-auto text-[#00F5FF]">{hq.query}</pre>
        </div>
      ))}
    </div>
  )
}

export default function AICenterPage() {
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('')
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [investigation, setInvestigation] = useState<AIInvestigation | null>(null)
  const [investigationLoading, setInvestigationLoading] = useState(false)
  const [investigationError, setInvestigationError] = useState<string | null>(null)
  const reportRef = useRef<HTMLDivElement>(null)

  const incidentsQuery = useQuery({
    queryKey: ['incidents-list'],
    queryFn: async () => {
      const res = await incidentService.getIncidents({ page_size: 100, sort_order: 'desc' })
      return res.data?.items || []
    },
  })

  const historyQuery = useQuery({
    queryKey: ['ai-history'],
    queryFn: () => aiService.listHistory(1, 20),
    refetchInterval: 30000,
  })

  const statsQuery = useQuery({
    queryKey: ['ai-stats'],
    queryFn: aiService.getStats,
    refetchInterval: 30000,
  })

  const getReport = useMutation({
    mutationFn: (incidentId: string) => aiService.getReport(incidentId),
    onSuccess: (data) => {
      setInvestigation(data)
      setInvestigationLoading(false)
    },
    onError: () => {
      setInvestigationLoading(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => aiService.deleteHistory(id),
    onSuccess: () => historyQuery.refetch(),
  })

  const handleInvestigate = async () => {
    if (!selectedIncidentId) return
    setInvestigationLoading(true)
    setInvestigationError(null)
    setInvestigation(null)

    try {
      getReport.mutate(selectedIncidentId, {
        onSuccess: (existing) => {
          if (existing) {
            setInvestigation(existing)
            setInvestigationLoading(false)
          }
        },
        onError: async () => {
          try {
            const result = await aiService.investigate(selectedIncidentId, selectedProvider || undefined)
            setInvestigation(result)
            historyQuery.refetch()
            statsQuery.refetch()
          } catch (err) {
            setInvestigationError(err instanceof Error ? err.message : 'Investigation failed')
          } finally {
            setInvestigationLoading(false)
          }
        },
      })
    } catch {
      setInvestigationLoading(false)
    }
  }

  const handleExportMarkdown = () => {
    if (!investigation) return
    const md = generateMarkdown(investigation)
    const blob = new Blob([md], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `investigation-${investigation.incident_id.slice(0, 8)}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleExportPDF = async () => {
    if (!reportRef.current || !investigation) return
    const html2canvas = (await import('html2canvas')).default
    const { jsPDF } = await import('jspdf')

    const canvas = await html2canvas(reportRef.current, {
      backgroundColor: '#0a0a0f',
      scale: 2,
    })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width
    let heightLeft = pdfHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight)
    heightLeft -= pdf.internal.pageSize.getHeight()

    while (heightLeft > 0) {
      position = heightLeft - pdfHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight)
      heightLeft -= pdf.internal.pageSize.getHeight()
    }

    pdf.save(`investigation-${investigation.incident_id.slice(0, 8)}.pdf`)
  }

  const incidents: Incident[] = incidentsQuery.data || []
  const stats = statsQuery.data
  const history = historyQuery.data

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Investigation Engine"
        description="Enterprise AI-powered incident investigation and analysis"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => { historyQuery.refetch(); statsQuery.refetch() }}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Investigations" value={formatNumber(stats?.total_investigations ?? 0)} icon={Brain} variant="info" />
        <StatCard title="Avg Confidence" value={stats ? `${(stats.average_confidence * 100).toFixed(1)}%` : '0%'} icon={Gauge} variant="success" />
        <StatCard title="Avg Response Time" value={stats ? `${stats.average_latency_ms.toFixed(0)}ms` : '0ms'} icon={Zap} variant="warning" />
        <StatCard title="Providers" value={stats ? Object.keys(stats.provider_usage).length.toString() : '0'} icon={Server} variant="default" />
      </div>

      <Card className="border-[#00F5FF]/20">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Brain className="h-5 w-5 text-[#00F5FF]" />
            AI Investigation
          </CardTitle>
          <CardDescription>Select an incident to analyze with AI</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={selectedIncidentId}
              onChange={(e) => setSelectedIncidentId(e.target.value)}
              className="flex-1 h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
            >
              <option value="">Select an incident...</option>
              {incidentsQuery.isLoading ? (
                <option disabled>Loading incidents...</option>
              ) : incidents.length === 0 ? (
                <option disabled>No investigations available.</option>
              ) : (
                incidents.map((inc) => (
                  <option key={inc.id} value={inc.id}>
                    [{inc.severity?.toUpperCase()}] {inc.title} ({inc.id.slice(0, 8)})
                  </option>
                ))
              )}
            </select>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50 w-40"
            >
              <option value="">Default provider</option>
              {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            <Button
              onClick={handleInvestigate}
              disabled={!selectedIncidentId || investigationLoading}
              variant="accent"
              className="h-10"
            >
              {investigationLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Zap className="mr-2 h-4 w-4" />
              )}
              {investigationLoading ? 'Investigating...' : 'Investigate'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <AnimatePresence>
        {investigationLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Card>
              <CardContent className="p-8">
                <div className="flex flex-col items-center justify-center gap-4 py-12">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  >
                    <Brain className="h-12 w-12 text-[#00F5FF]" />
                  </motion.div>
                  <div className="text-center">
                    <p className="text-lg font-medium text-foreground">AI Investigation in Progress</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Analyzing incident data, correlating events, and generating report...
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Activity className="h-3 w-3 animate-pulse text-[#00F5FF]" />
                    <span>Gathering evidence</span>
                    <Activity className="h-3 w-3 animate-pulse text-[#00F5FF] ml-2" />
                    <span>Querying AI provider</span>
                    <Activity className="h-3 w-3 animate-pulse text-[#00F5FF] ml-2" />
                    <span>Building report</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {investigationError && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Card className="border-red-500/30">
              <CardContent className="p-6 flex items-center gap-3 text-red-400">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <div>
                  <p className="font-medium">Investigation Failed</p>
                  <p className="text-sm text-red-400/80">{investigationError}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {investigation && !investigation.error && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <div ref={reportRef} className="space-y-4">
              <Card className="border-[#00F5FF]/20">
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5 text-[#00F5FF]" />
                      Investigation Report
                    </CardTitle>
                    <CardDescription>
                      Incident: {selectedIncidentId.slice(0, 8)} | Provider: {investigation.provider} | {timeAgo(investigation.created_at)}
                      {investigation.tokens_used ? ` | ${investigation.tokens_used} tokens` : ''}
                      {investigation.latency_ms ? ` | ${investigation.latency_ms}ms` : ''}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={handleExportMarkdown}>
                      <Copy className="mr-2 h-4 w-4" /> Export MD
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleExportPDF}>
                      <Download className="mr-2 h-4 w-4" /> Export PDF
                    </Button>
                  </div>
                </CardHeader>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <ConfidenceGauge value={investigation.confidence_score ?? 0} label="Confidence Score" />
                <ConfidenceGauge value={1 - (investigation.false_positive_probability ?? 0)} label="True Positive Likelihood" />
                <div className="flex flex-col items-center justify-center gap-1">
                  <div className="text-3xl font-bold text-[#00F5FF]">
                    {investigation.tokens_used ?? 0}
                  </div>
                  <span className="text-xs text-muted-foreground">Tokens Used</span>
                  <div className="text-3xl font-bold text-[#FBBF24]">
                    {investigation.latency_ms ?? 0}
                  </div>
                  <span className="text-xs text-muted-foreground">Latency (ms)</span>
                </div>
              </div>

              <SectionCard title="Executive Summary" icon={FileText} iconColor="#00F5FF">
                <MarkdownContent content={investigation.summary || 'No summary available'} />
              </SectionCard>

              {investigation.attack_explanation && (
                <SectionCard title="Attack Explanation" icon={Zap} iconColor="#F87171">
                  <MarkdownContent content={investigation.attack_explanation} />
                </SectionCard>
              )}

              {investigation.root_cause && (
                <SectionCard title="Root Cause" icon={Target} iconColor="#FBBF24">
                  <MarkdownContent content={investigation.root_cause} />
                </SectionCard>
              )}

              {investigation.mitre_explanation && (
                <SectionCard title="MITRE ATT&CK Analysis" icon={Shield} iconColor="#A78BFA">
                  <MarkdownContent content={investigation.mitre_explanation} />
                </SectionCard>
              )}

              {investigation.ioc_summary && (
                <SectionCard title="IOC Summary" icon={Hash} iconColor="#34D399">
                  <MarkdownContent content={investigation.ioc_summary} />
                </SectionCard>
              )}

              {investigation.risk_explanation && (
                <SectionCard title="Risk Assessment" icon={AlertTriangle} iconColor="#F97316">
                  <MarkdownContent content={investigation.risk_explanation} />
                </SectionCard>
              )}

              <SectionCard title="Timeline" icon={Clock} iconColor="#00F5FF">
                <TimelineCard events={investigation.timeline_data || []} />
              </SectionCard>

              <SectionCard title="Recommendations" icon={AlertTriangle} iconColor="#F87171">
                <RecommendationsList items={investigation.recommendations || []} />
              </SectionCard>

              {investigation.containment && (
                <SectionCard title="Containment" icon={Shield} iconColor="#F87171">
                  <MarkdownContent content={investigation.containment} />
                </SectionCard>
              )}

              {investigation.recovery && (
                <SectionCard title="Recovery" icon={RefreshCw} iconColor="#34D399">
                  <MarkdownContent content={investigation.recovery} />
                </SectionCard>
              )}

              <SectionCard title="Hunting Queries" icon={Search} iconColor="#00F5FF">
                <HuntingQueriesList queries={investigation.hunting_queries || []} />
              </SectionCard>
            </div>
          </motion.div>
        )}

        {investigation && investigation.error && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Card className="border-red-500/30">
              <CardContent className="p-6 flex items-center gap-3 text-red-400">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <div>
                  <p className="font-medium">Investigation Error</p>
                  <p className="text-sm text-red-400/80">{investigation.error}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5 text-[#00F5FF]" />
            Investigation History
          </CardTitle>
          <CardDescription>Previous AI investigations</CardDescription>
        </CardHeader>
        <CardContent>
          {historyQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : !history || history.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Brain className="h-12 w-12 mb-3 opacity-20" />
              <p className="text-sm">No investigations yet. Select an incident above to begin.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs text-muted-foreground">
                    <th className="pb-2 font-medium">Incident</th>
                    <th className="pb-2 font-medium">Provider</th>
                    <th className="pb-2 font-medium">Confidence</th>
                    <th className="pb-2 font-medium">Tokens</th>
                    <th className="pb-2 font-medium">Latency</th>
                    <th className="pb-2 font-medium">Date</th>
                    <th className="pb-2 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.items.map((item) => (
                    <tr key={item.id} className="border-b border-border/50 hover:bg-card/50 transition-colors">
                      <td className="py-2.5 pr-4">
                        <div>
                          <span className="text-xs font-medium text-foreground">{item.incident_title || item.incident_id.slice(0, 8)}</span>
                        </div>
                      </td>
                      <td className="py-2.5 pr-4">
                        <Badge variant="outline" className="text-xs font-mono">{item.provider}</Badge>
                      </td>
                      <td className="py-2.5 pr-4">
                        {item.confidence_score != null ? (
                          <span className="font-mono text-xs text-emerald-400">{(item.confidence_score * 100).toFixed(0)}%</span>
                        ) : (
                          <span className="text-xs text-muted-foreground">N/A</span>
                        )}
                      </td>
                      <td className="py-2.5 pr-4 font-mono text-xs text-muted-foreground">{item.tokens_used ?? '-'}</td>
                      <td className="py-2.5 pr-4 font-mono text-xs text-muted-foreground">{item.latency_ms != null ? `${item.latency_ms}ms` : '-'}</td>
                      <td className="py-2.5 pr-4 text-xs text-muted-foreground">{timeAgo(item.created_at)}</td>
                      <td className="py-2.5">
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost" size="icon-sm"
                            onClick={() => {
                              setSelectedIncidentId(item.incident_id)
                              setInvestigationLoading(true)
                              aiService.getReport(item.incident_id).then((r) => {
                                setInvestigation(r)
                                setInvestigationLoading(false)
                              }).catch(() => setInvestigationLoading(false))
                            }}
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                          </Button>
                          <Button variant="ghost" size="icon-sm" onClick={() => deleteMutation.mutate(item.id)}>
                            <Trash2 className="h-3.5 w-3.5 text-red-400" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function generateMarkdown(inv: AIInvestigation): string {
  const sections: string[] = []

  sections.push(`# AI Investigation Report`)
  sections.push(`**Incident:** ${inv.incident_id}`)
  sections.push(`**Provider:** ${inv.provider}`)
  sections.push(`**Date:** ${inv.created_at}`)
  sections.push(`**Confidence:** ${inv.confidence_score != null ? `${(inv.confidence_score * 100).toFixed(0)}%` : 'N/A'}`)
  sections.push(`**Tokens Used:** ${inv.tokens_used ?? 'N/A'}`)
  sections.push(`**Latency:** ${inv.latency_ms != null ? `${inv.latency_ms}ms` : 'N/A'}`)
  sections.push('')

  if (inv.summary) {
    sections.push('## Executive Summary')
    sections.push(inv.summary)
    sections.push('')
  }

  if (inv.attack_explanation) {
    sections.push('## Attack Explanation')
    sections.push(inv.attack_explanation)
    sections.push('')
  }

  if (inv.root_cause) {
    sections.push('## Root Cause')
    sections.push(inv.root_cause)
    sections.push('')
  }

  if (inv.mitre_explanation) {
    sections.push('## MITRE ATT&CK Analysis')
    sections.push(inv.mitre_explanation)
    sections.push('')
  }

  if (inv.ioc_summary) {
    sections.push('## IOC Summary')
    sections.push(inv.ioc_summary)
    sections.push('')
  }

  if (inv.risk_explanation) {
    sections.push('## Risk Assessment')
    sections.push(inv.risk_explanation)
    sections.push('')
  }

  if (inv.recommendations && inv.recommendations.length > 0) {
    sections.push('## Recommendations')
    inv.recommendations.forEach((rec) => {
      sections.push(`- **[${rec.priority.toUpperCase()}]** ${rec.action}`)
      if (rec.details) sections.push(`  - ${rec.details}`)
    })
    sections.push('')
  }

  if (inv.containment) {
    sections.push('## Containment')
    sections.push(inv.containment)
    sections.push('')
  }

  if (inv.recovery) {
    sections.push('## Recovery')
    sections.push(inv.recovery)
    sections.push('')
  }

  if (inv.hunting_queries && inv.hunting_queries.length > 0) {
    sections.push('## Hunting Queries')
    inv.hunting_queries.forEach((hq) => {
      sections.push(`### ${hq.description}`)
      sections.push(`- **Type:** ${hq.type}`)
      sections.push('```')
      sections.push(hq.query)
      sections.push('```')
    })
    sections.push('')
  }

  if (inv.timeline_data && inv.timeline_data.length > 0) {
    sections.push('## Timeline')
    inv.timeline_data.forEach((ev) => {
      sections.push(`- **${ev.timestamp || 'Unknown'}** — ${ev.event} (${ev.source})`)
      if (ev.detail) sections.push(`  - ${ev.detail}`)
    })
    sections.push('')
  }

  return sections.join('\n')
}
