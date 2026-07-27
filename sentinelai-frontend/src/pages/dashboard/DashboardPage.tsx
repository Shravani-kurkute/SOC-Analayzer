import { motion } from 'framer-motion';
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
  Users,
  Globe,
  Zap,
} from 'lucide-react';
import { StatCard } from '@components/common/StatCard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card';
import { Badge } from '@components/ui/badge';
import { Button } from '@components/ui/button';

import { Progress } from '@components/ui/progress';
import { PageHeader } from '@components/common/PageHeader';

const stats = [
  {
    title: 'Total Alerts',
    value: '1,284',
    description: 'Last 24 hours',
    icon: AlertTriangle,
    variant: 'danger' as const,
    trend: { value: 12, isUp: true },
  },
  {
    title: 'Active Incidents',
    value: '7',
    description: '3 critical, 2 high, 2 medium',
    icon: Siren,
    variant: 'warning' as const,
    trend: { value: 2, isUp: false },
  },
  {
    title: 'Threats Blocked',
    value: '15.3K',
    description: 'Automated prevention',
    icon: Shield,
    variant: 'success' as const,
    trend: { value: 8, isUp: true },
  },
  {
    title: 'Assets Monitored',
    value: '2,547',
    description: '93% coverage',
    icon: Server,
    variant: 'info' as const,
    trend: { value: 5, isUp: true },
  },
];

const recentAlerts = [
  {
    id: 'ALT-2024-3841',
    title: 'Brute Force Attack Detected',
    severity: 'critical' as const,
    source: 'Firewall-01',
    timestamp: '2 minutes ago',
    status: 'new' as const,
  },
  {
    id: 'ALT-2024-3840',
    title: 'Malware Quarantine Alert',
    severity: 'high' as const,
    source: 'EDR-Endpoint-42',
    timestamp: '8 minutes ago',
    status: 'acknowledged' as const,
  },
  {
    id: 'ALT-2024-3839',
    title: 'Unusual Outbound Traffic',
    severity: 'medium' as const,
    source: 'Network-Segment-B',
    timestamp: '15 minutes ago',
    status: 'investigating' as const,
  },
  {
    id: 'ALT-2024-3838',
    title: 'Phishing Email Reported',
    severity: 'medium' as const,
    source: 'Email-Gateway',
    timestamp: '22 minutes ago',
    status: 'new' as const,
  },
  {
    id: 'ALT-2024-3837',
    title: 'USB Device Blocked',
    severity: 'low' as const,
    source: 'DLP-Policy-03',
    timestamp: '31 minutes ago',
    status: 'resolved' as const,
  },
];

const threatActivity = [
  { name: '00:00', value: 45 },
  { name: '04:00', value: 78 },
  { name: '08:00', value: 142 },
  { name: '12:00', value: 98 },
  { name: '16:00', value: 187 },
  { name: '20:00', value: 134 },
  { name: 'Now', value: 67 },
];

const mitreTactics = [
  { tactic: 'Initial Access', count: 42, percentage: 85 },
  { tactic: 'Execution', count: 38, percentage: 72 },
  { tactic: 'Persistence', count: 25, percentage: 54 },
  { tactic: 'Privilege Escalation', count: 31, percentage: 63 },
  { tactic: 'Defense Evasion', count: 47, percentage: 91 },
  { tactic: 'Credential Access', count: 19, percentage: 41 },
];

const severityColors = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};

