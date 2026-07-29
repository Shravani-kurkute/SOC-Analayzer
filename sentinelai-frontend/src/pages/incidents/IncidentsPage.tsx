import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Siren, Search, RefreshCw, Clock, MoreHorizontal,
  AlertTriangle, ChevronDown, ChevronUp,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { incidentService } from '@services/incidentService'
import type { IncidentListItem, IncidentFilter } from '@typings/incident'

const SEVERITY_BG: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  informational: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
}

const STATUS_BG: Record<string, string> = {
  new: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  assigned: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  investigating: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  contained: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  eradiated: 'text-red-400 bg-red-500/10 border-red-500/20',
  recovered: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  closed: 'text-gray-400 bg-gray-500/10 border-gray-500/20',
  false_positive: 'text-gray-400 bg-gray-500/10 border-gray-500/20',
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

export default function IncidentsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filterSeverity, setFilterSeverity] = useState<string>('')
  const [filterStatus, setFilterStatus] = useState<string>('')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')

  const filters: IncidentFilter = {}
  if (filterSeverity) filters.severity = filterSeverity
  if (filterStatus) filters.status = filterStatus
  if (search) filters.search = search
  filters.sort_by = sortBy
  filters.sort_order = sortOrder

  const listQuery = useQuery({
    queryKey: ['incidents-list', page, filterSeverity, filterStatus, search, sortBy, sortOrder],
    queryFn: () => incidentService.getIncidents({ ...filters, page, page_size: 20 }),
    refetchInterval: 30000,
  })

  const statsQuery = useQuery({
    queryKey: ['incidents-stats'],
    queryFn: incidentService.getStats,
    refetchInterval: 30000,
  })

  const data = listQuery.data?.data
  const stats = statsQuery.data

  return (
    <div className="space-y-6">
      <PageHeader
        title="Incident Response"
        description="Track, manage, and respond to security incidents"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => { listQuery.refetch(); statsQuery.refetch() }}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard title="Total Incidents" value={formatNumber(stats?.total_incidents ?? 0)} icon={Siren} variant="info" />
        <StatCard title="Open" value={formatNumber(stats?.open_incidents ?? 0)} icon={AlertTriangle} variant="warning" />
        <StatCard title="Critical" value={formatNumber(stats?.critical_incidents ?? 0)} icon={Siren} variant="danger" />
        <StatCard title="Closed" value={formatNumber(stats?.closed_incidents ?? 0)} icon={Siren} variant="success" />
        <StatCard title="Avg Resolution" value={stats?.avg_resolution_seconds ? formatDuration(stats.avg_resolution_seconds) : 'N/A'} icon={Clock} variant="default" />
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search incidents..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                  className="pl-9 h-9 w-64"
                />
              </div>
              <select
                value={filterSeverity}
                onChange={(e) => { setFilterSeverity(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              >
                <option value="">All Severity</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <select
                value={filterStatus}
                onChange={(e) => { setFilterStatus(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              >
                <option value="">All Status</option>
                <option value="new">New</option>
                <option value="assigned">Assigned</option>
                <option value="investigating">Investigating</option>
                <option value="contained">Contained</option>
                <option value="eradiated">Eradicated</option>
                <option value="recovered">Recovered</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              >
                <option value="created_at">Created</option>
                <option value="updated_at">Updated</option>
                <option value="severity">Severity</option>
                <option value="title">Title</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="h-9 px-2 rounded-lg border border-border bg-background hover:bg-accent transition-colors"
              >
                {sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {listQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : !data || data.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Siren className="h-12 w-12 mb-3 opacity-20" />
              <p className="text-sm font-medium">No incidents found</p>
              <p className="text-xs mt-1">All clear. Incidents will appear when alerts are correlated.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-muted-foreground">
                      <th className="pb-2.5 font-medium pr-3">Title</th>
                      <th className="pb-2.5 font-medium pr-3">Severity</th>
                      <th className="pb-2.5 font-medium pr-3">Status</th>
                      <th className="pb-2.5 font-medium pr-3">Assignee</th>
                      <th className="pb-2.5 font-medium pr-3">Alerts</th>
                      <th className="pb-2.5 font-medium pr-3">Tasks</th>
                      <th className="pb-2.5 font-medium pr-3">Created</th>
                      <th className="pb-2.5 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((inc: IncidentListItem) => (
                      <tr
                        key={inc.id}
                        className="border-b border-border/50 hover:bg-card/50 transition-colors cursor-pointer"
                        onClick={() => navigate(`/incidents/${inc.id}`)}
                      >
                        <td className="py-3 pr-3">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-foreground text-sm">{inc.title}</span>
                            {inc.category && <Badge variant="outline" className="text-[10px] h-4 px-1">{inc.category}</Badge>}
                          </div>
                        </td>
                        <td className="py-3 pr-3">
                          <Badge variant="outline" className={`text-[10px] h-4 px-1 ${SEVERITY_BG[inc.severity] || ''}`}>{inc.severity}</Badge>
                        </td>
                        <td className="py-3 pr-3">
                          <Badge variant="outline" className={`text-[10px] h-4 px-1 ${STATUS_BG[inc.status] || ''}`}>{inc.status}</Badge>
                        </td>
                        <td className="py-3 pr-3 text-xs text-muted-foreground">{inc.assignee_name || '-'}</td>
                        <td className="py-3 pr-3 text-xs font-mono text-muted-foreground">{inc.alert_count}</td>
                        <td className="py-3 pr-3 text-xs font-mono text-muted-foreground">{inc.task_done}/{inc.task_count}</td>
                        <td className="py-3 pr-3 text-xs text-muted-foreground">{timeAgo(inc.created_at)}</td>
                        <td className="py-3">
                          <Button variant="ghost" size="icon-sm" onClick={(e) => { e.stopPropagation(); navigate(`/incidents/${inc.id}`) }}>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {data.total_pages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <span className="text-xs text-muted-foreground">Page {page} of {data.total_pages}</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Previous</Button>
                    <Button variant="outline" size="sm" disabled={page >= data.total_pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
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

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`
}
