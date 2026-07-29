import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Filter, X, Copy, Check, ExternalLink, Clock,
  Activity, Shield, Globe, Server, Hash, Terminal,
  FileText, Download, RefreshCw, ChevronDown, ChevronUp,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { iocService } from '@services/iocService'
import { IOC_TYPE_MAP, IOC_SEVERITY_COLORS, type IocEntry } from '@typings/ioc'

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `${days}d ago`
  return new Date(ts).toLocaleDateString()
}

function IocIcon({ type, className }: { type: string; className?: string }) {
  const IconComponent = IOC_ICONS[type] || Shield
  const color = IOC_TYPE_MAP[type]?.color
  return <IconComponent className={className} style={color ? { color } : undefined} />
}

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }, [value])
  return (
    <button onClick={handleCopy} className="text-muted-foreground hover:text-[#00F5FF] transition-colors" title="Copy to clipboard">
      {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
    </button>
  )
}

const IOC_ICONS: Record<string, React.ElementType> = {
  ipv4: Globe, ipv6: Globe, domain: Globe, url: ExternalLink,
  hostname: Server, email: Server, username: Terminal, md5: Hash,
  sha1: Hash, sha256: Hash, registry_key: FileText, windows_sid: FileText,
  process_name: Terminal, executable_path: FileText, command_line: Terminal,
  cve: Shield, mitre_technique: Shield, port: Activity, protocol: Activity,
}