const statusColors = {
  new: 'text-blue-400 bg-blue-500/10',
  acknowledged: 'text-yellow-400 bg-yellow-500/10',
  investigating: 'text-purple-400 bg-purple-500/10',
  resolved: 'text-emerald-400 bg-emerald-500/10',
};

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Dashboard"
        description="Real-time security operations overview"
        actions={
          <>
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Filter
            </Button>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="accent" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div>
              <CardTitle>Threat Activity</CardTitle>
              <CardDescription>Past 24 hours detection events</CardDescription>
            </div>
            <Badge variant="default" className="gap-1">
              <Activity className="h-3 w-3" />
              Live
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="relative h-64">
              <div className="absolute inset-0 flex items-end justify-between gap-2">
                {threatActivity.map((point) => {
                  const height = (point.value / 187) * 100;
                  const isPeak = point.value > 140;
                  return (
                    <div key={point.name} className="relative flex h-full flex-col items-center justify-end flex-1 group">
                      <span className="absolute -top-6 text-[10px] text-muted-foreground/60 opacity-0 group-hover:opacity-100 transition-opacity">
                        {point.value}
                      </span>
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${height}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className={`w-full mx-0.5 rounded-t-lg transition-all duration-300 group-hover:opacity-80 ${
                          isPeak
                            ? 'bg-gradient-to-t from-red-500 to-red-400 shadow-[0_0_15px_rgba(239,68,68,0.3)]'
                            : 'bg-gradient-to-t from-[#00F5FF]/60 to-[#00F5FF]/30'
                        }`}
                      />
                      <span className="mt-2 text-[9px] text-muted-foreground/40">{point.name}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>MITRE ATT&CK</CardTitle>
            <CardDescription>Top tactics detected</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mitreTactics.map((tactic) => (
              <div key={tactic.tactic} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-foreground">{tactic.tactic}</span>
                  <span className="text-xs text-muted-foreground">{tactic.count} alerts</span>
                </div>
                <div className="relative">
                  <Progress value={tactic.percentage} className="h-2" />
                  <div
                    className={`absolute inset-0 h-2 rounded-full bg-gradient-to-r ${
                      tactic.percentage > 80
                        ? 'from-red-500/20 to-red-500/5'
                        : tactic.percentage > 60
                        ? 'from-orange-500/20 to-orange-500/5'
                        : 'from-yellow-500/20 to-yellow-500/5'
                    }`}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div>
              <CardTitle>Recent Alerts</CardTitle>
              <CardDescription>Latest security events requiring attention</CardDescription>
            </div>
            <Badge variant="critical" className="gap-1">
              <Zap className="h-3 w-3" />
              {recentAlerts.length} active
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentAlerts.map((alert) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="group flex items-center gap-3 rounded-lg border border-border/50 p-3 transition-all duration-200 hover:border-border hover:bg-accent/30"
                >
                  <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${severityColors[alert.severity]}`}>
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-muted-foreground">{alert.id}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${statusColors[alert.status]}`}>
                        {alert.status}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-foreground truncate">{alert.title}</p>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-[11px] text-muted-foreground">{alert.source}</span>
                      <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {alert.timestamp}
                      </span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon-sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Security Posture</CardTitle>
            <CardDescription>Overall security health score</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center py-8">
              <div className="relative">
                <svg className="h-40 w-40 -rotate-90" viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    fill="none"
                    stroke="hsl(var(--muted))"
                    strokeWidth="8"
                  />
                  <motion.circle
                    cx="60"
                    cy="60"
                    r="54"
                    fill="none"
                    stroke="url(#gauge-gradient)"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={`${(85 / 100) * 339.292} 339.292`}
                    initial={{ strokeDasharray: '0 339.292' }}
                    animate={{ strokeDasharray: `${(85 / 100) * 339.292} 339.292` }}
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
                      85
                    </motion.p>
                    <p className="text-xs text-muted-foreground">/100</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Endpoint Protection', value: 94, color: 'text-emerald-400' },
                { label: 'Network Security', value: 88, color: 'text-emerald-400' },
                { label: 'Identity Security', value: 76, color: 'text-yellow-400' },
                { label: 'Data Protection', value: 82, color: 'text-[#00F5FF]' },
              ].map((item) => (
                <div key={item.label} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{item.label}</span>
                    <span className={`text-xs font-medium ${item.color}`}>{item.value}%</span>
                  </div>
                  <Progress value={item.value} className="h-1.5" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Active Analysts', value: '12', icon: Users, desc: '3 on-call', variant: 'info' as const },
          { label: 'SIEM Events/s', value: '12.4K', icon: Activity, desc: 'Peak: 18.2K', variant: 'default' as const },
          { label: 'Geo-Blocked IPs', value: '847', icon: Globe, desc: '+124 today', variant: 'success' as const },
          { label: 'Avg Response Time', value: '4.2m', icon: Zap, desc: '12% faster', variant: 'warning' as const },
        ].map((item) => (
          <Card key={item.label} className="p-4">
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                item.variant === 'info' ? 'bg-[#00F5FF]/10 text-[#00F5FF]' :
                item.variant === 'success' ? 'bg-emerald-500/10 text-emerald-400' :
                item.variant === 'warning' ? 'bg-yellow-500/10 text-yellow-400' :
                'bg-primary/10 text-primary'
              }`}>
                <item.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="text-lg font-bold text-foreground">{item.value}</p>
                <p className="text-[10px] text-muted-foreground/60">{item.desc}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
