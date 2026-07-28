import { motion } from 'framer-motion'
import { Clock, AlertTriangle, Globe, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import type { CorrelationEvent } from '@typings/correlation'

const SEVERITY_BG: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10',
  high: 'text-orange-400 bg-orange-500/10',
  medium: 'text-yellow-400 bg-yellow-500/10',
  low: 'text-emerald-400 bg-emerald-500/10',
  info: 'text-blue-400 bg-blue-500/10',
}

interface RelatedEventsProps {
  events: CorrelationEvent[]
  isLoading?: boolean
}

export function RelatedEvents({ events, isLoading }: RelatedEventsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Related Events</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!events || events.length === 0) {
    return (
      <Card>
        <CardHeader><CardTitle>Related Events</CardTitle></CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
            <Activity className="mr-2 h-4 w-4" />
            No related events
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Related Events
          <Badge variant="default" className="ml-auto text-[10px]">{events.length} events</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {events.map((event, idx) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.03 }}
              className="flex items-center gap-3 rounded-lg border border-border/50 p-3 transition-colors hover:border-border hover:bg-accent/30"
            >
              <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${SEVERITY_BG[event.severity || 'info'] || SEVERITY_BG.info}`}>
                <Globe className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] h-4 px-1">{event.event_type}</Badge>
                  {event.severity && (
                    <Badge variant={event.severity === 'critical' ? 'critical' : 'default'} className="text-[10px] h-4 px-1">
                      {event.severity}
                    </Badge>
                  )}
                  {event.risk_score && event.risk_score > 0 && (
                    <span className="text-[10px] font-mono text-red-400">Score: {event.risk_score}</span>
                  )}
                  <span className="ml-auto text-[10px] text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  {event.source_ip && <span className="text-xs font-mono text-foreground">{event.source_ip}</span>}
                  {event.destination_ip && <span className="text-xs text-muted-foreground">→ {event.destination_ip}</span>}
                  {event.action && <span className="text-xs text-muted-foreground">{event.action}</span>}
                </div>
                {event.raw_message && (
                  <p className="text-[10px] text-muted-foreground truncate mt-0.5 font-mono">{event.raw_message}</p>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
