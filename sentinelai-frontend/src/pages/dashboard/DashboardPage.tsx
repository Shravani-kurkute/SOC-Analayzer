import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  AlertTriangle,
  Siren,
  Shield,
  Server,
  Activity,
  MoreHorizontal,
  RefreshCw,
  Download,
  Filter,
  Clock,
  Globe,
  Zap,
  FileText,
  TrendingUp,
  Network,
  Hash,
  Target,
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { StatCard } from '@components/common/StatCard'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import { Button } from '@components/ui/button'
import { Skeleton } from '@components/ui/skeleton'
import { PageHeader } from '@components/common/PageHeader'
import { mitreService } from '@services/mitreService'
import { iocService } from '@services/iocService'
import { dashboardService } from '@services/dashboardService'
import type {
  RecentAlertItem,
  RecentIncidentItem,
  RecentLogItem,
  MostActiveSourceIp,
} from '@typings/dashboard'

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#EF4444',
  high: '#F97316',
  medium: '#EAB308',
  low: '#22C55E',
  informational: '#6366F1',
}

const SEVERITY_BG: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  informational: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
}

const STATUS_BG: Record<string, string> = {
  new: 'text-blue-400 bg-blue-500/10',
  acknowledged: 'text-yellow-400 bg-yellow-500/10',
  investigating: 'text-purple-400 bg-purple-500/10',
  resolved: 'text-emerald-400 bg-emerald-500/10',
  false_positive: 'text-gray-400 bg-gray-500/10',
  open: 'text-blue-400 bg-blue-500/10',
  contained: 'text-orange-400 bg-orange-500/10',
  eradiated: 'text-purple-400 bg-purple-500/10',
  recovered: 'text-emerald-400 bg-emerald-500/10',
  closed: 'text-gray-400 bg-gray-500/10',
}

function StatSkeleton() {
  return (
    <Card className="p-5">
      <div className="space-y-3">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-3 w-32" />
      </div>
    </Card>
  )
}

function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-5 w-48" />
        <Skeleton className="h-4 w-64" />
      </CardHeader>
      <CardContent>
        <Skeleton className={`w-full rounded-lg`} style={{ height }} />
      </CardContent>
    </Card>
  )
}

function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-4 w-56" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-lg" />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

function getSeverityVariant(severity: string): 'critical' | 'warning' | 'success' | 'info' | 'default' {
  const map: Record<string, 'critical' | 'warning' | 'success' | 'info' | 'default'> = {
    critical: 'critical',
    high: 'warning',
    medium: 'warning',
    low: 'info',
    informational: 'default',
  }
  return map[severity] || 'default'
}

