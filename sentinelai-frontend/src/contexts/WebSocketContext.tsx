import { createContext, useContext, useCallback, useRef, useState, useEffect } from 'react'
import type { WebSocketStatus, LiveActivityEvent } from '@typings/notification'

const WS_URL = 'ws://localhost:8000/ws'

function getToken(): string | null {
  return localStorage.getItem('sentinelai_auth_token')
}

interface WebSocketContextType {
  status: WebSocketStatus
  send: (data: unknown) => void
  subscribe: (channel: string, handler: (event: LiveActivityEvent) => void) => () => void
  lastEvent: LiveActivityEvent | null
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected')
  const [lastEvent, setLastEvent] = useState<LiveActivityEvent | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()
  const handlersRef = useRef<Map<string, Set<(event: LiveActivityEvent) => void>>>(new Map())
  const pingIntervalRef = useRef<ReturnType<typeof setInterval>>()
  const reconnectAttemptRef = useRef(0)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return
    const token = getToken()
    if (!token) return

    setStatus('connecting')
    const url = `${WS_URL}?token=${encodeURIComponent(token)}`
    const ws = new WebSocket(url)

    ws.onopen = () => {
      setStatus('connected')
      reconnectAttemptRef.current = 0
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)
    }

    ws.onclose = () => {
      setStatus('disconnected')
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current)
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptRef.current), 30000)
      reconnectAttemptRef.current++
      reconnectTimeoutRef.current = setTimeout(connect, delay)
    }

    ws.onerror = () => {
      setStatus('error')
      ws.close()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'pong') return
        setLastEvent(data)
        handlersRef.current.forEach((handlers, channel) => {
          if (channel === '*' || channel === data.event || channel === data.type) {
            handlers.forEach(h => h(data))
          }
        })
      } catch {
        // ignore parse errors
      }
    }

    wsRef.current = ws
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, [connect])

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  const subscribe = useCallback((channel: string, handler: (event: LiveActivityEvent) => void) => {
    if (!handlersRef.current.has(channel)) {
      handlersRef.current.set(channel, new Set())
    }
    handlersRef.current.get(channel)!.add(handler)
    return () => {
      handlersRef.current.get(channel)?.delete(handler)
    }
  }, [])

  return (
    <WebSocketContext.Provider value={{ status, send, subscribe, lastEvent }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const ctx = useContext(WebSocketContext)
  if (!ctx) throw new Error('useWebSocket must be used within WebSocketProvider')
  return ctx
}
