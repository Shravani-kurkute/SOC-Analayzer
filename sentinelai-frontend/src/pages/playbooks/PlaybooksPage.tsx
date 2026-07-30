import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  PlayCircle, Plus, RefreshCw, Search, ChevronDown, ChevronUp,
  Clock, Shield, CheckCircle, XCircle,
  FileText, Activity, Terminal,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { Tabs, TabsList, TabsTrigger } from '@components/ui/tabs'
import { StatCard } from '@components/common/StatCard'
import { soarService } from '@services/soarService'
import type { PlaybookListItem, PlaybookExecution, ApprovalRequest, TemplateDefinition } from '@typings/soar'
import toast from 'react-hot-toast'

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
}

const EXEC_STATUS_STYLES: Record<string, string> = {
  pending: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  running: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  completed: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  failed: 'text-red-400 bg-red-500/10 border-red-500/20',
  awaiting_approval: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
}

function timeAgo(ts: string | null): string {
  if (!ts) return '-'
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

function PlaybookTemplateCard({ template, onUse }: { template: TemplateDefinition; onUse: () => void }) {
  return (
    <div className="rounded-lg border border-border/50 bg-card/50 p-4 hover:border-[#00F5FF]/30 transition-colors cursor-pointer" onClick={onUse}>
      <div className="flex items-start justify-between mb-2">
        <div className="h-8 w-8 rounded-lg bg-[#00F5FF]/10 flex items-center justify-center">
          <Terminal className="h-4 w-4 text-[#00F5FF]" />
        </div>
        <Badge variant="outline" className="text-[10px]">{template.steps} steps</Badge>
      </div>
      <h3 className="text-sm font-semibold mb-1">{template.name}</h3>
      <p className="text-[11px] text-muted-foreground">{template.type.replace(/_/g, ' ')}</p>
    </div>
  )
}

export default function PlaybooksPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('playbooks')
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')

  const statsQuery = useQuery({
    queryKey: ['soar-stats'],
    queryFn: soarService.getStats,
    refetchInterval: 15000,
  })

  const listQuery = useQuery({
    queryKey: ['playbooks-list', page, search, filterType, sortBy, sortOrder],
    queryFn: () => soarService.getPlaybooks({ page, page_size: 20, search: search || undefined, playbook_type: filterType || undefined, sort_by: sortBy, sort_order: sortOrder }),
    refetchInterval: 30000,
  })

  const execsQuery = useQuery({
    queryKey: ['playbook-executions', page],
    queryFn: () => soarService.getExecutions({ page, page_size: 20 }),
    enabled: activeTab === 'executions',
    refetchInterval: 10000,
  })

  const templatesQuery = useQuery({
    queryKey: ['playbook-templates'],
    queryFn: soarService.getTemplates,
    enabled: activeTab === 'templates',
  })

  const approvalsQuery = useQuery({
    queryKey: ['playbook-approvals'],
    queryFn: () => soarService.getPendingApprovals({ page: 1, page_size: 20 }),
    enabled: activeTab === 'approvals',
    refetchInterval: 10000,
  })

  const instantiateMutation = useMutation({
    mutationFn: (params: { type: string; name?: string }) => soarService.instantiateTemplate(params.type, params.name),
    onSuccess: (data) => {
      toast.success('Playbook created from template')
      queryClient.invalidateQueries({ queryKey: ['playbooks-list'] })
      navigate(`/playbooks/${data.id}`)
    },
    onError: () => toast.error('Failed to create playbook'),
  })

  const executeMutation = useMutation({
    mutationFn: (id: string) => soarService.executePlaybook(id),
    onSuccess: (data) => {
      toast.success(`Execution ${data.status}`)
      queryClient.invalidateQueries({ queryKey: ['playbook-executions'] })
      queryClient.invalidateQueries({ queryKey: ['soar-stats'] })
      navigate(`/playbooks/executions/${data.execution_id}`)
    },
    onError: () => toast.error('Execution failed'),
  })

  const approveMutation = useMutation({
    mutationFn: (params: { id: string; approve: boolean }) => soarService.resolveApproval(params.id, params.approve),
    onSuccess: (_, vars) => {
      toast.success(vars.approve ? 'Approved' : 'Rejected')
      queryClient.invalidateQueries({ queryKey: ['playbook-approvals'] })
      queryClient.invalidateQueries({ queryKey: ['soar-stats'] })
    },
    onError: () => toast.error('Failed to resolve approval'),
  })

  const stats = statsQuery.data
  const data = listQuery.data?.data
  const execs = execsQuery.data?.data
  const templates = templatesQuery.data
  const approvals = approvalsQuery.data?.data

  const playbookTypes = [...new Set((data?.items || []).map(p => p.playbook_type))]

  return (
    <div className="space-y-6">
      <PageHeader
        title="SOAR Automation"
        description="Security Orchestration, Automation & Response"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => { listQuery.refetch(); statsQuery.refetch() }}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button size="sm" onClick={() => navigate('/playbooks/new')}>
              <Plus className="mr-2 h-4 w-4" /> Create Playbook
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard title="Playbooks" value={formatNumber(stats?.total_playbooks ?? 0)} icon={PlayCircle} variant="info" />
        <StatCard title="Executed Today" value={formatNumber(stats?.executions_today ?? 0)} icon={Activity} variant="info" />
        <StatCard title="Success Rate" value={stats ? `${stats.success_rate.toFixed(0)}%` : '0%'} icon={CheckCircle} variant="success" />
        <StatCard title="Avg Time" value={stats ? `${(stats.avg_execution_time_ms / 1000).toFixed(1)}s` : '0s'} icon={Clock} variant="default" />
        <StatCard title="Pending Approvals" value={formatNumber(stats?.pending_approvals ?? 0)} icon={Shield} variant={(stats?.pending_approvals ?? 0) > 0 ? 'warning' : 'default'} />
      </div>

      <Card>
        <CardHeader className="pb-0">
          <Tabs value={activeTab} onValueChange={(v) => { setActiveTab(v); setPage(1) }}>
            <TabsList className="grid grid-cols-4 w-[500px]">
              <TabsTrigger value="playbooks">Playbooks</TabsTrigger>
              <TabsTrigger value="templates">Templates</TabsTrigger>
              <TabsTrigger value="executions">Executions</TabsTrigger>
              <TabsTrigger value="approvals">Approvals</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardHeader>
      </Card>

      {activeTab === 'playbooks' && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Search playbooks..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }} className="pl-9 h-9 w-56" />
                </div>
                <select value={filterType} onChange={(e) => { setFilterType(e.target.value); setPage(1) }}
                  className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                  <option value="">All Types</option>
                  {playbookTypes.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
                  className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                  <option value="created_at">Created</option>
                  <option value="name">Name</option>
                  <option value="severity">Severity</option>
                  <option value="execution_count">Executions</option>
                </select>
                <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="h-9 px-2 rounded-lg border border-border bg-background hover:bg-accent">
                  {sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {listQuery.isLoading ? (
              <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}</div>
            ) : !data || data.items.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <PlayCircle className="h-12 w-12 mb-3 opacity-20" />
                <p className="text-sm font-medium">No playbooks defined</p>
                <p className="text-xs mt-1">Create a playbook or instantiate from a template.</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border text-left text-xs text-muted-foreground">
                        <th className="pb-2.5 font-medium pr-3">Name</th>
                        <th className="pb-2.5 font-medium pr-3">Type</th>
                        <th className="pb-2.5 font-medium pr-3">Severity</th>
                        <th className="pb-2.5 font-medium pr-3">Executions</th>
                        <th className="pb-2.5 font-medium pr-3">Success Rate</th>
                        <th className="pb-2.5 font-medium pr-3">Status</th>
                        <th className="pb-2.5 font-medium pr-3">Created</th>
                        <th className="pb-2.5 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.items.map((pb: PlaybookListItem) => (
                        <tr key={pb.id} className="border-b border-border/50 hover:bg-card/50 transition-colors cursor-pointer"
                          onClick={() => navigate(`/playbooks/${pb.id}`)}>
                          <td className="py-3 pr-3"><span className="font-medium text-sm">{pb.name}</span></td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{pb.playbook_type.replace(/_/g, ' ')}</td>
                          <td className="py-3 pr-3">
                            <Badge variant="outline" className={`text-[10px] h-4 px-1 ${SEVERITY_STYLES[pb.severity] || ''}`}>{pb.severity}</Badge>
                          </td>
                          <td className="py-3 pr-3 text-xs font-mono">{pb.execution_count}</td>
                          <td className="py-3 pr-3 text-xs font-mono">{pb.success_rate.toFixed(0)}%</td>
                          <td className="py-3 pr-3">
                            <Badge variant="outline" className={`text-[10px] h-4 px-1 ${pb.is_active ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-gray-400 bg-gray-500/10 border-gray-500/20'}`}>
                              {pb.is_active ? 'Active' : 'Disabled'}
                            </Badge>
                          </td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{timeAgo(pb.created_at)}</td>
                          <td className="py-3">
                            <div className="flex gap-1">
                              <Button variant="ghost" size="icon-sm" onClick={(e) => { e.stopPropagation(); executeMutation.mutate(pb.id) }}
                                title="Execute now"><PlayCircle className="h-4 w-4 text-emerald-400" /></Button>
                              <Button variant="ghost" size="icon-sm" onClick={(e) => { e.stopPropagation(); navigate(`/playbooks/${pb.id}`) }}
                                title="View"><FileText className="h-4 w-4" /></Button>
                            </div>
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
                      <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Previous</Button>
                      <Button variant="outline" size="sm" disabled={page >= data.total_pages} onClick={() => setPage(p => p + 1)}>Next</Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'templates' && (
        <Card>
          <CardContent className="p-6">
            {templatesQuery.isLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-28 w-full" />)}</div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {(templates || []).map((t: TemplateDefinition) => (
                  <PlaybookTemplateCard key={t.type} template={t} onUse={() => instantiateMutation.mutate({ type: t.type })} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'executions' && (
        <Card>
          <CardContent className="p-6">
            {execsQuery.isLoading ? (
              <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}</div>
            ) : !execs || execs.items.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <Activity className="h-12 w-12 mb-3 opacity-20" />
                <p className="text-sm font-medium">No executions yet</p>
                <p className="text-xs mt-1">Run a playbook to see execution history.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-muted-foreground">
                      <th className="pb-2.5 font-medium pr-3">Playbook</th>
                      <th className="pb-2.5 font-medium pr-3">Status</th>
                      <th className="pb-2.5 font-medium pr-3">Step</th>
                      <th className="pb-2.5 font-medium pr-3">Duration</th>
                      <th className="pb-2.5 font-medium pr-3">Triggered By</th>
                      <th className="pb-2.5 font-medium pr-3">Time</th>
                      <th className="pb-2.5 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {execs.items.map((ex: PlaybookExecution) => (
                      <tr key={ex.id} className="border-b border-border/50 hover:bg-card/50 transition-colors cursor-pointer"
                        onClick={() => navigate(`/playbooks/executions/${ex.id}`)}>
                        <td className="py-3 pr-3"><span className="font-medium text-sm">{ex.playbook_name}</span></td>
                        <td className="py-3 pr-3">
                          <Badge variant="outline" className={`text-[10px] h-4 px-1 ${EXEC_STATUS_STYLES[ex.status] || ''}`}>{ex.status}</Badge>
                        </td>
                        <td className="py-3 pr-3 text-xs text-muted-foreground">{ex.current_step}/{ex.total_steps}</td>
                        <td className="py-3 pr-3 text-xs font-mono">{ex.duration_ms ? `${(ex.duration_ms / 1000).toFixed(1)}s` : '-'}</td>
                        <td className="py-3 pr-3 text-xs text-muted-foreground">{ex.triggered_by || '-'}</td>
                        <td className="py-3 pr-3 text-xs text-muted-foreground">{timeAgo(ex.created_at)}</td>
                        <td className="py-3">
                          <Button variant="ghost" size="icon-sm" onClick={(e) => { e.stopPropagation(); navigate(`/playbooks/executions/${ex.id}`) }}>
                            <FileText className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'approvals' && (
        <Card>
          <CardContent className="p-6">
            {approvalsQuery.isLoading ? (
              <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 w-full" />)}</div>
            ) : !approvals || approvals.items.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <Shield className="h-12 w-12 mb-3 opacity-20" />
                <p className="text-sm font-medium">No pending approvals</p>
                <p className="text-xs mt-1">All approval requests have been resolved.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {approvals.items.map((req: ApprovalRequest) => (
                  <div key={req.id} className="flex items-center justify-between p-4 rounded-lg border border-border/50 bg-card/50">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{req.action_type.replace(/_/g, ' ')}</p>
                      <p className="text-xs text-muted-foreground">Step {req.step_index} · {req.requested_by || 'system'}</p>
                      {req.reason && <p className="text-xs text-muted-foreground mt-1">{req.reason}</p>}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <Button size="sm" variant="outline" className="text-emerald-400 border-emerald-500/20"
                        onClick={() => approveMutation.mutate({ id: req.id, approve: true })}>
                        <CheckCircle className="mr-1 h-3 w-3" /> Approve
                      </Button>
                      <Button size="sm" variant="outline" className="text-red-400 border-red-500/20"
                        onClick={() => approveMutation.mutate({ id: req.id, approve: false })}>
                        <XCircle className="mr-1 h-3 w-3" /> Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
