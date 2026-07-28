import { motion } from 'framer-motion'
import { Clock, ArrowRight, Shield, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import type { AttackChainPhase } from '@typings/correlation'

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-emerald-500',
  info: 'bg-blue-500',
}

const PHASE_COLORS: Record<string, string> = {
  reconnaissance: 'border-l-sky-500',
  initial_access: 'border-l-orange-500',
  execution: 'border-l-red-500',
  persistence: 'border-l-purple-500',
  privilege_escalation: 'border-l-pink-500',
  defense_evasion: 'border-l-yellow-500',
  credential_access: 'border-l-amber-500',
  discovery: 'border-l-cyan-500',
  lateral_movement: 'border-l-fuchsia-500',
  collection: 'border-l-indigo-500',
  command_and_control: 'border-l-violet-500',
  exfiltration: 'border-l-rose-500',
  impact: 'border-l-red-600',
}

interface AttackTimelineProps {
  chain: AttackChainPhase[]
  isLoading?: boolean
}

export function AttackTimeline({ chain, isLoading }: AttackTimelineProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle>Attack Chain</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-20 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!chain || chain.length === 0) {
    return (
      <Card>
        <CardHeader><CardTitle>Attack Chain</CardTitle></CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
            <Shield className="mr-2 h-4 w-4" />
            No attack chain data available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Attack Chain
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-0">
          {chain.map((phase, idx) => (
            <motion.div
              key={phase.phase}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`relative border-l-2 pl-6 pb-6 last:pb-0 ${PHASE_COLORS[phase.phase] || 'border-l-muted'}`}
            >
              {idx < chain.length - 1 && (
                <div className="absolute bottom-0 left-[-1px] h-full w-0.5 bg-gradient-to-b from-border to-transparent" />
              )}
              <div className="absolute left-[-9px] top-0 flex h-4 w-4 items-center justify-center rounded-full border-2 border-background bg-card">
                <div className={`h-2 w-2 rounded-full ${SEVERITY_COLORS[phase.max_severity] || 'bg-muted'}`} />
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-muted-foreground">Phase {idx + 1}</span>
                <Badge variant="outline" className="text-[10px] capitalize">{phase.phase.replace(/_/g, ' ')}</Badge>
                <Badge variant={phase.max_severity === 'critical' ? 'critical' : 'default'} className="text-[10px]">
                  {phase.count} events
                </Badge>
              </div>
              <div className="space-y-1">
                {phase.events.slice(0, 3).map((event) => (
                  <div key={event.event_id} className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3 shrink-0" />
                    <span className="font-mono">{event.source_ip || '?'}</span>
                    <ArrowRight className="h-3 w-3 shrink-0" />
                    <span className="font-mono">{event.destination_ip || '?'}</span>
                    <span className="truncate">{event.action || event.event_type}</span>
                    {event.risk_score && event.risk_score > 0 && (
                      <span className="font-mono text-red-400">{event.risk_score}</span>
                    )}
                  </div>
                ))}
                {phase.events.length > 3 && (
                  <p className="text-[10px] text-muted-foreground">+{phase.events.length - 3} more events</p>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
