import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  AlertTriangle, Activity, Play, Shield,
  Search, X, ChevronLeft, ChevronRight,
  Filter, Clock, Globe, Target, Zap,
  CheckCircle, XCircle, BookOpen, Server,
} from 'lucide-react';
import { PageHeader } from '@components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@components/ui/card';
import { Button } from '@components/ui/button';
import { Badge } from '@components/ui/badge';
import { Input } from '@components/ui/input';
import { Skeleton } from '@components/ui/skeleton';
import { StatCard } from '@components/common/StatCard';
import { alertService } from '@services/alertService';
import type { Alert } from '@typings/alert';

type SevCfg = { variant: 'critical' | 'warning' | 'info' | 'success'; color: string };
const SEVERITY_CONFIG: { [key: string]: SevCfg } = {
  critical: { variant: 'critical', color: 'text-red-400 bg-red-500/10 border-red-500/20' },
  high: { variant: 'warning', color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' },
  medium: { variant: 'info', color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' },
  low: { variant: 'success', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  informational: { variant: 'info', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
};

type StatusCfg = { variant: 'critical' | 'warning' | 'success' | 'outline' | 'secondary' };
const STATUS_CONFIG: { [key: string]: StatusCfg } = {
  open: { variant: 'critical' },
  acknowledged: { variant: 'warning' },
  investigating: { variant: 'outline' },
  resolved: { variant: 'success' },
  false_positive: { variant: 'secondary' },
};

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function AlertDetailCard({ alert }: { alert: Alert }) {
  const queryClient = useQueryClient();
  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => alertService.updateAlert(alert.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] });
    },
  });

  const severityCfg = (SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.medium) as SevCfg;

  return (
    <Card className="border-[#00F5FF]/30">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base">{alert.title}</CardTitle>
              <Badge variant={severityCfg.variant} className="text-[10px]">{alert.severity}</Badge>
            </div>
            <CardDescription className="text-xs">{alert.description}</CardDescription>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-xs text-muted-foreground">Score</span>
            <span className={`text-lg font-bold tabular-nums ${alert.score >= 70 ? 'text-red-400' : alert.score >= 40 ? 'text-yellow-400' : 'text-emerald-400'}`}>
              {alert.score}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3 text-xs">
          {alert.source_ip && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Globe className="h-3.5 w-3.5" />
              <span>Source: <span className="font-mono text-foreground">{alert.source_ip}</span></span>
            </div>
          )}
          {alert.destination_ip && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Target className="h-3.5 w-3.5" />
              <span>Dest: <span className="font-mono text-foreground">{alert.destination_ip}</span></span>
            </div>
          )}
          {alert.protocol && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Server className="h-3.5 w-3.5" />
              <span>Proto: <span className="font-mono text-foreground">{alert.protocol}</span></span>
            </div>
          )}
          {alert.rule_name && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Shield className="h-3.5 w-3.5" />
              <span>Rule: <span className="text-foreground">{alert.rule_name}</span></span>
            </div>
          )}
          {alert.country && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Globe className="h-3.5 w-3.5" />
              <span>Country: <span className="text-foreground">{alert.country}</span></span>
            </div>
          )}
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span>{new Date(alert.created_at).toLocaleString()}</span>
          </div>
        </div>

        {alert.mitre_technique_id && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] text-muted-foreground">MITRE:</span>
            <Badge variant="outline" className="text-[10px] font-mono">
              {alert.mitre_technique_id}
            </Badge>
            {alert.mitre_tactic && (
              <Badge variant="secondary" className="text-[10px]">{alert.mitre_tactic}</Badge>
            )}
          </div>
        )}

        {alert.recommendation && (
          <div className="rounded-md border border-blue-500/20 bg-blue-500/5 p-3">
            <div className="flex items-start gap-2">
              <BookOpen className="mt-0.5 h-3.5 w-3.5 text-blue-400 shrink-0" />
              <div>
                <p className="text-[10px] font-medium text-blue-400 mb-0.5">Recommendation</p>
                <p className="text-xs text-muted-foreground">{alert.recommendation}</p>
              </div>
            </div>
          </div>
        )}

        {alert.tags && alert.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {alert.tags.map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 rounded text-[10px] bg-muted text-muted-foreground font-mono">
                {tag}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 pt-2 border-t border-border/50">
          <span className="text-[10px] text-muted-foreground">Status:</span>
          <Badge variant={((STATUS_CONFIG[alert.status] || STATUS_CONFIG.open) as StatusCfg).variant} className="text-[10px] h-5">
            {alert.status}
          </Badge>
          {alert.status === 'open' && (
            <Button variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => updateMutation.mutate({ status: 'acknowledged' })}>
              <CheckCircle className="mr-1 h-3 w-3" />Acknowledge
            </Button>
          )}
          {alert.status === 'acknowledged' && (
            <Button variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => updateMutation.mutate({ status: 'resolved' })}>
              <CheckCircle className="mr-1 h-3 w-3" />Resolve
            </Button>
          )}
          {alert.status === 'open' && (
            <Button variant="outline" size="sm" className="h-7 text-[10px] text-red-400 border-red-500/30" onClick={() => updateMutation.mutate({ status: 'false_positive' })}>
              <XCircle className="mr-1 h-3 w-3" />False Positive
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function AlertsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const queryParams = useMemo(() => {
    const params: Record<string, unknown> = { page, page_size: 20, sort_by: 'created_at', sort_order: 'desc' };
    if (filterSeverity) params.severity = filterSeverity;
    if (filterStatus) params.status = filterStatus;
    if (search) params.search = search;
    return params;
  }, [page, filterSeverity, filterStatus, search]);

  const alertsQuery = useQuery({
    queryKey: ['alerts', queryParams],
    queryFn: () => alertService.getAlerts(queryParams),
    refetchInterval: 15_000,
  });

  const statsQuery = useQuery({
    queryKey: ['alert-stats'],
    queryFn: () => alertService.getStats(),
    refetchInterval: 30_000,
  });

  const selectedAlert = useMemo(() => {
    if (!selectedId || !alertsQuery.data) return null;
    return alertsQuery.data.items.find((a) => a.id === selectedId) || null;
  }, [selectedId, alertsQuery.data]);

  const runDetectionMutation = useMutation({
    mutationFn: () => alertService.getAlerts({ page: 1, page_size: 1 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] });
    },
  });

  const alerts = alertsQuery.data;
  const stats = statsQuery.data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Security Alerts"
        description="Monitor and respond to detected threats"
        actions={
          <>
            <Button variant="outline" size="sm" onClick={() => { setFilterSeverity(null); setFilterStatus(null); setSearch(''); setPage(1); }}>
              <Filter className="mr-2 h-4 w-4" />Clear Filters
            </Button>
            <Button variant="accent" size="sm" onClick={() => runDetectionMutation.mutate()}>
              <Play className="mr-2 h-4 w-4" />Run Detection
            </Button>
          </>
        }
      />

      {alertsQuery.isError && (
        <Card className="border-red-500/30 bg-red-500/5 p-4">
          <p className="text-sm text-red-400">Failed to load alerts</p>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats ? (
          <>
            <StatCard title="Total Alerts" value={formatNumber(stats.total)} description="All generated alerts" icon={Activity} variant="info" />
            <StatCard title="Critical" value={stats.by_severity.critical || 0} description="Requires immediate action" icon={AlertTriangle} variant="danger" />
            <StatCard title="High" value={stats.by_severity.high || 0} description="Needs investigation" icon={Zap} variant="warning" />
            <StatCard title="Avg Score" value={stats.avg_score.toFixed(1)} description="Average alert severity score" icon={Shield} variant={stats.avg_score > 5 ? 'warning' : 'default'} />
          </>
        ) : (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5"><Skeleton className="h-16 w-full" /></Card>
          ))
        )}
      </div>

      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search alerts..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9 h-9 text-sm"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="h-3 w-3" />
            </button>
          )}
        </div>
        <select
          value={filterSeverity || ''}
          onChange={(e) => { setFilterSeverity(e.target.value || null); setPage(1); }}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground"
        >
          <option value="">All severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={filterStatus || ''}
          onChange={(e) => { setFilterStatus(e.target.value || null); setPage(1); }}
          className="h-9 rounded-md border border-input bg-background px-3 text-xs text-muted-foreground"
        >
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
          <option value="false_positive">False Positive</option>
        </select>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className={`space-y-2 ${selectedId ? 'lg:col-span-1' : 'lg:col-span-3'}`}>
          {alertsQuery.isError ? (
            <Card className="border-red-500/30 bg-red-500/5 p-4">
              <p className="text-sm text-red-400">Failed to load alerts</p>
            </Card>
          ) : alerts ? (
            alerts.items.length === 0 ? (
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center justify-center py-8 text-sm text-muted-foreground">
                    <Shield className="mb-2 h-8 w-8" />
                    <p>No alerts found</p>
                    <p className="text-xs mt-1">Run detection rules on parsed events to generate alerts</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="flex items-center justify-between px-1 mb-1">
                  <span className="text-xs text-muted-foreground">{alerts.total} alert{alerts.total !== 1 ? 's' : ''}</span>
                  {alerts.total_pages > 1 && (
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="icon-sm" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <span className="text-[10px] text-muted-foreground tabular-nums">{page}/{alerts.total_pages}</span>
                      <Button variant="ghost" size="icon-sm" disabled={page >= alerts.total_pages} onClick={() => setPage((p) => p + 1)}>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
                {alerts.items.map((alert, i) => {
                  const severityCfg = (SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.medium) as SevCfg;
                  return (
                    <motion.button
                      key={alert.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                      onClick={() => setSelectedId(selectedId === alert.id ? null : alert.id)}
                      className={`w-full text-left rounded-lg border p-3 transition-all hover:border-[#00F5FF]/30 hover:bg-accent/30 ${
                        selectedId === alert.id ? 'border-[#00F5FF]/50 bg-[#00F5FF]/5' : 'border-border/50'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${severityCfg.color}`}>
                          {alert.severity}
                        </span>
                        <Badge variant={((STATUS_CONFIG[alert.status] || STATUS_CONFIG.open) as StatusCfg).variant} className="text-[10px] h-4 px-1">
                          {alert.status}
                        </Badge>
                        {alert.mitre_technique_id && (
                          <span className="text-[10px] font-mono text-muted-foreground">{alert.mitre_technique_id}</span>
                        )}
                      </div>
                      <p className="text-xs font-medium text-foreground truncate">{alert.title}</p>
                      {alert.source_ip && (
                        <p className="text-[10px] font-mono text-muted-foreground mt-0.5">{alert.source_ip}</p>
                      )}
                      <div className="flex items-center gap-3 mt-1 text-[10px] text-muted-foreground">
                        <span className={`font-medium tabular-nums ${alert.score >= 70 ? 'text-red-400' : alert.score >= 40 ? 'text-yellow-400' : 'text-emerald-400'}`}>
                          Score: {alert.score}
                        </span>
                        <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{timeAgo(alert.created_at)}</span>
                      </div>
                    </motion.button>
                  );
                })}
              </>
            )
          ) : (
            Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-lg" />
            ))
          )}
        </div>

        {selectedId && selectedAlert && (
          <div className="lg:col-span-2">
            <AlertDetailCard alert={selectedAlert} />
          </div>
        )}

        {selectedId && !selectedAlert && alertsQuery.data && (
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-8">
                <div className="flex flex-col items-center justify-center text-sm text-muted-foreground">
                  <AlertTriangle className="mb-2 h-8 w-8" />
                  <p>Alert not found</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
