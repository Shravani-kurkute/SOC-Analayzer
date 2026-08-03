import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, X, Shield, Activity, Target,
  ChevronRight, RefreshCw, Hash,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { mitreService } from '@services/mitreService'
import { TACTIC_COLORS, MITRE_SEVERITY_COLORS } from '@typings/mitre'

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

const TACTICS_ORDER = [
  'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
  'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
  'Collection', 'Command and Control', 'Exfiltration', 'Impact',
]

export default function MitrePage() {
  const [search, setSearch] = useState('')
  const [filterTactic, setFilterTactic] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [selectedTechId, setSelectedTechId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'matrix' | 'list'>('matrix')

  const coverageQuery = useQuery({
    queryKey: ['mitre-coverage'],
    queryFn: mitreService.getCoverage,
    refetchInterval: 60_000,
  })

  const techniquesQuery = useQuery({
    queryKey: ['mitre-techniques', filterTactic, search, page],
    queryFn: () => mitreService.listTechniques({
      tactic: filterTactic || undefined,
      search: search || undefined,
      page, page_size: 100,
    }),
    refetchInterval: 30_000,
  })

  const detailQuery = useQuery({
    queryKey: ['mitre-detail', selectedTechId],
    queryFn: () => mitreService.getTechnique(selectedTechId!),
    enabled: !!selectedTechId,
  })

  const coverage = coverageQuery.data
  const techData = techniquesQuery.data
  const techniques = techData?.items || []
  const detail = detailQuery.data

  const tactics = coverage?.by_tactic || []

  const getCoverageColor = (pct: number) => {
    if (pct >= 75) return 'text-emerald-400'
    if (pct >= 50) return 'text-yellow-400'
    if (pct >= 25) return 'text-orange-400'
    return 'text-red-400'
  }

  const getCoverageBg = (pct: number) => {
    if (pct >= 75) return 'bg-emerald-500/20'
    if (pct >= 50) return 'bg-yellow-500/20'
    if (pct >= 25) return 'bg-orange-500/20'
    return 'bg-red-500/20'
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="MITRE ATT&CK"
        description="Enterprise MITRE ATT&CK mapping and coverage analysis"
        actions={
          <>
            <div className="flex items-center gap-1 rounded-lg border border-border/50 p-0.5">
              <button onClick={() => setViewMode('matrix')}
                className={`px-3 py-1.5 text-xs rounded-md transition-colors ${viewMode === 'matrix' ? 'bg-[#00F5FF]/10 text-[#00F5FF]' : 'text-muted-foreground'}`}>
                Matrix
              </button>
              <button onClick={() => setViewMode('list')}
                className={`px-3 py-1.5 text-xs rounded-md transition-colors ${viewMode === 'list' ? 'bg-[#00F5FF]/10 text-[#00F5FF]' : 'text-muted-foreground'}`}>
                List
              </button>
            </div>
            <Button variant="outline" size="sm" onClick={() => { techniquesQuery.refetch(); coverageQuery.refetch() }}>
              <RefreshCw className="mr-2 h-4 w-4" />Refresh
            </Button>
          </>
        }
      />

      {coverage ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Overall Coverage" value={`${coverage.overall_coverage.toFixed(1)}%`}
            description={`${coverage.total_mapped}/${coverage.total_techniques} techniques`}
            icon={Shield} variant={coverage.overall_coverage >= 50 ? 'success' : 'warning'} />
          <StatCard title="Total Techniques" value={formatNumber(coverage.total_techniques)}
            description="MITRE ATT&CK v15.1" icon={Hash} variant="info" />
          <StatCard title="Mapped Techniques" value={formatNumber(coverage.total_mapped)}
            description="With detection coverage" icon={Target} variant="info" />
          <StatCard title="Total Detections" value={formatNumber(coverage.total_detections)}
            description="Mapped to MITRE techniques" icon={Activity} variant="info" />
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <Card key={i} className="p-5"><Skeleton className="h-16 w-full" /></Card>)}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3 xl:grid-cols-4">
        <div className={`${detail ? 'lg:col-span-2 xl:col-span-3' : 'lg:col-span-3 xl:col-span-4'} space-y-4`}>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative flex-1 min-w-[200px] max-w-xs">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Search techniques..." value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }} className="pl-9 h-9 text-sm" />
              {search && (
                <button onClick={() => { setSearch(''); setPage(1) }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
            <select value={filterTactic || ''} onChange={(e) => { setFilterTactic(e.target.value || null); setPage(1) }}
              className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground">
              <option value="">All tactics</option>
              {TACTICS_ORDER.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {viewMode === 'matrix' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {TACTICS_ORDER.filter(t => !filterTactic || t === filterTactic).map((tactic) => {
                const tacticTechs = techniques.filter(t => t.tactic === tactic)
                const tacticCoverage = tactics.find(t => t.tactic === tactic)
                if (!tacticTechs.length && !search) return null
                return (
                  <Card key={tactic} className="border-border/50">
                    <CardHeader className="pb-2 pt-3 px-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-[11px] font-semibold flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: TACTIC_COLORS[tactic] || '#666' }} />
                          {tactic}
                        </CardTitle>
                        {tacticCoverage && (
                          <span className={`text-[10px] font-mono ${getCoverageColor(tacticCoverage.coverage_percent)}`}>
                            {tacticCoverage.coverage_percent.toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="px-3 pb-3">
                      <div className="space-y-0.5">
                        {(search ? tacticTechs.filter(t =>
                          t.name.toLowerCase().includes(search.toLowerCase()) ||
                          t.technique_id.toLowerCase().includes(search.toLowerCase())
                        ) : tacticTechs).slice(0, 12).map((tech) => {
                          const sevColor = MITRE_SEVERITY_COLORS[tech.severity] || 'text-muted-foreground'
                          return (
                            <button key={tech.id} onClick={() => setSelectedTechId(tech.technique_id)}
                              className={`w-full text-left flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors hover:bg-accent/30 ${
                                selectedTechId === tech.technique_id ? 'bg-[#00F5FF]/10' : ''
                              }`}>
                              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${sevColor.split(' ')[0]}`} />
                              <span className="font-mono text-[10px] text-muted-foreground shrink-0">{tech.technique_id}</span>
                              <span className="truncate">{tech.name}</span>
                              {tech.is_subtechnique && <span className="text-[9px] text-muted-foreground ml-auto">sub</span>}
                            </button>
                          )
                        })}
                        {tacticTechs.length > 12 && (
                          <p className="text-[9px] text-muted-foreground text-center pt-1">+{tacticTechs.length - 12} more</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            <div className="rounded-lg border border-border/50 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border/50 bg-muted/30">
                      <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase">ID</th>
                      <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase">Name</th>
                      <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase">Tactic</th>
                      <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase">Severity</th>
                      <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase">Score</th>
                      <th className="px-3 py-2.5 text-left text-[10px] font-medium text-muted-foreground uppercase">Sub</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/30">
                    {techniques.map((tech) => (
                      <motion.tr key={tech.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        onClick={() => setSelectedTechId(tech.technique_id)}
                        className={`cursor-pointer transition-colors hover:bg-accent/20 ${selectedTechId === tech.technique_id ? 'bg-[#00F5FF]/5' : ''}`}>
                        <td className="px-3 py-2 font-mono text-xs">{tech.technique_id}</td>
                        <td className="px-3 py-2 text-xs">{tech.name}</td>
                        <td className="px-3 py-2">
                          <span className="inline-flex items-center gap-1 text-[10px]">
                            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: TACTIC_COLORS[tech.tactic] || '#666' }} />
                            {tech.tactic}
                          </span>
                        </td>
                        <td className="px-3 py-2">
                          <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${MITRE_SEVERITY_COLORS[tech.severity] || ''}`}>
                            {tech.severity}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-xs font-mono">{tech.score.toFixed(1)}</td>
                        <td className="px-3 py-2 text-[10px] text-muted-foreground">{tech.is_subtechnique ? 'Yes' : 'No'}</td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {techData && techData.total_pages > 1 && (
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Page {techData.page} of {techData.total_pages}</span>
              <div className="flex gap-1">
                <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="h-7 text-xs px-2">Prev</Button>
                <Button variant="outline" size="sm" disabled={page >= techData.total_pages} onClick={() => setPage(p => p + 1)} className="h-7 text-xs px-2">Next</Button>
              </div>
            </div>
          )}
        </div>

        {detail && (
          <div className="lg:col-span-1 space-y-4">
            <AnimatePresence mode="wait">
              <motion.div key={detail.technique.technique_id} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
                <Card>
                  <CardHeader className="pb-2">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="font-mono text-[10px]">{detail.technique.technique_id}</Badge>
                      <Badge variant={detail.technique.severity === 'critical' ? 'critical' : detail.technique.severity === 'high' ? 'destructive' : 'default'} className="text-[10px]">
                        {detail.technique.severity}
                      </Badge>
                    </div>
                    <CardTitle className="text-sm">{detail.technique.name}</CardTitle>
                    <CardDescription className="flex items-center gap-1 mt-1">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: TACTIC_COLORS[detail.technique.tactic] || '#666' }} />
                      {detail.technique.tactic}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Score</span>
                        <span className="font-mono">{detail.technique.score.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Detection Coverage</span>
                        <span className="font-mono">{(detail.detection_coverage * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Mappings</span>
                        <span className="font-mono">{detail.mapped_count}</span>
                      </div>
                      {detail.technique.kill_chain_phase && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Kill Chain</span>
                          <span className="font-mono">{detail.technique.kill_chain_phase}</span>
                        </div>
                      )}
                      {detail.technique.is_subtechnique && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Parent</span>
                          <span className="font-mono">{detail.technique.parent_technique_id}</span>
                        </div>
                      )}
                      {detail.technique.detection_rules && detail.technique.detection_rules.length > 0 && (
                        <div className="pt-2 border-t border-border/40">
                          <span className="text-muted-foreground block mb-1">Detection Rules</span>
                          <div className="flex flex-wrap gap-1">
                            {detail.technique.detection_rules.map(r => (
                              <Badge key={r} variant="outline" className="text-[9px]">{r}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {detail.technique.ioc_indicators && detail.technique.ioc_indicators.length > 0 && (
                        <div className="pt-2 border-t border-border/40">
                          <span className="text-muted-foreground block mb-1">IOC Indicators</span>
                          <div className="flex flex-wrap gap-1">
                            {detail.technique.ioc_indicators.map(i => (
                              <Badge key={i} variant="outline" className="text-[9px]">{i}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {detail.mappings.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/40">
                        <span className="text-xs text-muted-foreground block mb-2">Recent Mappings</span>
                        <div className="space-y-1 max-h-40 overflow-y-auto">
                          {detail.mappings.slice(0, 10).map(m => (
                            <div key={m.id} className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                              <span className="px-1 rounded bg-muted">{m.mapped_type}</span>
                              <span className="truncate font-mono">{m.mapped_id}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {detail.related_techniques.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/40">
                        <span className="text-xs text-muted-foreground block mb-2">Related Techniques</span>
                        <div className="space-y-1">
                          {detail.related_techniques.map(r => (
                            <button key={r.technique_id} onClick={() => setSelectedTechId(r.technique_id)}
                              className="flex items-center gap-1.5 text-[10px] text-muted-foreground hover:text-foreground w-full text-left">
                              <ChevronRight className="h-3 w-3 shrink-0" />
                              <span className="font-mono">{r.technique_id}</span>
                              <span className="truncate">{r.name}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </AnimatePresence>
          </div>
        )}
      </div>

      {coverage && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4 text-[#00F5FF]" />
              ATT&CK Coverage by Tactic
            </CardTitle>
            <CardDescription>Detection coverage across all MITRE ATT&CK tactics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {TACTICS_ORDER.map((tactic) => {
                const stat = tactics.find(t => t.tactic === tactic)
                if (!stat) return null
                const pct = stat.coverage_percent
                return (
                  <div key={tactic}>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: TACTIC_COLORS[tactic] || '#666' }} />
                        <span className="text-xs font-medium">{tactic}</span>
                      </div>
                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                        <span>{stat.mapped_techniques}/{stat.total_techniques} techniques</span>
                        <span className={`font-mono font-medium ${getCoverageColor(pct)}`}>{pct.toFixed(0)}%</span>
                      </div>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <motion.div
                        className={`h-full rounded-full ${getCoverageBg(pct)}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
