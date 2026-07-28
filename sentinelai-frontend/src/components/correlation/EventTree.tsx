import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight, ChevronDown, Globe, AlertTriangle, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import { cn } from '@utils/cn'
import type { EventTree as EventTreeType } from '@typings/correlation'

interface EventTreeProps {
  tree: EventTreeType | null
  isLoading?: boolean
}

export function EventTree({ tree, isLoading }: EventTreeProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Event Tree</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-12 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!tree || tree.total_events === 0) {
    return (
      <Card>
        <CardHeader><CardTitle>Event Tree</CardTitle></CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
            <Activity className="mr-2 h-4 w-4" />
            No event tree data
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Event Tree
          <Badge variant="default" className="ml-auto text-[10px]">{tree.total_events} events</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {Object.entries(tree.source_groups).map(([sourceIp, group]) => (
            <SourceGroup key={sourceIp} sourceIp={sourceIp} group={group} />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function SourceGroup({ sourceIp, group }: { sourceIp: string; group: EventTreeType['source_groups'][string] }) {
  const [expanded, setExpanded] = useState(false)

  const topSeverity = Object.entries(group.severity_distribution).sort(
    ([, a], [, b]) => b - a,
  )[0]?.[0] || 'info'

  return (
    <div className="rounded-lg border border-border/50">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 p-3 text-left hover:bg-accent/30 transition-colors"
      >
        {expanded ? <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />}
        <Globe className="h-4 w-4 text-[#00F5FF]" />
        <span className="text-sm font-mono font-medium">{sourceIp}</span>
        <Badge variant="outline" className="text-[10px] ml-auto">{group.count} events</Badge>
        <Badge variant={topSeverity === 'critical' ? 'critical' : 'default'} className="text-[10px]">{topSeverity}</Badge>
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border/50 p-3 space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground">Actions</p>
                  {Object.entries(group.action_types).map(([action, count]) => (
                    <div key={action} className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground truncate">{action}</span>
                      <span className="font-mono">{count}</span>
                    </div>
                  ))}
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground">Severity</p>
                  {Object.entries(group.severity_distribution).map(([sev, count]) => (
                    <div key={sev} className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground capitalize">{sev}</span>
                      <span className="font-mono">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
              {group.events.length > 5 && (
                <p className="text-[10px] text-muted-foreground">
                  Showing first 5 of {group.events.length} events
                </p>
              )}
              {group.events.slice(0, 5).map((event) => (
                <div key={event.id} className="flex items-center gap-2 rounded bg-muted/30 p-2 text-xs">
                  <AlertTriangle className={cn('h-3 w-3 shrink-0', event.severity === 'critical' ? 'text-red-400' : 'text-muted-foreground')} />
                  <span className="font-mono text-muted-foreground">{event.event_type}</span>
                  <span className="text-muted-foreground">{event.action || '-'}</span>
                  <span className="ml-auto text-muted-foreground">{new Date(event.timestamp).toLocaleTimeString()}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
