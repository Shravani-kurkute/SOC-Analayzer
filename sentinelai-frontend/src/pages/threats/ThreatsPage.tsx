import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Shield, Globe, Hash, ExternalLink, Server, AlertTriangle,
  Activity, Copy, Check,
  AlertCircle, RefreshCw, Filter,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { threatIntelService } from '@services/threatIntelService'
import type { ThreatIntelResult } from '@typings/threatIntel'

const IOC_TYPES = [
  { value: 'ip', label: 'IPv4', icon: Globe, color: '#00F5FF' },
  { value: 'ipv6', label: 'IPv6', icon: Globe, color: '#00F5FF' },
  { value: 'domain', label: 'Domain', icon: Globe, color: '#A78BFA' },
  { value: 'url', label: 'URL', icon: ExternalLink, color: '#F472B6' },
  { value: 'hostname', label: 'Hostname', icon: Server, color: '#34D399' },
  { value: 'md5', label: 'MD5', icon: Hash, color: '#FBBF24' },
  { value: 'sha1', label: 'SHA1', icon: Hash, color: '#FB923C' },
  { value: 'sha256', label: 'SHA256', icon: Hash, color: '#F87171' },
]

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

function timeAgo(ts: string | null): string {
  if (!ts) return 'Never'
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

function ScoreBar({ score }: { score: number }) {
  const color = score > 0.7 ? '#F87171' : score > 0.4 ? '#FBBF24' : '#34D399'
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 rounded-full bg-secondary">
        <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${Math.min(score * 100, 100)}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-mono w-10 text-right">{(score * 100).toFixed(0)}%</span>
    </div>
  )
}

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }, [value])
  return (
    <button onClick={handleCopy} className="text-muted-foreground hover:text-[#00F5FF] transition-colors" title="Copy">
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  )
}

function MaliciousBadge({ isMalicious }: { isMalicious: boolean }) {
  if (isMalicious) return <Badge variant="destructive" className="text-xs">Malicious</Badge>
  return <Badge variant="secondary" className="text-xs bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Harmless</Badge>
}

