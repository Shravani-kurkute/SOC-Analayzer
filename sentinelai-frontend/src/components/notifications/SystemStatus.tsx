import { useWebSocket } from '@contexts/WebSocketContext'
import { Card, CardContent } from '@components/ui/card'

const statusDot = (status: string) => {
  if (status === 'connected' || status === 'healthy') return 'bg-emerald-500'
  if (status === 'connecting' || status === 'degraded') return 'bg-orange-500'
  return 'bg-red-500'
}

const statusLabel = (status: string) => {
  if (status === 'connected') return 'Connected'
  if (status === 'connecting') return 'Connecting...'
  if (status === 'disconnected') return 'Disconnected'
  if (status === 'error') return 'Error'
  if (status === 'healthy') return 'Healthy'
  if (status === 'degraded') return 'Degraded'
  return 'Down'
}

export function SystemStatus() {
  const { status: wsStatus } = useWebSocket()

  return (
    <Card className="border-[#00F5FF]/10">
      <CardContent className="p-3">
        <p className="text-xs font-medium text-muted-foreground mb-2">System Status</p>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${statusDot(wsStatus)}`} />
              <span className="text-xs">WebSocket</span>
            </div>
            <span className={`text-[10px] ${wsStatus === 'connected' ? 'text-emerald-400' : wsStatus === 'connecting' ? 'text-orange-400' : 'text-red-400'}`}>
              {statusLabel(wsStatus)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-xs">Backend</span>
            </div>
            <span className="text-[10px] text-emerald-400">Healthy</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-xs">Database</span>
            </div>
            <span className="text-[10px] text-emerald-400">Healthy</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-xs">Redis</span>
            </div>
            <span className="text-[10px] text-emerald-400">Healthy</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