export default function DashboardPage() {
  const summaryQuery = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: dashboardService.getSummary,
    refetchInterval: 30_000,
  })

  const chartsQuery = useQuery({
    queryKey: ['dashboard-charts'],
    queryFn: dashboardService.getCharts,
    refetchInterval: 30_000,
  })

  const recentAlertsQuery = useQuery({
    queryKey: ['dashboard-recent-alerts'],
    queryFn: () => dashboardService.getRecentAlerts(5),
    refetchInterval: 30_000,
  })

  const recentIncidentsQuery = useQuery({
    queryKey: ['dashboard-recent-incidents'],
    queryFn: () => dashboardService.getRecentIncidents(5),
    refetchInterval: 30_000,
  })

  const recentLogsQuery = useQuery({
    queryKey: ['dashboard-recent-logs'],
    queryFn: () => dashboardService.getRecentLogs(5),
    refetchInterval: 30_000,
  })

  const activeIpsQuery = useQuery({
    queryKey: ['dashboard-active-ips'],
    queryFn: () => dashboardService.getMostActiveIps(5),
    refetchInterval: 30_000,
  })

  const iocStatsQuery = useQuery({
    queryKey: ['dashboard-ioc-stats'],
    queryFn: iocService.getStats,
    refetchInterval: 30_000,
  })

  const mitreCoverageQuery = useQuery({
    queryKey: ['dashboard-mitre-coverage'],
    queryFn: mitreService.getCoverage,
    refetchInterval: 60_000,
  })

  const summary = summaryQuery.data
  const charts = chartsQuery.data
  const iocStats = iocStatsQuery.data
  const mitreCoverage = mitreCoverageQuery.data

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Dashboard"
        description="Real-time security operations overview"
        actions={
          <>
            <Button variant="outline" size="sm"><Filter className="mr-2 h-4 w-4" />Filter</Button>
            <Button variant="outline" size="sm"><Download className="mr-2 h-4 w-4" />Export</Button>
            <Button
              variant="accent" size="sm"
              onClick={() => {
                summaryQuery.refetch()
                chartsQuery.refetch()
                recentAlertsQuery.refetch()
                recentIncidentsQuery.refetch()
                recentLogsQuery.refetch()
                activeIpsQuery.refetch()
              }}
            >
              <RefreshCw className="mr-2 h-4 w-4" />Refresh
            </Button>
          </>
        }
      />

      {summaryQuery.isError && (
        <Card className="border-red-500/30 bg-red-500/5 p-4">
          <p className="text-sm text-red-400">Failed to load dashboard data: {summaryQuery.error?.message || 'Unknown error'}</p>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {summary ? (
          <>
            <StatCard
              title="Total Logs Processed"
              value={formatNumber(summary.total_logs_processed)}
              description="Last 24 hours"
              icon={FileText}
              variant="info"
            />
            <StatCard
              title="Active Incidents"
              value={summary.active_incidents}
              description="Requiring investigation"
              icon={Siren}
              variant="warning"
            />
            <StatCard
              title="Critical Alerts"
              value={summary.critical_alerts}
              description="Immediate action required"
              icon={AlertTriangle}
              variant="danger"
            />
            <StatCard
              title="High Alerts"
              value={summary.high_alerts}
              description="Priority investigation"
              icon={Zap}
              variant="warning"
            />
            <StatCard
              title="Medium Alerts"
              value={summary.medium_alerts}
              description="Review needed"
              icon={Activity}
              variant="default"
            />
            <StatCard
              title="Low Alerts"
              value={summary.low_alerts}
              description="Informational"
              icon={Shield}
              variant="success"
            />
            <StatCard
              title="Threat Score"
              value={`${summary.threat_score}%`}
              description="Overall risk level"
              icon={TrendingUp}
              variant={summary.threat_score > 70 ? 'danger' : summary.threat_score > 40 ? 'warning' : 'success'}
            />
            <StatCard
              title="Assets Monitored"
              value={summary.assets_monitored}
              description="Coverage across network"
              icon={Server}
              variant="info"
            />
          </>
        ) : (
          Array.from({ length: 8 }).map((_, i) => <StatSkeleton key={i} />)
        )}
      </div>

      {iocStats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total IOCs" value={formatNumber(iocStats.total)} description="Extracted indicators" icon={Shield} variant="info" />
          <StatCard title="Unique IPs" value={formatNumber(iocStats.unique_ips)} description="IPv4 & IPv6 addresses" icon={Globe} variant="info" />
          <StatCard title="Unique Domains" value={formatNumber(iocStats.unique_domains)} description="Domain indicators" icon={Globe} variant="warning" />
          <StatCard title="Unique Hashes" value={formatNumber(iocStats.unique_hashes)} description="MD5, SHA1, SHA256" icon={Hash} variant="danger" />
        </div>
      )}

      {mitreCoverage && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="ATT&CK Coverage" value={`${mitreCoverage.overall_coverage.toFixed(1)}%`}
            description={`${mitreCoverage.total_mapped}/${mitreCoverage.total_techniques} techniques`}
            icon={Target} variant={mitreCoverage.overall_coverage >= 50 ? 'success' : 'warning'} />
          <StatCard title="Total Techniques" value={formatNumber(mitreCoverage.total_techniques)} description="MITRE ATT&CK v15.1" icon={Hash} variant="info" />
          <StatCard title="Mapped Techniques" value={formatNumber(mitreCoverage.total_mapped)} description="With detection coverage" icon={Target} variant="info" />
          <StatCard title="Total Detections" value={formatNumber(mitreCoverage.total_detections)} description="Mapped to MITRE techniques" icon={Activity} variant="info" />
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {charts ? (
          <>
            <Card className="xl:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between pb-4">
                <div>
                  <CardTitle>Attack Timeline</CardTitle>
                  <CardDescription>Security events over the past 24 hours</CardDescription>
                </div>
                <Badge variant="default" className="gap-1"><Activity className="h-3 w-3" />Live</Badge>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={charts.attack_timeline}>
                      <defs>
                        <linearGradient id="attackGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#00F5FF" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#00F5FF" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="timestamp" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                      <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#00F5FF"
                        strokeWidth={2}
                        fill="url(#attackGradient)"
                        animationDuration={800}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Alerts by Severity</CardTitle>
                <CardDescription>Distribution of alert severities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={charts.alerts_by_severity}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={3}
                        dataKey="value"
                        animationDuration={800}
                      >
                        {charts.alerts_by_severity.map((entry) => (
                          <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name] || '#6366F1'} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2">
                  {charts.alerts_by_severity.map((entry) => (
                    <div key={entry.name} className="flex items-center gap-2 text-xs">
                      <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: SEVERITY_COLORS[entry.name] || '#6366F1' }} />
                      <span className="capitalize text-muted-foreground">{entry.name}</span>
                      <span className="ml-auto font-medium text-foreground">{entry.value}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Attack Types</CardTitle>
                <CardDescription>Top MITRE tactics detected</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.attack_types} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={140}
                        tick={{ fontSize: 9, fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="count" fill="#00F5FF" radius={[0, 4, 4, 0]} animationDuration={800} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Source IPs</CardTitle>
                <CardDescription>Most frequently detected IPs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.top_source_ips} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                      <YAxis
                        type="category"
                        dataKey="ip"
                        width={120}
                        tick={{ fontSize: 9, fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                        formatter={(value: number) => [`${value} alerts`, 'Count']}
                      />
                      <Bar dataKey="count" fill="#F97316" radius={[0, 4, 4, 0]} animationDuration={800} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>MITRE ATT&CK</CardTitle>
                <CardDescription>Technique distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.mitre_distribution} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                      <YAxis
                        type="category"
                        dataKey="tactic"
                        width={140}
                        tick={{ fontSize: 9, fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="count" fill="#6366F1" radius={[0, 4, 4, 0]} animationDuration={800} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Country Distribution</CardTitle>
                <CardDescription>Threat origins by geography</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.country_distribution} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                      <YAxis
                        type="category"
                        dataKey="country"
                        width={40}
                        tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="count" fill="#22C55E" radius={[0, 4, 4, 0]} animationDuration={800} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <>
            <ChartSkeleton height={288} />
            <ChartSkeleton height={288} />
            <ChartSkeleton height={288} />
            <ChartSkeleton height={288} />
            <ChartSkeleton height={288} />
            <ChartSkeleton height={288} />
          </>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {recentAlertsQuery.isError ? (
          <Card className="border-red-500/30 bg-red-500/5 p-4">
            <p className="text-sm text-red-400">Failed to load recent alerts</p>
          </Card>
        ) : recentAlertsQuery.data ? (
          <Card className="xl:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between pb-4">
              <div>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>Latest security events requiring attention</CardDescription>
              </div>
              <Badge variant="critical" className="gap-1">
                <Zap className="h-3 w-3" />{recentAlertsQuery.data.length} active
              </Badge>
            </CardHeader>
            <CardContent>
              {recentAlertsQuery.data.length === 0 ? (
                <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">No alerts found</div>
              ) : (
                <div className="space-y-2">
                  {recentAlertsQuery.data.map((alert: RecentAlertItem) => (
                    <motion.div
                      key={alert.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="group flex items-center gap-3 rounded-lg border border-border/50 p-3 transition-all duration-200 hover:border-border hover:bg-accent/30"
                    >
                      <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${SEVERITY_BG[alert.severity] || SEVERITY_BG.informational}`}>
                        <AlertTriangle className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-muted-foreground">{alert.id.slice(0, 8)}</span>
                          <Badge variant={getSeverityVariant(alert.severity)} className="text-[10px] h-4 px-1">{alert.severity}</Badge>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${STATUS_BG[alert.status] || STATUS_BG.new}`}>{alert.status}</span>
                          <span className="ml-auto text-[10px] font-mono text-muted-foreground">Score: {alert.score}</span>
                        </div>
                        <p className="text-sm font-medium text-foreground truncate mt-0.5">{alert.title}</p>
                        <div className="flex items-center gap-3 mt-0.5">
                          {alert.source && <span className="text-[11px] text-muted-foreground">{alert.source}</span>}
                          {alert.source_ip && <span className="text-[11px] text-muted-foreground font-mono">{alert.source_ip}</span>}
                          <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3" />{timeAgo(alert.timestamp)}
                          </span>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon-sm" className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <TableSkeleton rows={5} />
        )}

        {activeIpsQuery.isError ? (
          <Card className="border-red-500/30 bg-red-500/5 p-4">
            <p className="text-sm text-red-400">Failed to load active IPs</p>
          </Card>
        ) : activeIpsQuery.data ? (
          <Card>
            <CardHeader>
              <CardTitle>Most Active Source IPs</CardTitle>
              <CardDescription>IPs with highest log activity</CardDescription>
            </CardHeader>
            <CardContent>
              {activeIpsQuery.data.length === 0 ? (
                <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">No IP data found</div>
              ) : (
                <div className="space-y-2">
                  {activeIpsQuery.data.map((ip: MostActiveSourceIp, i: number) => (
                    <motion.div
                      key={ip.ip}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center gap-3 rounded-lg border border-border/50 p-3 transition-all duration-200 hover:border-border hover:bg-accent/30"
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#00F5FF]/10 text-[#00F5FF]">
                        <Globe className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-medium text-foreground">{ip.ip}</span>
                          {ip.country && <span className="text-[10px] text-muted-foreground">({ip.country})</span>}
                        </div>
                        <div className="flex items-center gap-3 mt-0.5">
                          <span className="text-[11px] text-muted-foreground">{ip.log_count} logs</span>
                          <span className="text-[11px] text-muted-foreground">{ip.alert_count} alerts</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold text-foreground">{ip.log_count}</p>
                        <p className="text-[10px] text-muted-foreground">events</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <TableSkeleton rows={5} />
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {recentIncidentsQuery.isError ? (
          <Card className="border-red-500/30 bg-red-500/5 p-4">
            <p className="text-sm text-red-400">Failed to load recent incidents</p>
          </Card>
        ) : recentIncidentsQuery.data ? (
          <Card>
            <CardHeader>
              <CardTitle>Recent Incidents</CardTitle>
              <CardDescription>Active and recent security incidents</CardDescription>
            </CardHeader>
            <CardContent>
              {recentIncidentsQuery.data.length === 0 ? (
                <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">No incidents found</div>
              ) : (
                <div className="space-y-2">
                  {recentIncidentsQuery.data.map((incident: RecentIncidentItem) => (
                    <motion.div
                      key={incident.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="group flex items-center gap-3 rounded-lg border border-border/50 p-3 transition-all duration-200 hover:border-border hover:bg-accent/30"
                    >
                      <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${SEVERITY_BG[incident.severity] || SEVERITY_BG.informational}`}>
                        <Siren className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-muted-foreground">{incident.id.slice(0, 8)}</span>
                          <Badge variant={getSeverityVariant(incident.severity)} className="text-[10px] h-4 px-1">{incident.severity}</Badge>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${STATUS_BG[incident.status] || STATUS_BG.new}`}>{incident.status}</span>
                        </div>
                        <p className="text-sm font-medium text-foreground truncate mt-0.5">{incident.title}</p>
                        <div className="flex items-center gap-3 mt-0.5">
                          {incident.category && <span className="text-[11px] text-muted-foreground">{incident.category}</span>}
                          <span className="text-[11px] text-muted-foreground">{incident.alert_count} alerts</span>
                          <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3" />{timeAgo(incident.created_at)}
                          </span>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon-sm" className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <TableSkeleton rows={5} />
        )}

        {recentLogsQuery.isError ? (
          <Card className="border-red-500/30 bg-red-500/5 p-4">
            <p className="text-sm text-red-400">Failed to load recent logs</p>
          </Card>
        ) : recentLogsQuery.data ? (
          <Card>
            <CardHeader>
              <CardTitle>Newest Logs</CardTitle>
              <CardDescription>Latest log entries from across the network</CardDescription>
            </CardHeader>
            <CardContent>
              {recentLogsQuery.data.length === 0 ? (
                <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">No log entries found</div>
              ) : (
                <div className="space-y-2">
                  {recentLogsQuery.data.map((log: RecentLogItem) => (
                    <motion.div
                      key={log.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="group flex items-center gap-3 rounded-lg border border-border/50 p-3 transition-all duration-200 hover:border-border hover:bg-accent/30"
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Network className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          {log.action && <Badge variant="outline" className="text-[10px] h-4 px-1">{log.action}</Badge>}
                          {log.protocol && <span className="text-[10px] font-mono text-muted-foreground">{log.protocol}</span>}
                          {log.threat_score !== null && log.threat_score !== undefined && log.threat_score > 0 && (
                            <span className="text-[10px] font-mono text-red-400">Score: {log.threat_score}</span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 mt-0.5">
                          {log.source_ip && <span className="text-[11px] font-mono text-foreground">{log.source_ip}</span>}
                          {log.destination_ip && <span className="text-[11px] text-muted-foreground">→ {log.destination_ip}</span>}
                          {log.log_source && <span className="text-[11px] text-muted-foreground">{log.log_source}</span>}
                        </div>
                        <span className="text-[10px] text-muted-foreground flex items-center gap-1 mt-0.5">
                          <Clock className="h-3 w-3" />{timeAgo(log.timestamp)}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <TableSkeleton rows={5} />
        )}

        <Card>
          <CardHeader>
            <CardTitle>Security Posture</CardTitle>
            <CardDescription>Overall security health score</CardDescription>
          </CardHeader>
          <CardContent>
            {summary ? (
              <>
                <div className="flex items-center justify-center py-8">
                  <div className="relative">
                    <svg className="h-40 w-40 -rotate-90" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="54" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                      <motion.circle
                        cx="60" cy="60" r="54" fill="none"
                        stroke="url(#gauge-gradient)" strokeWidth="8" strokeLinecap="round"
                        strokeDasharray={`${(Math.min(summary.threat_score, 100) / 100) * 339.292} 339.292`}
                        initial={{ strokeDasharray: '0 339.292' }}
                        animate={{ strokeDasharray: `${(Math.min(summary.threat_score, 100) / 100) * 339.292} 339.292` }}
                        transition={{ duration: 1.5, ease: 'easeOut' }}
                      />
                      <defs>
                        <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#6366F1" />
                          <stop offset="50%" stopColor="#00F5FF" />
                          <stop offset="100%" stopColor="#10B981" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <motion.p
                          initial={{ opacity: 0, scale: 0.5 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ duration: 0.5, delay: 0.8 }}
                          className="text-4xl font-bold text-foreground"
                        >
                          {100 - Math.round(summary.threat_score)}
                        </motion.p>
                        <p className="text-xs text-muted-foreground">/100</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Log Coverage', value: Math.min(100, Math.round((summary.total_logs_processed / 3000) * 100)), color: 'text-emerald-400' },
                    { label: 'Incident Response', value: Math.min(100, Math.round((1 - summary.active_incidents / (summary.active_incidents + 30)) * 100)), color: 'text-[#00F5FF]' },
                    { label: 'Alert Triage', value: Math.max(0, 100 - Math.round((summary.critical_alerts + summary.high_alerts) / Math.max(1, summary.total_logs_processed / 10) * 100)), color: 'text-yellow-400' },
                    { label: 'Asset Coverage', value: Math.round((summary.assets_monitored / 50) * 100), color: 'text-emerald-400' },
                  ].map((item) => (
                    <div key={item.label} className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">{item.label}</span>
                        <span className={`text-xs font-medium ${item.color}`}>{Math.min(100, item.value)}%</span>
                      </div>
                      <div className="relative h-1.5 rounded-full bg-muted overflow-hidden">
                        <motion.div
                          className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-[#00F5FF] to-primary"
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(100, item.value)}%` }}
                          transition={{ duration: 1, delay: 0.5 }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="space-y-6 py-4">
                <Skeleton className="h-40 w-40 rounded-full mx-auto" />
                <div className="grid grid-cols-2 gap-4">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="space-y-1">
                      <Skeleton className="h-3 w-20" />
                      <Skeleton className="h-1.5 w-full" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
