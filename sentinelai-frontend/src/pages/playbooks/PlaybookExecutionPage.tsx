import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, RefreshCw,
  Activity, Play, FileText, Brain,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Skeleton } from '@components/ui/skeleton'
import { Progress } from '@components/ui/progress'
import { soarService } from '@services/soarService'
import type { PlaybookExecutionLog } from '@typings/soar'
import toast from 'react-hot-toast'

const EXEC_STATUS_STYLES: Record<string, string> = {
  pending: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  running: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  completed: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  failed: 'text-red-400 bg-red-500/10 border-red-500/20',
  awaiting_approval: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
}

const LOG_STATUS_STYLES: Record<string, string> = {
  completed: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  failed: 'text-red-400 bg-red-500/10 border-red-500/20',
  running: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  pending: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
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

export default function PlaybookExecutionPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const execQuery = useQuery({
    queryKey: ['playbook-execution', id],
    queryFn: () => soarService.getExecution(id!),
    enabled: !!id,
    refetchInterval: 5000,
  })

  const logsQuery = useQuery({
    queryKey: ['playbook-execution-logs', id],
    queryFn: () => soarService.getExecutionLogs(id!),
    enabled: !!id,
    refetchInterval: 5000,
  })

  const retryMutation = useMutation({
    mutationFn: () => {
      const ex = execQuery.data
      return soarService.retryPlaybook(ex!.playbook_id, ex!.incident_id || undefined)
    },
    onSuccess: (data) => {
      toast.success('Retrying...')
      navigate(`/playbooks/executions/${data.execution_id}`)
    },
    onError: () => toast.error('Retry failed'),
  })

  const ex = execQuery.data
  const logs = logsQuery.data

  if (execQuery.isLoading) {
    return <div className="space-y-6"><Skeleton className="h-8 w-64" /><Skeleton className="h-48 w-full" /></div>
  }

  if (!ex) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <Activity className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-20" />
          <h2 className="text-xl font-bold">Execution Not Found</h2>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/playbooks')}><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
        </div>
      </div>
    )
  }

  const progress = ex.total_steps > 0 ? Math.round((ex.current_step / ex.total_steps) * 100) : 0
  const isRunning = ex.status === 'running'

  return (
    <div className="space-y-6">
      <PageHeader
        title={ex.playbook_name}
        description={`Execution ${ex.id.slice(0, 8)}...`}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => { execQuery.refetch(); logsQuery.refetch() }}
              disabled={isRunning}>
              <RefreshCw className={`mr-2 h-4 w-4 ${isRunning ? 'animate-spin' : ''}`} /> Refresh
            </Button>
            {ex.status === 'failed' && (
              <Button size="sm" onClick={() => retryMutation.mutate()} disabled={retryMutation.isPending}>
                <Play className="mr-2 h-4 w-4" /> Retry
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={() => navigate(`/playbooks/${ex.playbook_id}`)}>
              <FileText className="mr-2 h-4 w-4" /> Playbook
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate('/playbooks')}><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="text-center">
                <Badge variant="outline" className={`text-xs px-3 py-1 ${EXEC_STATUS_STYLES[ex.status] || ''}`}>
                  {ex.status.replace(/_/g, ' ')}
                </Badge>
              </div>
              <Progress value={progress} className={`h-2 ${ex.status === 'completed' ? 'bg-emerald-500' : ex.status === 'failed' ? 'bg-red-500' : 'bg-[#00F5FF]'}`} />
              <div className="space-y-2 text-xs">
                <div className="flex justify-between"><span className="text-muted-foreground">Progress</span><span className="font-mono">{ex.current_step}/{ex.total_steps} steps</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Duration</span><span className="font-mono">{ex.duration_ms ? `${(ex.duration_ms / 1000).toFixed(1)}s` : 'Running...'}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Triggered By</span><span className="font-mono">{ex.triggered_by || '-'}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Started</span><span className="font-mono">{timeAgo(ex.started_at)}</span></div>
                {ex.completed_at && <div className="flex justify-between"><span className="text-muted-foreground">Completed</span><span className="font-mono">{timeAgo(ex.completed_at)}</span></div>}
              </div>
              {ex.error_message && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                  <p className="text-xs font-medium text-red-400">Error</p>
                  <p className="text-xs text-red-300 mt-1">{ex.error_message}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {ex.ai_summary && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Brain className="h-4 w-4 text-[#00F5FF]" /> AI Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">{ex.ai_summary}</p>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="lg:col-span-3 space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Activity className="h-4 w-4 text-[#00F5FF]" /> Execution Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              {logsQuery.isLoading ? (
                <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}</div>
              ) : !logs || logs.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No logs yet</p>
              ) : (
                <div className="space-y-2">
                  {logs.map((log: PlaybookExecutionLog, i: number) => (
                    <div key={log.id} className="relative pl-8">
                      {i < logs.length - 1 && <div className="absolute left-[15px] top-6 bottom-0 w-px bg-border" />}
                      <div className={`absolute left-2.5 top-1.5 h-[7px] w-[7px] rounded-full ${
                        log.status === 'completed' ? 'bg-emerald-500' :
                        log.status === 'failed' ? 'bg-red-500' :
                        'bg-yellow-500'
                      }`} />
                      <div className="p-3 rounded-lg border border-border/50 bg-card/50">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium">{log.step_name}</span>
                            <Badge variant="outline" className={`text-[9px] h-3.5 px-1 ${LOG_STATUS_STYLES[log.status] || ''}`}>{log.status}</Badge>
                          </div>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            {log.duration_ms ? `${log.duration_ms}ms` : ''}
                          </span>
                        </div>
                        {log.message && <p className="text-xs text-muted-foreground">{log.message}</p>}
                        {log.error && <p className="text-xs text-red-400 mt-1">{log.error}</p>}
                        {log.output_data && log.output_data.success !== undefined && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {log.output_data.success ? 'Success' : 'Failed'}:
                            {' '}{log.output_data.message || log.output_data.action || JSON.stringify(log.output_data).slice(0, 100)}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <FileText className="h-4 w-4 text-[#00F5FF]" /> Execution Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                  <p className="text-xs text-muted-foreground">ID</p>
                  <p className="text-xs font-mono mt-1">{ex.id}</p>
                </div>
                <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                  <p className="text-xs text-muted-foreground">Playbook</p>
                  <p className="text-xs font-medium mt-1">{ex.playbook_name}</p>
                </div>
                <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                  <p className="text-xs text-muted-foreground">Incident</p>
                  <p className="text-xs font-mono mt-1">{ex.incident_id ? `${ex.incident_id.slice(0, 8)}...` : 'N/A'}</p>
                </div>
                <div className="p-3 rounded-lg bg-card/50 border border-border/50">
                  <p className="text-xs text-muted-foreground">Status</p>
                  <p className="text-xs font-medium mt-1 capitalize">{ex.status.replace(/_/g, ' ')}</p>
                </div>
              </div>
              {ex.execution_data && Object.keys(ex.execution_data).length > 0 && (
                <div className="mt-4 p-3 rounded-lg bg-card/50 border border-border/50">
                  <p className="text-xs text-muted-foreground mb-2">Context Data</p>
                  <pre className="text-[10px] text-muted-foreground font-mono whitespace-pre-wrap">
                    {JSON.stringify(ex.execution_data, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