export default function IocPage() {
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState<string | null>(null)
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState('last_seen')
  const [sortOrder, setSortOrder] = useState('desc')
  const [page, setPage] = useState(1)
  const [selectedIoc, setSelectedIoc] = useState<IocEntry | null>(null)

  const statsQuery = useQuery({
    queryKey: ['ioc-stats'],
    queryFn: iocService.getStats,
    refetchInterval: 30_000,
  })

  const iocsQuery = useQuery({
    queryKey: ['iocs', page, sortBy, sortOrder, filterType, filterSeverity, filterStatus, search],
    queryFn: () => iocService.list({
      page, page_size: 20, sort_by: sortBy, sort_order: sortOrder,
      ioc_type: filterType || undefined, severity: filterSeverity || undefined,
      status: filterStatus || undefined,
    }),
    refetchInterval: 15_000,
  })

  const iocDetailQuery = useQuery({
    queryKey: ['ioc-detail', selectedIoc?.id],
    queryFn: () => iocService.get(selectedIoc!.id),
    enabled: !!selectedIoc?.id,
  })

  const stats = statsQuery.data
  const iocData = iocsQuery.data
  const iocs = iocData?.items || []
  const total = iocData?.total || 0
  const totalPages = iocData?.total_pages || 1
  const detail = iocDetailQuery.data

  const IOC_TYPES = Object.keys(IOC_TYPE_MAP)
  const SEVERITIES = ['critical', 'high', 'medium', 'low']
  const STATUSES = ['active', 'suspicious', 'false_positive', 'archived']

  return (
    <div className="space-y-6">
      <PageHeader
        title="IOC Explorer"
        description="Indicators of Compromise extracted from security events"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => { setFilterType(null); setFilterSeverity(null); setFilterStatus(null); setSearch(''); setPage(1) }}>
              <Filter className="mr-2 h-4 w-4" />Clear Filters
            </Button>
            <Button variant="outline" size="sm"><Download className="mr-2 h-4 w-4" />Export</Button>
            <Button variant="outline" size="sm" onClick={() => { iocsQuery.refetch(); statsQuery.refetch() }}>
              <RefreshCw className="mr-2 h-4 w-4" />Refresh
            </Button>
          </>
        }
      />

      {statsQuery.isError && (
        <Card className="border-red-500/30 bg-red-500/5 p-4">
          <p className="text-sm text-red-400">Failed to load IOC statistics</p>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {stats ? (
          <>
            <StatCard title="Total IOCs" value={formatNumber(stats.total)} description="Extracted indicators" icon={Shield} variant="info" />
            <StatCard title="Unique IPs" value={formatNumber(stats.unique_ips)} description="IPv4 & IPv6 addresses" icon={Globe} variant="info" />
            <StatCard title="Unique Domains" value={formatNumber(stats.unique_domains)} description="Domain indicators" icon={Globe} variant="warning" />
            <StatCard title="Unique Hashes" value={formatNumber(stats.unique_hashes)} description="MD5, SHA1, SHA256" icon={Hash} variant="danger" />
            <StatCard title="IOC Types" value={Object.keys(stats.by_type).length} description="Distinct IOC categories" icon={Activity} variant="default" />
          </>
        ) : (
          Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="p-5"><Skeleton className="h-16 w-full" /></Card>
          ))
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search IOCs..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="pl-9 h-9 text-sm"
          />
          {search && (
            <button onClick={() => { setSearch(''); setPage(1) }} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="h-3 w-3" />
            </button>
          )}
        </div>
        <select value={filterType || ''} onChange={(e) => { setFilterType(e.target.value || null); setPage(1) }}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground">
          <option value="">All types</option>
          {IOC_TYPES.map(t => {
            const info = IOC_TYPE_MAP[t]
            return <option key={t} value={t}>{info?.label || t}</option>
          })}
        </select>
        <select value={filterSeverity || ''} onChange={(e) => { setFilterSeverity(e.target.value || null); setPage(1) }}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground">
          <option value="">All severities</option>
          {SEVERITIES.map(s => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
        <select value={filterStatus || ''} onChange={(e) => { setFilterStatus(e.target.value || null); setPage(1) }}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground">
          <option value="">All status</option>
          {STATUSES.map(s => (
            <option key={s} value={s}>{s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
          ))}
        </select>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground">
          <option value="last_seen">Last Seen</option>
          <option value="first_seen">First Seen</option>
          <option value="occurrences">Occurrences</option>
          <option value="severity">Severity</option>
          <option value="ioc_type">Type</option>
        </select>
        <button onClick={() => setSortOrder(o => o === 'desc' ? 'asc' : 'desc')}
          className="h-9 px-2 rounded-md border border-input bg-background text-muted-foreground hover:text-foreground text-xs">
          {sortOrder === 'desc' ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-2">
          {iocsQuery.isError ? (
            <Card className="border-red-500/30 bg-red-500/5 p-4">
              <p className="text-sm text-red-400">Failed to load IOCs</p>
            </Card>
          ) : iocs.length > 0 ? (
            <>
              <div className="rounded-lg border border-border/50 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border/50 bg-muted/30">
                        <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Type</th>
                        <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Value</th>
                        <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Severity</th>
                        <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                        <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Occurrences</th>
                        <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Last Seen</th>
                        <th className="px-3 py-2.5 text-right text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/30">
                      {iocs.map((ioc) => {
                        const typeInfo = IOC_TYPE_MAP[ioc.ioc_type] || { label: ioc.ioc_type, color: '#6b7280' }
                        return (
                          <motion.tr
                            key={ioc.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            onClick={() => setSelectedIoc(ioc)}
                            className={`cursor-pointer transition-colors hover:bg-accent/20 ${selectedIoc?.id === ioc.id ? 'bg-[#00F5FF]/5' : ''}`}
                          >
                            <td className="px-3 py-2.5">
                              <div className="flex items-center gap-1.5">
                                <IocIcon type={ioc.ioc_type} className="h-3.5 w-3.5" />
                                <span className="text-[11px] font-medium">{typeInfo.label}</span>
                              </div>
                            </td>
                            <td className="px-3 py-2.5">
                              <div className="flex items-center gap-1.5">
                                <span className="font-mono text-xs text-foreground truncate max-w-[200px]">{ioc.normalized_value}</span>
                                <CopyButton value={ioc.normalized_value} />
                              </div>
                            </td>
                            <td className="px-3 py-2.5">
                              <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${IOC_SEVERITY_COLORS[ioc.severity] || 'text-muted-foreground bg-muted border-border'}`}>
                                {ioc.severity}
                              </span>
                            </td>
                            <td className="px-3 py-2.5">
                              <span className={`text-[10px] ${ioc.status === 'active' ? 'text-emerald-400' : ioc.status === 'suspicious' ? 'text-yellow-400' : 'text-muted-foreground'}`}>
                                {ioc.status}
                              </span>
                            </td>
                            <td className="px-3 py-2.5">
                              <span className="text-xs font-mono">{ioc.occurrences}</span>
                            </td>
                            <td className="px-3 py-2.5">
                              <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
                                <Clock className="h-3 w-3" />
                                {timeAgo(ioc.last_seen)}
                              </div>
                            </td>
                            <td className="px-3 py-2.5 text-right">
                              <CopyButton value={ioc.normalized_value} />
                            </td>
                          </motion.tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Showing {(page - 1) * 20 + 1}-{Math.min(page * 20, total)} of {total}</span>
                <div className="flex items-center gap-1">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="h-7 text-xs px-2">Prev</Button>
                  {Array.from({ length: Math.min(totalPages, 5) }).map((_, i) => {
                    const p = i + 1
                    return (
                      <button key={p} onClick={() => setPage(p)}
                        className={`h-7 w-7 rounded text-xs font-medium ${page === p ? 'bg-[#00F5FF]/10 text-[#00F5FF]' : 'text-muted-foreground hover:text-foreground'}`}>
                        {p}
                      </button>
                    )
                  })}
                  <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)} className="h-7 text-xs px-2">Next</Button>
                </div>
              </div>
            </>
          ) : iocsQuery.isLoading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded-lg" />
            ))
          ) : (
            <Card>
              <CardContent className="p-12">
                <div className="flex flex-col items-center justify-center text-sm text-muted-foreground">
                  <Shield className="mb-3 h-12 w-12" />
                  <p className="font-medium">No IOCs found</p>
                  <p className="text-xs mt-1">IOCs are extracted from parsed security events</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="lg:col-span-1 space-y-4">
          {detail ? (
            <AnimatePresence mode="wait">
              <motion.div key={detail.id} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="space-y-4">
                <Card>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <IocIcon type={detail.ioc_type} className="h-4 w-4" />
                        {IOC_TYPE_MAP[detail.ioc_type]?.label || detail.ioc_type}
                      </CardTitle>
                      <Badge variant={detail.severity === 'critical' ? 'critical' : detail.severity === 'high' ? 'destructive' : 'default'} className="text-[10px]">
                        {detail.severity}
                      </Badge>
                    </div>
                    <CardDescription className="mt-1">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs text-foreground break-all">{detail.normalized_value}</span>
                        <CopyButton value={detail.normalized_value} />
                      </div>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Status</span>
                        <span className={detail.status === 'active' ? 'text-emerald-400' : detail.status === 'suspicious' ? 'text-yellow-400' : 'text-muted-foreground'}>
                          {detail.status.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Confidence</span>
                        <span className="font-mono">{(detail.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Occurrences</span>
                        <span className="font-mono">{detail.occurrences}</span>
                      </div>
                      {detail.source_ip && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Source IP</span>
                          <span className="font-mono">{detail.source_ip}</span>
                        </div>
                      )}
                      {detail.source_log && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Source Log</span>
                          <span className="truncate max-w-[150px]">{detail.source_log}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">First Seen</span>
                        <span className="font-mono">{new Date(detail.first_seen).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Last Seen</span>
                        <span className="font-mono">{timeAgo(detail.last_seen)}</span>
                      </div>
                      {detail.kill_chain_phase && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Kill Chain Phase</span>
                          <span className="font-mono">{detail.kill_chain_phase}</span>
                        </div>
                      )}
                      {detail.context && (
                        <div className="pt-2 border-t border-border/40">
                          <span className="text-muted-foreground block mb-1">Context</span>
                          <p className="text-[11px] text-foreground/80 leading-relaxed">{detail.context}</p>
                        </div>
                      )}
                      {detail.tags && Object.keys(detail.tags).length > 0 && (
                        <div className="pt-2 border-t border-border/40">
                          <span className="text-muted-foreground block mb-1">Tags</span>
                          <div className="flex flex-wrap gap-1">
                            {Object.entries(detail.tags).map(([k, v]) => (
                              <Badge key={k} variant="outline" className="text-[9px] px-1 py-0">{k}:{String(v)}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {detail.source_ids && detail.source_ids.length > 0 && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs">Source Events ({detail.source_ids.length})</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-1">
                        {detail.source_ids.slice(0, 10).map((sid) => (
                          <div key={sid} className="flex items-center gap-1.5 text-[11px] font-mono text-muted-foreground">
                            <FileText className="h-3 w-3 shrink-0" />
                            <span className="truncate">{sid}</span>
                          </div>
                        ))}
                        {detail.source_ids.length > 10 && (
                          <p className="text-[10px] text-muted-foreground">...and {detail.source_ids.length - 10} more</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </motion.div>
            </AnimatePresence>
          ) : selectedIoc && iocs.length > 0 ? null : iocs.length > 0 ? (
            <Card>
              <CardContent className="p-8">
                <div className="flex flex-col items-center justify-center text-sm text-muted-foreground">
                  <Shield className="mb-3 h-10 w-10" />
                  <p className="font-medium">Select an IOC</p>
                  <p className="text-xs mt-1">Click on an IOC row to view details</p>
                </div>
              </CardContent>
            </Card>
          ) : iocDetailQuery.isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-48 w-full rounded-lg" />
              <Skeleton className="h-32 w-full rounded-lg" />
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