export default function ThreatsPage() {
  const [searchValue, setSearchValue] = useState('')
  const [searchType, setSearchType] = useState<string>('ip')
  const [lookupResult, setLookupResult] = useState<ThreatIntelResult | null>(null)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [lookupError, setLookupError] = useState<string | null>(null)
  const [filterType] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const statsQuery = useQuery({
    queryKey: ['threat-intel-stats'],
    queryFn: threatIntelService.getStats,
    refetchInterval: 30000,
  })

  const listQuery = useQuery({
    queryKey: ['threat-intel-list', page, filterType],
    queryFn: () => threatIntelService.list({ page, page_size: 20, sort_by: 'last_analysis', sort_order: 'desc', ioc_type: filterType || undefined }),
    refetchInterval: 30000,
  })

  const handleLookup = async () => {
    if (!searchValue.trim()) return
    setLookupLoading(true)
    setLookupError(null)
    setLookupResult(null)
    try {
      const result = await threatIntelService.lookup(searchType, searchValue.trim())
      setLookupResult(result)
    } catch (err) {
      setLookupError(err instanceof Error ? err.message : 'Lookup failed')
    } finally {
      setLookupLoading(false)
    }
  }

  const stats = statsQuery.data
  const listData = listQuery.data

  return (
    <div className="space-y-6">
      <PageHeader title="Threat Intelligence" description="Enrich IOCs with external threat intelligence providers" actions={
        <Button variant="outline" size="sm" onClick={() => { statsQuery.refetch(); listQuery.refetch() }}>
          <RefreshCw className="mr-2 h-4 w-4" /> Refresh
        </Button>
      } />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard title="Total IOC Lookups" value={formatNumber(stats?.total_iocs ?? 0)} icon={Shield} variant="info" />
        <StatCard title="Malicious" value={formatNumber(stats?.malicious_count ?? 0)} icon={AlertTriangle} variant="danger" />
        <StatCard title="Harmless" value={formatNumber(stats?.harmless_count ?? 0)} icon={Shield} variant="success" />
        <StatCard title="Types" value={Object.keys(stats?.by_type ?? {}).length.toString()} icon={Filter} variant="default" />
        <StatCard title="Providers" value={Object.keys(stats?.provider_stats ?? {}).length.toString()} icon={Activity} variant="warning" />
      </div>

      <Card className="border-[#00F5FF]/20">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="h-5 w-5 text-[#00F5FF]" />
            IOC Lookup
          </CardTitle>
          <CardDescription>Search any IOC across threat intelligence providers</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              className="h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
            >
              {IOC_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <Input
              placeholder="Enter IOC value (IP, domain, hash, etc.)"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
              className="flex-1 h-10"
            />
            <Button onClick={handleLookup} disabled={lookupLoading} variant="accent" className="h-10">
              {lookupLoading ? <Activity className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
              Lookup
            </Button>
          </div>
        </CardContent>
      </Card>

      <AnimatePresence>
        {lookupLoading && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Card><CardContent className="p-6"><Skeleton className="h-48 w-full" /></CardContent></Card>
          </motion.div>
        )}

        {lookupError && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Card className="border-red-500/30">
              <CardContent className="p-6 flex items-center gap-3 text-red-400">
                <AlertCircle className="h-5 w-5" />
                <span>{lookupError}</span>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {lookupResult && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Card className="border-[#00F5FF]/20">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Badge variant="outline" className="text-xs font-mono">{lookupResult.ioc_type}</Badge>
                    <span className="font-mono text-sm">{lookupResult.ioc_value}</span>
                    <CopyButton value={lookupResult.ioc_value} />
                  </CardTitle>
                  <CardDescription>
                    {lookupResult.cached ? 'Retrieved from cache' : 'Fresh lookup from providers'}
                    {' | '}
                    Last analyzed: {timeAgo(lookupResult.last_analysis)}
                  </CardDescription>
                </div>
                <MaliciousBadge isMalicious={lookupResult.is_malicious} />
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Reputation Score</span>
                    <ScoreBar score={lookupResult.reputation_score} />
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Confidence</span>
                    <ScoreBar score={lookupResult.confidence} />
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">Country</span>
                    <span className="font-mono text-sm">{lookupResult.country || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">ASN</span>
                    <span className="font-mono text-sm">{lookupResult.asn || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">Malicious</span>
                    <span className="font-mono text-sm text-red-400">{lookupResult.malicious_count}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">Suspicious</span>
                    <span className="font-mono text-sm text-yellow-400">{lookupResult.suspicious_count}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">Harmless</span>
                    <span className="font-mono text-sm text-emerald-400">{lookupResult.harmless_count}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">ASN Org</span>
                    <span className="font-mono text-sm">{lookupResult.asn_org || 'N/A'}</span>
                  </div>
                </div>

                {lookupResult.tags && lookupResult.tags.length > 0 && (
                  <div className="mb-4">
                    <span className="text-xs text-muted-foreground block mb-2">Tags</span>
                    <div className="flex flex-wrap gap-1.5">
                      {lookupResult.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs bg-[#00F5FF]/5 border-[#00F5FF]/20">{tag}</Badge>
                      ))}
                    </div>
                  </div>
                )}

                {lookupResult.providers && lookupResult.providers.length > 0 && (
                  <div>
                    <span className="text-xs text-muted-foreground block mb-2">Provider Results</span>
                    <div className="space-y-2">
                      {lookupResult.providers.map((pr) => (
                        <div key={pr.name} className="flex items-center justify-between rounded-lg border border-border/50 bg-card/50 p-3">
                          <div className="flex items-center gap-3">
                            <Badge variant="outline" className="text-xs">{pr.name}</Badge>
                            <span className={`text-xs ${pr.reputation === 'malicious' ? 'text-red-400' : pr.reputation === 'harmless' ? 'text-emerald-400' : 'text-muted-foreground'}`}>
                              {pr.reputation || 'Unknown'}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            <span>Confidence: {(pr.confidence * 100).toFixed(0)}%</span>
                            <span>{timeAgo(pr.looked_up_at)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5 text-[#00F5FF]" />
            Recent Lookups
          </CardTitle>
          <CardDescription>Previously enriched IOC entries</CardDescription>
        </CardHeader>
        <CardContent>
          {listQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : !listData || listData.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Search className="h-12 w-12 mb-3 opacity-20" />
              <p className="text-sm">No IOC lookups yet. Search an IOC above.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-muted-foreground">
                      <th className="pb-2 font-medium">Type</th>
                      <th className="pb-2 font-medium">Value</th>
                      <th className="pb-2 font-medium">Score</th>
                      <th className="pb-2 font-medium">Status</th>
                      <th className="pb-2 font-medium">Country</th>
                      <th className="pb-2 font-medium">ASN</th>
                      <th className="pb-2 font-medium">Last Analysis</th>
                    </tr>
                  </thead>
                  <tbody>
                    {listData.items.map((item) => (
                      <tr key={item.id} className="border-b border-border/50 hover:bg-card/50 transition-colors">
                        <td className="py-2.5 pr-4">
                          <Badge variant="outline" className="text-xs font-mono">{item.ioc_type}</Badge>
                        </td>
                        <td className="py-2.5 pr-4">
                          <span className="font-mono text-xs">{item.ioc_value.length > 40 ? `${item.ioc_value.slice(0, 40)}...` : item.ioc_value}</span>
                        </td>
                        <td className="py-2.5 pr-4">
                          <div className="w-20">
                            <ScoreBar score={item.reputation_score} />
                          </div>
                        </td>
                        <td className="py-2.5 pr-4"><MaliciousBadge isMalicious={item.is_malicious} /></td>
                        <td className="py-2.5 pr-4 font-mono text-xs">{item.country || '-'}</td>
                        <td className="py-2.5 pr-4 font-mono text-xs">{item.asn || '-'}</td>
                        <td className="py-2.5 text-xs text-muted-foreground">{timeAgo(item.last_analysis)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {listData.total_pages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <span className="text-xs text-muted-foreground">Page {page} of {listData.total_pages}</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Previous</Button>
                    <Button variant="outline" size="sm" disabled={page >= listData.total_pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
