import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import {
  PlayCircle, ArrowLeft, Edit3, Trash2, RefreshCw,
  Clock, CheckCircle, XCircle, AlertTriangle,
  Terminal, Shield, Play,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Skeleton } from '@components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@components/ui/tabs'
import { soarService } from '@services/soarService'
import type { PlaybookExecution } from '@typings/soar'
import toast from 'react-hot-toast'

const SEVERITY_STYLES: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
}



function timeAgo(ts: string | null): string {
  if (!ts) return '-'
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return new Date(ts).toLocaleDateString()
}

export default function PlaybookDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('overview')

  const pbQuery = useQuery({
    queryKey: ['playbook', id],
    queryFn: () => soarService.getPlaybook(id!),
    enabled: !!id,
    refetchInterval: 15000,
  })

  const execsQuery = useQuery({
    queryKey: ['playbook-execs', id],
    queryFn: () => soarService.getExecutions({ playbook_id: id, page_size: 20 }),
    enabled: activeTab === 'executions',
    refetchInterval: 10000,
  })

  const executeMutation = useMutation({
    mutationFn: () => soarService.executePlaybook(id!),
    onSuccess: (data) => {
      toast.success(`Execution started: ${data.status}`)
      queryClient.invalidateQueries({ queryKey: ['playbook-execs', id] })
      navigate(`/playbooks/executions/${data.execution_id}`)
    },
    onError: () => toast.error('Execution failed'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => soarService.deletePlaybook(id!),
    onSuccess: () => {
      toast.success('Playbook deleted')
      navigate('/playbooks')
    },
    onError: () => toast.error('Failed to delete'),
  })

  const pb = pbQuery.data
  const execs = execsQuery.data?.data

  if (pbQuery.isLoading) {
    return <div className="space-y-6"><Skeleton className="h-8 w-64" /><Skeleton className="h-48 w-full" /></div>
  }

  if (!pb) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <PlayCircle className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-20" />
          <h2 className="text-xl font-bold">Playbook Not Found</h2>
          <p className="text-sm text-muted-foreground mt-2">The playbook you're looking for doesn't exist.</p>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/playbooks')}><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={pb.name}
        description={`${pb.playbook_type.replace(/_/g, ' ')} · ${(pb.steps || []).length} steps`}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => pbQuery.refetch()}><RefreshCw className="mr-2 h-4 w-4" /> Refresh</Button>
            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700" onClick={() => executeMutation.mutate()}
              disabled={executeMutation.isPending}>
              <Play className="mr-2 h-4 w-4" /> Execute
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate(`/playbooks/${id}/edit`)}><Edit3 className="mr-2 h-4 w-4" /> Edit</Button>
            <Button variant="outline" size="sm" className="text-red-400" onClick={() => deleteMutation.mutate()}><Trash2 className="mr-2 h-4 w-4" /> Delete</Button>
            <Button variant="outline" size="sm" onClick={() => navigate('/playbooks')}><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col items-center text-center mb-4">
                <div className="h-14 w-14 rounded-xl bg-[#00F5FF]/10 flex items-center justify-center mb-3">
                  <Terminal className="h-7 w-7 text-[#00F5FF]" />
                </div>
                <h2 className="text-lg font-bold">{pb.name}</h2>
                <p className="text-xs text-muted-foreground">{pb.playbook_type.replace(/_/g, ' ')}</p>
                <div className="flex gap-2 mt-2">
                  <Badge variant="outline" className={`text-[10px] ${SEVERITY_STYLES[pb.severity] || ''}`}>{pb.severity}</Badge>
                  <Badge variant="outline" className={`text-[10px] ${pb.is_active ? 'text-emerald-400 bg-emerald-500/10' : 'text-gray-400 bg-gray-500/10'}`}>
                    {pb.is_active ? 'Active' : 'Disabled'}
                  </Badge>
                </div>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between"><span className="text-muted-foreground">Executions</span><span className="font-mono">{pb.execution_count}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Success Rate</span><span className="font-mono">{pb.success_rate.toFixed(0)}%</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Avg Time</span><span className="font-mono">{(pb.avg_execution_time / 1000).toFixed(1)}s</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Steps</span><span className="font-mono">{(pb.steps || []).length}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Category</span><span>{pb.category || '-'}</span></div>
              </div>
              {pb.description && (
                <div className="mt-4 pt-4 border-t border-border/50">
                  <p className="text-xs text-muted-foreground">{pb.description}</p>
                </div>
              )}
              {pb.tags && pb.tags.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border/50">
                  <div className="flex flex-wrap gap-1">
                    {pb.tags.map((tag, i) => <Badge key={i} variant="secondary" className="text-[10px]">{tag}</Badge>)}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-3 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid grid-cols-3 w-[400px]">
              <TabsTrigger value="overview">Steps</TabsTrigger>
              <TabsTrigger value="executions">Executions</TabsTrigger>
              <TabsTrigger value="designer">Designer</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6 space-y-4">
              {(pb.steps || []).length === 0 ? (
                <Card><CardContent className="p-6 text-center text-sm text-muted-foreground">No steps defined</CardContent></Card>
              ) : (
                (pb.steps || []).map((step, i) => (
                  <div key={i} className="relative">
                    {i > 0 && <div className="absolute left-5 top-0 bottom-1/2 w-px bg-border" />}
                    <div className="flex items-start gap-4 p-4 rounded-lg border border-border/50 bg-card/50">
                      <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
                        step.type === 'action' ? 'bg-[#00F5FF]/10 text-[#00F5FF]' :
                        step.type === 'condition' ? 'bg-yellow-500/10 text-yellow-400' :
                        step.type === 'delay' ? 'bg-purple-500/10 text-purple-400' :
                        step.type === 'approval' ? 'bg-orange-500/10 text-orange-400' :
                        'bg-gray-500/10 text-gray-400'
                      }`}>
                        {step.type === 'action' ? <Play className="h-4 w-4" /> :
                         step.type === 'condition' ? <AlertTriangle className="h-4 w-4" /> :
                         step.type === 'delay' ? <Clock className="h-4 w-4" /> :
                         <Shield className="h-4 w-4" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{step.name}</span>
                          <Badge variant="outline" className="text-[10px]">{step.action}</Badge>
                          <Badge variant="outline" className="text-[10px]">{step.type}</Badge>
                        </div>
                        {step.config && Object.keys(step.config).length > 0 && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {Object.entries(step.config).map(([k, v]) => `${k}: ${v}`).join(', ')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </TabsContent>

            <TabsContent value="executions" className="mt-6">
              {!execs || execs.items.length === 0 ? (
                <Card><CardContent className="p-6 text-center text-sm text-muted-foreground">No executions yet</CardContent></Card>
              ) : (
                <div className="space-y-3">
                  {execs.items.map((ex: PlaybookExecution) => (
                    <div key={ex.id} className="flex items-center justify-between p-4 rounded-lg border border-border/50 bg-card/50 cursor-pointer hover:bg-card transition-colors"
                      onClick={() => navigate(`/playbooks/executions/${ex.id}`)}>
                      <div className="flex items-center gap-3">
                        <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${
                          ex.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' :
                          ex.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                          ex.status === 'running' ? 'bg-blue-500/10 text-blue-400' :
                          'bg-yellow-500/10 text-yellow-400'
                        }`}>
                          {ex.status === 'completed' ? <CheckCircle className="h-4 w-4" /> :
                           ex.status === 'failed' ? <XCircle className="h-4 w-4" /> :
                           <Clock className="h-4 w-4" />}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{ex.status} · {ex.current_step}/{ex.total_steps} steps</p>
                          <p className="text-xs text-muted-foreground">
                            {ex.duration_ms ? `${(ex.duration_ms / 1000).toFixed(1)}s · ` : ''}
                            {ex.triggered_by || 'auto'} · {timeAgo(ex.created_at)}
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-[10px]">{ex.status}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="designer" className="mt-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                    <Terminal className="h-12 w-12 mb-3 opacity-20" />
                    <p className="text-sm font-medium">Drag & Drop Designer</p>
                    <p className="text-xs mt-1">Use the visual workflow editor to modify steps.</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {['action', 'condition', 'delay', 'approval', 'loop'].map(type => (
                        <Badge key={type} variant="outline" className="text-[10px] px-3 py-1">{type}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
