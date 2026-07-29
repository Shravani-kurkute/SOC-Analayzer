import { useState, useEffect, useRef } from 'react'
import { useWebSocket } from '@contexts/WebSocketContext'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import { Clock, Siren, AlertTriangle, CheckCircle, Brain, FileText, Shield, Activity } from 'lucide-react'
import type { LiveActivityEvent } from '@typings/notification'

const EVENT_ICONS: Record<string, typeof Siren> = {
  new_alert: Siren,
  new_incident: AlertTriangle,
  incident_assigned: Activity,
  incident_closed: CheckCircle,
  severity_changed: AlertTriangle,
  ai_investigation: Brain,
  ioc_created: Shield,
  threat_match: Shield,
  report_generated: FileText,
  log_uploaded: Activity,
  correlation_finished: Activity,
}

const EVENT_COLORS: Record<string, string> = {
  new_alert: 'text-red-400 bg-red-500/10',
  new_incident: 'text-orange-400 bg-orange-500/10',
  incident_assigned: 'text-blue-400 bg-blue-500/10',
  incident_closed: 'text-emerald-400 bg-emerald-500/10',
  severity_changed: 'text-yellow-400 bg-yellow-500/10',
  ai_investigation: 'text-purple-400 bg-purple-500/10',
  ioc_created: 'text-cyan-400 bg-cyan-500/10',
  threat_match: 'text-red-400 bg-red-500/10',
  report_generated: 'text-[#00F5FF] bg-[#00F5FF]/10',
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return new Date(ts).toLocaleDateString()
}

export function LiveActivityFeed() {
  const { lastEvent } = useWebSocket()
  const [events, setEvents] = useState<(LiveActivityEvent & { _ts: string })[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (lastEvent) {
      setEvents(prev => [{
        ...lastEvent,
        _ts: new Date().toISOString(),
      }, ...prev].slice(0, 100))
    }
  }, [lastEvent])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }, [events.length])

  const getEventText = (ev: LiveActivityEvent): string => {
    if (ev.type === 'notification' && ev.notification) {
      return ev.notification.title
    }
    if (ev.data?.message) return String(ev.data.message)
    return ev.event.replace(/_/g, ' ')
  }

  return (
    <Card className="border-[#00F5FF]/10">
      <CardHeader className="py-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Activity className="h-4 w-4 text-[#00F5FF]" />
            Live Activity
          </CardTitle>
          <Badge variant="outline" className="text-[10px] gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            {events.length > 0 ? 'Live' : 'Waiting'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div ref={scrollRef} className="max-h-80 overflow-y-auto">
          {events.length === 0 ? (
            <div className="text-center py-8 text-xs text-muted-foreground">
              Waiting for events...
            </div>
          ) : (
            events.map((ev, i) => {
              const Icon = EVENT_ICONS[ev.event] || Activity
              const color = EVENT_COLORS[ev.event] || 'text-muted-foreground bg-secondary/20'
              return (
                <div key={`${ev.event}-${i}`} className="flex items-start gap-3 px-4 py-2.5 border-b border-border/30 last:border-0 hover:bg-secondary/20 transition-colors">
                  <div className={`p-1 rounded mt-0.5 ${color}`}>
                    <Icon className="h-3 w-3" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-foreground truncate">{getEventText(ev)}</p>
                    <p className="text-[10px] text-muted-foreground flex items-center gap-1 mt-0.5">
                      <Clock className="h-2.5 w-2.5" />
                      {timeAgo(ev._ts || ev.notification?.created_at || new Date().toISOString())}
                    </p>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
