import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  GitBranch, Play, RefreshCw, Filter, Download,
  Search, X, Clock, AlertTriangle, Activity, Zap, Shield,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { correlationService } from '@services/correlationService'
import { AttackTimeline } from '@components/correlation/AttackTimeline'
import { RelatedEvents } from '@components/correlation/RelatedEvents'

const GROUP_TYPE_COLORS: Record<string, string> = {
  ssh_session: 'text-cyan-400 bg-cyan-500/10',
  port_scan: 'text-orange-400 bg-orange-500/10',
  firewall_block: 'text-red-400 bg-red-500/10',
  web_attack: 'text-purple-400 bg-purple-500/10',
  web_error_chain: 'text-yellow-400 bg-yellow-500/10',
  attack_chain: 'text-pink-400 bg-pink-500/10',
  credential_stuffing: 'text-amber-400 bg-amber-500/10',
  credential_compromise: 'text-rose-400 bg-rose-500/10',
  targeted_attack: 'text-indigo-400 bg-indigo-500/10',
}

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
  return `${days}d ago`
}

export default function CorrelationPage() {
  const queryClient = useQueryClient()
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null)
  const [searchIp, setSearchIp] = useState('')
  const [filterType, setFilterType] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState<string | null>(null)

  const statsQuery = useQuery({
    queryKey: ['correlation-stats'],
    queryFn: correlationService.getStats,
    refetchInterval: 30_000,
  })

  const groupsQuery = useQuery({
    queryKey: ['correlation-groups', filterType, filterStatus, searchIp],
    queryFn: () => correlationService.getGroups({
      group_type: filterType || undefined,
      status: filterStatus || undefined,
      source_ip: searchIp || undefined,
      limit: 50,
    }),
    refetchInterval: 30_000,
  })

  const groupDetailQuery = useQuery({
    queryKey: ['correlation-group', selectedGroup],
    queryFn: () => correlationService.getGroup(selectedGroup!),
    enabled: !!selectedGroup,
  })

  const runMutation = useMutation({
    mutationFn: correlationService.runAllCorrelations,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['correlation-groups'] })
      queryClient.invalidateQueries({ queryKey: ['correlation-stats'] })
    },
  })

  const stats = statsQuery.data
  const groups = groupsQuery.data
  const selected = groupDetailQuery.data

  return (
    <div className="space-y-6">
      <PageHeader
        title="Event Correlation"
        description="Correlated event groups and attack chains"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => { setFilterType(null); setFilterStatus(null); setSearchIp('') }}>
              <Filter className="mr-2 h-4 w-4" />Clear Filters
            </Button>
            <Button variant="outline" size="sm"><Download className="mr-2 h-4 w-4" />Export</Button>
            <Button
              variant="accent" size="sm"
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
            >
              {runMutation.isPending ? (
                <><RefreshCw className="mr-2 h-4 w-4 animate-spin" />Running...</>
              ) : (
                <><Play className="mr-2 h-4 w-4" />Run Correlation</>
              )}
            </Button>
          </>
        }
      />

      {statsQuery.isError && (
        <Card className="border-red-500/30 bg-red-500/5 p-4">
          <p className="text-sm text-red-400">Failed to load correlation stats</p>
        </Card>
      )}

      {runMutation.data && (
        <Card className="border-[#00F5FF]/30 bg-[#00F5FF]/5 p-4">
          <div className="flex items-center gap-2 text-sm text-[#00F5FF]">
            <Activity className="h-4 w-4" />
            {runMutation.data.message}
          </div>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats ? (
          <>
            <StatCard title="Total Groups" value={formatNumber(stats.total_groups)} description="Correlated event groups" icon={GitBranch} variant="info" />
            <StatCard title="Open Groups" value={stats.open_groups} description="Requiring investigation" icon={AlertTriangle} variant="warning" />
            <StatCard title="Avg Risk Score" value={`${stats.avg_risk_score.toFixed(1)}`} description="Average risk across groups" icon={Zap} variant={stats.avg_risk_score > 5 ? 'danger' : 'default'} />
            <StatCard title="Events Correlated" value={formatNumber(stats.total_events_correlated)} description="Total correlated events" icon={Activity} variant="info" />
          </>
        ) : (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5"><Skeleton className="h-16 w-full" /></Card>
          ))
        )}
      </div>

      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Filter by IP..."
            value={searchIp}
            onChange={(e) => setSearchIp(e.target.value)}
            className="pl-9 h-9 text-sm"
          />
          {searchIp && (
            <button onClick={() => setSearchIp('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="h-3 w-3" />
            </button>
          )}
        </div>
        <select
          value={filterType || ''}
          onChange={(e) => setFilterType(e.target.value || null)}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground"
        >
          <option value="">All types</option>
          <option value="ssh_session">SSH Session</option>
          <option value="port_scan">Port Scan</option>
          <option value="firewall_block">Firewall Block</option>
          <option value="web_attack">Web Attack</option>
          <option value="attack_chain">Attack Chain</option>
          <option value="credential_stuffing">Credential Stuffing</option>
          <option value="credential_compromise">Credential Compromise</option>
          <option value="targeted_attack">Targeted Attack</option>
        </select>
        <select
          value={filterStatus || ''}
          onChange={(e) => setFilterStatus(e.target.value || null)}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground"
        >
          <option value="">All status</option>
          <option value="open">Open</option>
          <option value="monitoring">Monitoring</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1 space-y-2">
          {groupsQuery.isError ? (
            <Card className="border-red-500/30 bg-red-500/5 p-4">
              <p className="text-sm text-red-400">Failed to load groups</p>
            </Card>
          ) : groups ? (
            groups.length === 0 ? (
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center justify-center py-8 text-sm text-muted-foreground">
                    <GitBranch className="mb-2 h-8 w-8" />
                    <p>No correlation groups found</p>
                    <p className="text-xs mt-1">Run correlation to detect event patterns</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              groups.map((group) => (
                <motion.button
                  key={group.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => setSelectedGroup(group.id)}
                  className={`w-full text-left rounded-lg border p-3 transition-all hover:border-[#00F5FF]/30 hover:bg-accent/30 ${
                    selectedGroup === group.id ? 'border-[#00F5FF]/50 bg-[#00F5FF]/5' : 'border-border/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${GROUP_TYPE_COLORS[group.group_type] || 'text-muted-foreground bg-muted'}`}>
                      {group.group_type.replace(/_/g, ' ')}
                    </span>
                    <Badge variant={group.status === 'open' ? 'critical' : 'default'} className="text-[10px] h-4 px-1">
                      {group.status}
                    </Badge>
                  </div>
                  {group.source_ip && (
                    <p className="text-xs font-mono text-foreground">{group.source_ip}</p>
                  )}
                  <div className="flex items-center gap-3 mt-1 text-[10px] text-muted-foreground">
                    <span>{group.event_count} events</span>
                    <span>Risk: {group.risk_score.toFixed(1)}</span>
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{timeAgo(group.start_time)}</span>
                  </div>
                  {group.description && (
                    <p className="text-[10px] text-muted-foreground truncate mt-1">{group.description}</p>
                  )}
                </motion.button>
              ))
            )
          ) : (
            Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full rounded-lg" />
            ))
          )}
        </div>

        <div className="lg:col-span-2 space-y-6">
          {selected && groupDetailQuery.data ? (
            <>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <GitBranch className="h-5 w-5" />
                        {selected.group_type.replace(/_/g, ' ')}
                        <Badge variant={selected.status === 'open' ? 'critical' : 'default'} className="text-[10px]">
                          {selected.status}
                        </Badge>
                      </CardTitle>
                      <CardDescription>{selected.description}</CardDescription>
                    </div>
                    <div className="text-right text-xs text-muted-foreground">
                      <div>Risk Score</div>
                      <div className={`text-lg font-bold ${selected.risk_score >= 7 ? 'text-red-400' : selected.risk_score >= 4 ? 'text-yellow-400' : 'text-emerald-400'}`}>
                        {selected.risk_score.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {selected.source_ip && (
                      <div>
                        <span className="text-muted-foreground">Source IP:</span>
                        <span className="ml-2 font-mono">{selected.source_ip}</span>
                      </div>
                    )}
                    {selected.destination_ip && (
                      <div>
                        <span className="text-muted-foreground">Destination IP:</span>
                        <span className="ml-2 font-mono">{selected.destination_ip}</span>
                      </div>
                    )}
                    {selected.username && (
                      <div>
                        <span className="text-muted-foreground">Username:</span>
                        <span className="ml-2 font-mono">{selected.username}</span>
                      </div>
                    )}
                    {selected.hostname && (
                      <div>
                        <span className="text-muted-foreground">Hostname:</span>
                        <span className="ml-2 font-mono">{selected.hostname}</span>
                      </div>
                    )}
                    <div>
                      <span className="text-muted-foreground">Time Window:</span>
                      <span className="ml-2 font-mono">{new Date(selected.start_time).toLocaleString()} → {new Date(selected.end_time).toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Event Count:</span>
                      <span className="ml-2 font-mono">{selected.event_count}</span>
                    </div>
                  </div>
                  {selected.attack_chain && selected.attack_chain.length > 0 && (
                    <div className="mt-3 flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Attack Chain:</span>
                      {selected.attack_chain.map((phase, i) => (
                        <span key={phase} className="flex items-center gap-1 text-xs">
                          <Badge variant="outline" className="text-[10px]">{phase.replace(/_/g, ' ')}</Badge>
                          {i < selected.attack_chain!.length - 1 && <span className="text-muted-foreground">→</span>}
                        </span>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <AttackTimeline
                chain={selected.events.map((e) => ({
                  phase: e.event_type,
                  events: [{
                    sequence: 1, timestamp: e.timestamp, event_id: e.id,
                    event_type: e.event_type, action: e.action,
                    source_ip: e.source_ip, destination_ip: e.destination_ip,
                    username: e.username, severity: e.severity,
                    risk_score: e.risk_score, raw_message: e.raw_message || '',
                    phase: e.event_type,
                  }],
                  count: 1,
                  max_severity: e.severity || 'info',
                }))}
              />

              <RelatedEvents events={selected.events} />
            </>
          ) : groupDetailQuery.isLoading ? (
            <div className="space-y-6">
              <Skeleton className="h-48 w-full rounded-lg" />
              <Skeleton className="h-64 w-full rounded-lg" />
            </div>
          ) : (
            <Card>
              <CardContent className="p-12">
                <div className="flex flex-col items-center justify-center text-sm text-muted-foreground">
                  <Shield className="mb-3 h-12 w-12" />
                  <p className="font-medium">Select a correlation group</p>
                  <p className="text-xs mt-1">Choose a group from the left panel to view details</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
