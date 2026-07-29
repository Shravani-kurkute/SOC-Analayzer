import { useState, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Siren, ArrowLeft, Clock, User, Activity, MessageSquare, Paperclip,
  CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp,
  Plus, Trash2, Edit3, Upload, ExternalLink, FileText,
  Brain, RefreshCw, Loader2, Check,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { incidentService } from '@services/incidentService'
import { aiService } from '@services/aiService'
import type { IncidentTimeline } from '@typings/incident'

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

function SectionCard({ title, icon: Icon, iconColor, children, defaultOpen = true, actions }: {
  title: string; icon: React.ElementType; iconColor?: string; children: React.ReactNode; defaultOpen?: boolean; actions?: React.ReactNode
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
          <div className="flex items-center gap-2">
            {actions}
            {open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
          </div>
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

function TimelineCard({ events }: { events: IncidentTimeline[] }) {
  if (!events || events.length === 0) return <p className="text-sm text-muted-foreground">No timeline entries</p>
  return (
    <div className="relative space-y-0">
      {events.map((ev, i) => (
        <div key={ev.id} className="flex gap-4 pb-4 last:pb-0">
          <div className="flex flex-col items-center">
            <div className="h-2.5 w-2.5 rounded-full bg-[#00F5FF] mt-1.5" />
            {i < events.length - 1 && <div className="w-px flex-1 bg-border" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{timeAgo(ev.created_at)}</span>
              <Badge variant="outline" className="text-[10px] h-4 px-1">{ev.action}</Badge>
            </div>
            <p className="text-sm font-medium text-foreground mt-0.5">{ev.actor}</p>
            {ev.details && <p className="text-xs text-muted-foreground mt-0.5">{ev.details}</p>}
          </div>
        </div>
      ))}
    </div>
  )
}

function MarkdownContent({ content }: { content: string }) {
  if (!content) return <p className="text-sm text-muted-foreground">No content</p>
  return (
    <div className="prose prose-invert max-w-none prose-headings:text-foreground prose-p:text-muted-foreground prose-strong:text-foreground prose-code:text-[#00F5FF] prose-code:bg-secondary/50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-pre:bg-secondary/50 prose-pre:border prose-pre:border-border prose-a:text-[#00F5FF] prose-ul:text-muted-foreground prose-ol:text-muted-foreground prose-li:text-muted-foreground prose-hr:border-border">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}

export default function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [newComment, setNewComment] = useState('')
  const [editingComment, setEditingComment] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [newTask, setNewTask] = useState('')
  const [newTaskPriority, setNewTaskPriority] = useState('medium')
  const [newTaskAssignee, setNewTaskAssignee] = useState('')
  const [newTaskDue, setNewTaskDue] = useState('')
  const [closeResolution, setCloseResolution] = useState('')
  const [closeNotes, setCloseNotes] = useState('')
  const [showClose, setShowClose] = useState(false)
  const [assignUserId, setAssignUserId] = useState('')
  const [assignMode, setAssignMode] = useState(false)
  const [aiReport, setAiReport] = useState<any>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const incidentQuery = useQuery({
    queryKey: ['incident', id],
    queryFn: () => incidentService.getIncident(id!),
    enabled: !!id,
    refetchInterval: 15000,
  })

  const incident = incidentQuery.data

  const commentMutation = useMutation({
    mutationFn: (content: string) => incidentService.addComment(id!, content),
    onSuccess: () => { setNewComment(''); incidentQuery.refetch() },
  })

  const editCommentMutation = useMutation({
    mutationFn: ({ commentId, content }: { commentId: string; content: string }) =>
      incidentService.editComment(id!, commentId, content),
    onSuccess: () => { setEditingComment(null); setEditContent(''); incidentQuery.refetch() },
  })

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId: string) => incidentService.deleteComment(id!, commentId),
    onSuccess: () => incidentQuery.refetch(),
  })

  const taskMutation = useMutation({
    mutationFn: () => incidentService.createTask(id!, {
      title: newTask, priority: newTaskPriority,
      assignee_id: newTaskAssignee || undefined,
      due_date: newTaskDue || undefined,
    }),
    onSuccess: () => { setNewTask(''); setNewTaskPriority('medium'); setNewTaskAssignee(''); setNewTaskDue(''); incidentQuery.refetch() },
  })

  const taskUpdateMutation = useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: any }) =>
      incidentService.updateTask(id!, taskId, data),
    onSuccess: () => incidentQuery.refetch(),
  })

  const assignMutation = useMutation({
    mutationFn: () => incidentService.assignIncident(id!, assignUserId),
    onSuccess: () => { setAssignMode(false); setAssignUserId(''); incidentQuery.refetch() },
  })

  const closeMutation = useMutation({
    mutationFn: () => incidentService.closeIncident(id!, closeResolution, closeNotes),
    onSuccess: () => { setShowClose(false); setCloseResolution(''); setCloseNotes(''); incidentQuery.refetch() },
  })

  const handleAiInvestigate = async () => {
    if (!id) return
    setAiLoading(true)
    try {
      const report = await aiService.getReport(id)
      if (report) {
        setAiReport(report)
      } else {
        const result = await aiService.investigate(id)
        setAiReport(result)
      }
    } catch {
      try {
        const result = await aiService.investigate(id)
        setAiReport(result)
      } catch (err) {
        console.error('AI investigation failed', err)
      }
    } finally {
      setAiLoading(false)
    }
  }

  const handleEvidenceUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !id) return
    try {
      await incidentService.uploadEvidence(id, file)
      incidentQuery.refetch()
    } catch (err) {
      console.error('Upload failed', err)
    }
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleStatusChange = async (status: string) => {
    if (!id) return
    try {
      await incidentService.updateIncident(id, { status })
      incidentQuery.refetch()
    } catch (err) {
      console.error('Status update failed', err)
    }
  }

  if (!id) return null

  if (incidentQuery.isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (!incident) {
    return (
      <div className="p-6">
        <Button variant="ghost" size="sm" onClick={() => navigate('/incidents')}><ArrowLeft className="mr-2 h-4 w-4" /> Back</Button>
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
          <Siren className="h-16 w-16 mb-4 opacity-20" />
          <p className="text-lg font-medium">Incident not found</p>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/incidents')}>Go to Incidents</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate('/incidents')}><ArrowLeft className="mr-1 h-4 w-4" /> Back</Button>
        <PageHeader
          title={incident.title}
          description={`ID: ${incident.id.slice(0, 8)}`}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <span className="text-xs text-muted-foreground">Severity</span>
            <div className="mt-1">
              <select
                value={incident.severity}
                onChange={(e) => incidentService.updateIncident(id, { severity: e.target.value }).then(() => incidentQuery.refetch())}
                className="h-8 rounded border border-border bg-background px-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <span className="text-xs text-muted-foreground">Status</span>
            <div className="mt-1">
              <select
                value={incident.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="h-8 rounded border border-border bg-background px-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              >
                <option value="new">New</option>
                <option value="assigned">Assigned</option>
                <option value="investigating">Investigating</option>
                <option value="contained">Contained</option>
                <option value="eradiated">Eradicated</option>
                <option value="recovered">Recovered</option>
                <option value="closed">Closed</option>
                <option value="false_positive">False Positive</option>
              </select>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <span className="text-xs text-muted-foreground">Assignee</span>
            <div className="mt-1">
              {assignMode ? (
                <div className="flex gap-1">
                  <input
                    placeholder="User ID..."
                    value={assignUserId}
                    onChange={(e) => setAssignUserId(e.target.value)}
                    className="h-8 flex-1 rounded border border-border bg-background px-2 text-xs focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
                  />
                  <Button size="icon-sm" variant="accent" disabled={!assignUserId} onClick={() => assignMutation.mutate()}>
                    <Check className="h-3 w-3" />
                  </Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setAssignMode(false)}>
                    <XCircle className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{incident.assignee_name || 'Unassigned'}</span>
                  <Button variant="ghost" size="icon-sm" onClick={() => setAssignMode(true)}>
                    <User className="h-3.5 w-3.5" />
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <span className="text-xs text-muted-foreground">Created</span>
            <p className="text-sm font-medium mt-1">{timeAgo(incident.created_at)}</p>
            <span className="text-xs text-muted-foreground">{incident.created_by ? `by ${incident.created_by}` : ''}</span>
          </CardContent>
        </Card>
      </div>

      <div className="flex gap-2">
        {incident.status !== 'closed' && incident.status !== 'false_positive' && (
          <Button size="sm" onClick={() => setShowClose(true)}>
            <CheckCircle className="mr-2 h-4 w-4" /> Close Incident
          </Button>
        )}
        <Button size="sm" variant="accent" onClick={handleAiInvestigate} disabled={aiLoading}>
          {aiLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Brain className="mr-2 h-4 w-4" />}
          AI Investigate
        </Button>
      </div>

      <AnimatePresence>
        {showClose && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Card className="border-yellow-500/30">
              <CardContent className="p-4 space-y-3">
                <Input placeholder="Resolution (e.g. 'False positive', 'Contained')" value={closeResolution} onChange={(e) => setCloseResolution(e.target.value)} />
                <Input placeholder="Closing notes" value={closeNotes} onChange={(e) => setCloseNotes(e.target.value)} />
                <div className="flex gap-2">
                  <Button size="sm" variant="accent" onClick={() => closeMutation.mutate()} disabled={closeMutation.isPending}>
                    <CheckCircle className="mr-2 h-4 w-4" /> Confirm Close
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setShowClose(false)}>Cancel</Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="space-y-4">
        <SectionCard title="Description" icon={FileText} iconColor="#00F5FF">
          <MarkdownContent content={incident.description || 'No description'} />
        </SectionCard>

        <SectionCard title="Activity Timeline" icon={Activity} iconColor="#00F5FF">
          <TimelineCard events={incident.timeline || []} />
        </SectionCard>

        <SectionCard title="AI Investigation" icon={Brain} iconColor="#A78BFA" actions={
          <Button variant="ghost" size="icon-sm" onClick={handleAiInvestigate} disabled={aiLoading}>
            <RefreshCw className={`h-3.5 w-3.5 ${aiLoading ? 'animate-spin' : ''}`} />
          </Button>
        }>
          {aiLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-[#00F5FF]" />
              <span className="ml-2 text-sm text-muted-foreground">Generating AI investigation...</span>
            </div>
          ) : aiReport ? (
            <div className="space-y-4">
              {aiReport.summary && (
                <div>
                  <h4 className="text-sm font-medium text-foreground mb-1">Summary</h4>
                  <MarkdownContent content={aiReport.summary} />
                </div>
              )}
              {aiReport.confidence_score != null && (
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>Confidence: <span className="text-emerald-400 font-medium">{(aiReport.confidence_score * 100).toFixed(0)}%</span></span>
                  <span>False Positive: <span className="text-yellow-400 font-medium">{aiReport.false_positive_probability != null ? `${(aiReport.false_positive_probability * 100).toFixed(0)}%` : 'N/A'}</span></span>
                  <span>Provider: <span className="font-mono">{aiReport.provider}</span></span>
                </div>
              )}
              <Button variant="outline" size="sm" onClick={() => navigate('/ai')}>
                <ExternalLink className="mr-2 h-4 w-4" /> Full AI Report
              </Button>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Click the AI Investigate button above to generate a report.</p>
          )}
        </SectionCard>

        <SectionCard title="Related Alerts" icon={AlertTriangle} iconColor="#F87171">
          {incident.alert_ids && incident.alert_ids.length > 0 ? (
            <div className="space-y-2">
              {incident.alert_ids.map((aid) => (
                <div key={aid} className="flex items-center gap-2 rounded-lg border border-border/50 p-2.5">
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-mono flex-1">{aid}</span>
                  <Button variant="ghost" size="icon-sm" onClick={() => navigate(`/alerts/${aid}`)}>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No alerts linked to this incident</p>
          )}
        </SectionCard>

        <SectionCard title="Tasks" icon={CheckCircle} iconColor="#34D399">
          <div className="space-y-3">
            {(incident.tasks || []).length === 0 ? (
              <p className="text-sm text-muted-foreground">No tasks created</p>
            ) : (
              <div className="space-y-2">
                {incident.tasks.map((task) => (
                  <div key={task.id} className="flex items-start gap-3 rounded-lg border border-border/50 p-3">
                    <button
                      onClick={() => taskUpdateMutation.mutate({
                        taskId: task.id,
                        data: { status: task.status === 'completed' ? 'pending' : 'completed' }
                      })}
                      className="mt-0.5"
                    >
                      {task.status === 'completed' ? (
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <XCircle className="h-4 w-4 text-muted-foreground" />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${task.status === 'completed' ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                          {task.title}
                        </span>
                        <Badge variant="outline" className="text-[10px] h-4 px-1">{task.priority}</Badge>
                        <Badge variant="outline" className="text-[10px] h-4 px-1">{task.status}</Badge>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                        {task.assignee_name && <span>{task.assignee_name}</span>}
                        {task.due_date && <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                      </div>
                    </div>
                    <select
                      value={task.status}
                      onChange={(e) => taskUpdateMutation.mutate({ taskId: task.id, data: { status: e.target.value } })}
                      className="h-7 rounded border border-border bg-background px-1 text-xs"
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                ))}
              </div>
            )}
            <div className="flex gap-2 pt-2">
              <input
                placeholder="New task..."
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && newTask && taskMutation.mutate()}
                className="flex-1 h-9 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
              />
              <select value={newTaskPriority} onChange={(e) => setNewTaskPriority(e.target.value)} className="h-9 rounded border border-border bg-background px-2 text-xs">
                <option value="low">Low</option>
                <option value="medium">Med</option>
                <option value="high">High</option>
                <option value="critical">Crit</option>
              </select>
              <Button size="sm" disabled={!newTask} onClick={() => taskMutation.mutate()}>
                <Plus className="mr-1 h-4 w-4" /> Add
              </Button>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Comments" icon={MessageSquare} iconColor="#00F5FF">
          <div className="space-y-4">
            {(incident.comments || []).length === 0 ? (
              <p className="text-sm text-muted-foreground">No comments yet</p>
            ) : (
              <div className="space-y-3">
                {incident.comments.map((comment) => (
                  <div key={comment.id} className="rounded-lg border border-border/50 p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="h-6 w-6 rounded-full bg-[#00F5FF]/10 flex items-center justify-center">
                          <span className="text-xs font-medium text-[#00F5FF]">{comment.author_name.charAt(0).toUpperCase()}</span>
                        </div>
                        <span className="text-sm font-medium text-foreground">{comment.author_name}</span>
                        <span className="text-xs text-muted-foreground">{timeAgo(comment.created_at)}</span>
                        {comment.is_edited && <Badge variant="outline" className="text-[10px] h-4 px-1">edited</Badge>}
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon-sm" onClick={() => { setEditingComment(comment.id); setEditContent(comment.content) }}>
                          <Edit3 className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="icon-sm" onClick={() => deleteCommentMutation.mutate(comment.id)}>
                          <Trash2 className="h-3.5 w-3.5 text-red-400" />
                        </Button>
                      </div>
                    </div>
                    {editingComment === comment.id ? (
                      <div className="space-y-2">
                        <textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          className="w-full h-20 rounded-lg border border-border bg-background p-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50"
                        />
                        <div className="flex gap-2">
                          <Button size="sm" variant="accent" onClick={() => editCommentMutation.mutate({ commentId: comment.id, content: editContent })}>
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setEditingComment(null)}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <MarkdownContent content={comment.content} />
                    )}
                  </div>
                ))}
              </div>
            )}
            <div className="flex gap-2 pt-2">
              <textarea
                placeholder="Add a comment (Markdown supported)..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="flex-1 h-20 rounded-lg border border-border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50 resize-none"
              />
            </div>
            <div className="flex justify-end">
              <Button size="sm" variant="accent" disabled={!newComment.trim()} onClick={() => commentMutation.mutate(newComment)}>
                <MessageSquare className="mr-2 h-4 w-4" /> Post Comment
              </Button>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Evidence" icon={Paperclip} iconColor="#FBBF24" actions={
          <Button variant="ghost" size="icon-sm" onClick={() => fileInputRef.current?.click()}>
            <Upload className="h-3.5 w-3.5" />
          </Button>
        }>
          <input ref={fileInputRef} type="file" className="hidden" onChange={handleEvidenceUpload} />
          {(incident.evidence || []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No evidence uploaded</p>
          ) : (
            <div className="space-y-2">
              {incident.evidence.map((ev) => (
                <div key={ev.id} className="flex items-center gap-3 rounded-lg border border-border/50 p-3">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground truncate">{ev.filename}</span>
                      <Badge variant="outline" className="text-[10px] h-4 px-1">{ev.file_type}</Badge>
                    </div>
                    <div className="flex items-center gap-3 mt-0.5 text-xs text-muted-foreground">
                      <span>{(ev.file_size / 1024).toFixed(1)} KB</span>
                      <span>SHA256: {ev.sha256.slice(0, 16)}...</span>
                      <span>by {ev.uploaded_by}</span>
                      <span>{timeAgo(ev.created_at)}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon-sm" onClick={() => incidentService.deleteEvidence(id, ev.id).then(() => incidentQuery.refetch())}>
                    <Trash2 className="h-3.5 w-3.5 text-red-400" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  )
}
