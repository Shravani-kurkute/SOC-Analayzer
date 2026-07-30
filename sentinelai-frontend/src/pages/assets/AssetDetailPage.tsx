import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Server, Globe, Monitor, HardDrive, Cloud, Container, Wifi, Database,
  ArrowLeft, Edit3, Trash2, RefreshCw,
  Shield, AlertTriangle, Siren, Brain, FileText, Target,
  Activity, Clock, User, MapPin, Building2, Tag, Hash,
} from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Skeleton } from '@components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@components/ui/tabs'
import { Progress } from '@components/ui/progress'
import { assetService } from '@services/assetService'
import type { AssetRelationshipItem, AssetHistoryItem } from '@typings/asset'

const ASSET_TYPE_ICONS: Record<string, React.ElementType> = {
  server: Server, linux_server: Server, windows_server: Server,
  cloud_vm: Cloud, container: Container, kubernetes_node: Container,
  workstation: Monitor, laptop: Monitor, mobile_device: Monitor,
  firewall: Shield, router: Globe, switch: Wifi,
  database: Database, application: HardDrive, web_server: Server,
  iot_device: Wifi, virtual_machine: Server,
}

const CRITICALITY_STYLES: Record<string, string> = {
  critical: 'text-red-400 bg-red-500/10 border-red-500/20',
  high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
}

const STATUS_STYLES: Record<string, string> = {
  online: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  offline: 'text-red-400 bg-red-500/10 border-red-500/20',
  maintenance: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  unknown: 'text-gray-400 bg-gray-500/10 border-gray-500/20',
}

function timeAgo(ts: string | null): string {
  if (!ts) return 'Never'
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

function getRiskColor(score: number): string {
  if (score >= 70) return 'text-red-400'
  if (score >= 50) return 'text-orange-400'
  if (score >= 30) return 'text-yellow-400'
  return 'text-emerald-400'
}

function getRiskBarColor(score: number): string {
  if (score >= 70) return 'bg-red-500'
  if (score >= 50) return 'bg-orange-500'
  if (score >= 30) return 'bg-yellow-500'
  return 'bg-emerald-500'
}

function InfoRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | null }) {
  return (
    <div className="flex items-center gap-3 py-2">
      <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
      <span className="text-xs text-muted-foreground w-24">{label}</span>
      <span className="text-sm font-medium">{value || '-'}</span>
    </div>
  )
}

interface SectionProps { title: string; icon: React.ElementType; children: React.ReactNode }

function Section({ title, icon: Icon, children }: SectionProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Icon className="h-4 w-4 text-[#00F5FF]" /> {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

function RelationshipGraph({ relationships }: { relationships: AssetRelationshipItem[] }) {
  if (relationships.length === 0) {
    return <p className="text-sm text-muted-foreground py-4 text-center">No relationships defined</p>
  }
  return (
    <div className="space-y-2">
      {relationships.map((rel) => (
        <div key={rel.id} className="flex items-center gap-3 p-2 rounded-lg border border-border/50 bg-card/50">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{rel.target.hostname || rel.target.id.slice(0, 8)}</p>
            <p className="text-xs text-muted-foreground">{rel.relationship_type} ({rel.direction})</p>
          </div>
          <Badge variant="outline" className="text-[10px]">{rel.target.asset_type || 'unknown'}</Badge>
        </div>
      ))}
    </div>
  )
}

export default function AssetDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')

  const assetQuery = useQuery({
    queryKey: ['asset', id],
    queryFn: () => assetService.getAsset(id!),
    enabled: !!id,
    refetchInterval: 15000,
  })

  const incidentsQuery = useQuery({
    queryKey: ['asset-incidents', id],
    queryFn: () => assetService.getAssetIncidents(id!),
    enabled: activeTab === 'incidents' || activeTab === 'overview',
  })

  const alertsQuery = useQuery({
    queryKey: ['asset-alerts', id],
    queryFn: () => assetService.getAssetAlerts(id!),
    enabled: activeTab === 'alerts' || activeTab === 'overview',
  })

  const iocsQuery = useQuery({
    queryKey: ['asset-iocs', id],
    queryFn: () => assetService.getAssetIocs(id!),
    enabled: activeTab === 'ioc',
  })

  const threatIntelQuery = useQuery({
    queryKey: ['asset-threat-intel', id],
    queryFn: () => assetService.getAssetThreatIntel(id!),
    enabled: activeTab === 'threat-intel',
  })

  const aiReportsQuery = useQuery({
    queryKey: ['asset-ai-reports', id],
    queryFn: () => assetService.getAssetAiReports(id!),
    enabled: activeTab === 'ai',
  })

  const asset = assetQuery.data
  const risk = asset?.risk_details
  const TypeIcon = asset ? ASSET_TYPE_ICONS[asset.asset_type] || Server : Server

  if (assetQuery.isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (!asset) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <Server className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-20" />
          <h2 className="text-xl font-bold">Asset Not Found</h2>
          <p className="text-sm text-muted-foreground mt-2">The asset you're looking for doesn't exist.</p>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/assets')}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Assets
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={asset.hostname}
        description={`${asset.asset_type.replace(/_/g, ' ')} · ${asset.ip_address || 'No IP'}`}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => assetQuery.refetch()}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate(`/assets/${id}/edit`)}>
              <Edit3 className="mr-2 h-4 w-4" /> Edit
            </Button>
            <Button variant="outline" size="sm" className="text-red-400" onClick={() => { assetService.deleteAsset(id!); navigate('/assets') }}>
              <Trash2 className="mr-2 h-4 w-4" /> Delete
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate('/assets')}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col items-center text-center mb-4">
                <div className="h-16 w-16 rounded-xl bg-[#00F5FF]/10 flex items-center justify-center mb-3">
                  <TypeIcon className="h-8 w-8 text-[#00F5FF]" />
                </div>
                <h2 className="text-lg font-bold">{asset.hostname}</h2>
                <p className="text-xs text-muted-foreground">{asset.ip_address || 'No IP'}</p>
                <div className="flex gap-2 mt-2">
                  <Badge variant="outline" className={`text-[10px] ${CRITICALITY_STYLES[asset.criticality] || ''}`}>
                    {asset.criticality}
                  </Badge>
                  <Badge variant="outline" className={`text-[10px] ${STATUS_STYLES[asset.status] || ''}`}>
                    {asset.status}
                  </Badge>
                </div>
              </div>

              <div className="space-y-1">
                <InfoRow icon={Tag} label="Type" value={asset.asset_type.replace(/_/g, ' ')} />
                <InfoRow icon={Globe} label="MAC" value={asset.mac_address} />
                <InfoRow icon={Monitor} label="OS" value={asset.os ? `${asset.os} ${asset.os_version || ''}` : null} />
                <InfoRow icon={Building2} label="Dept" value={asset.department} />
                <InfoRow icon={User} label="Owner" value={asset.owner} />
                <InfoRow icon={MapPin} label="Location" value={asset.location} />
                <InfoRow icon={Building2} label="Environment" value={asset.environment} />
                <InfoRow icon={Hash} label="Serial" value={asset.serial_number} />
                <InfoRow icon={Building2} label="Vendor" value={asset.vendor} />
                <InfoRow icon={Activity} label="Discovery" value={asset.discovery_source} />
                <InfoRow icon={Clock} label="Last Seen" value={timeAgo(asset.last_seen)} />
              </div>

              {asset.tags && asset.tags.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border/50">
                  <p className="text-xs text-muted-foreground mb-2">Tags</p>
                  <div className="flex flex-wrap gap-1">
                    {asset.tags.map((tag, i) => (
                      <Badge key={i} variant="secondary" className="text-[10px]">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {risk && (
            <Card>
              <CardContent className="p-6">
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Target className="h-4 w-4 text-[#00F5FF]" /> Risk Score
                </h3>
                <div className="text-center mb-4">
                  <span className={`text-4xl font-bold ${getRiskColor(risk.risk_score)}`}>
                    {risk.risk_score.toFixed(0)}
                  </span>
                  <p className="text-xs text-muted-foreground mt-1">out of 100</p>
                </div>
                <Progress value={risk.risk_score} className={`h-2 ${getRiskBarColor(risk.risk_score)}`} />
                <div className="mt-4 space-y-2 text-xs">
                  <div className="flex justify-between"><span>Open Incidents</span><span className="font-mono">{risk.open_incidents}</span></div>
                  <div className="flex justify-between"><span>Critical Alerts</span><span className="font-mono">{risk.critical_alerts}</span></div>
                  <div className="flex justify-between"><span>Threat Intel Matches</span><span className="font-mono">{risk.threat_intel_matches}</span></div>
                  <div className="flex justify-between"><span>CVEs</span><span className="font-mono">{risk.cve_count}</span></div>
                  <div className="flex justify-between"><span>Exposure</span><span className="font-mono">{(risk.exposure_score * 100).toFixed(0)}%</span></div>
                </div>
              </CardContent>
            </Card>
          )}

          <Section title="Counts" icon={Activity}>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-3 rounded-lg bg-card/50 border border-border/50">
                <p className="text-lg font-bold text-[#00F5FF]">{asset.incident_count}</p>
                <p className="text-[10px] text-muted-foreground">Incidents</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-card/50 border border-border/50">
                <p className="text-lg font-bold text-orange-400">{asset.alert_count}</p>
                <p className="text-[10px] text-muted-foreground">Alerts</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-card/50 border border-border/50">
                <p className="text-lg font-bold text-purple-400">{asset.ioc_count}</p>
                <p className="text-[10px] text-muted-foreground">IOCs</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-card/50 border border-border/50">
                <p className="text-lg font-bold text-red-400">{asset.threat_intel_count}</p>
                <p className="text-[10px] text-muted-foreground">Threat Intel</p>
              </div>
            </div>
          </Section>
        </div>

        <div className="lg:col-span-3 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid grid-cols-7 w-full">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="incidents">Incidents</TabsTrigger>
              <TabsTrigger value="alerts">Alerts</TabsTrigger>
              <TabsTrigger value="ioc">IOCs</TabsTrigger>
              <TabsTrigger value="threat-intel">Threat Intel</TabsTrigger>
              <TabsTrigger value="ai">AI Reports</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6 mt-6">
              <Section title="Relationships" icon={Globe}>
                <RelationshipGraph relationships={asset.relationships || []} />
              </Section>

              <Section title="Notes" icon={FileText}>
                <p className="text-sm text-muted-foreground">{asset.notes || 'No notes'}</p>
              </Section>

              {alertsQuery.data && alertsQuery.data.length > 0 && (
                <Section title="Recent Alerts" icon={AlertTriangle}>
                  <div className="space-y-2">
                    {alertsQuery.data.slice(0, 5).map((alert: any) => (
                      <div key={alert.id} className="flex items-center justify-between p-2 rounded-lg border border-border/50 bg-card/50">
                        <div>
                          <p className="text-sm font-medium">{alert.title}</p>
                          <p className="text-xs text-muted-foreground">{alert.severity} · {new Date(alert.created_at).toLocaleDateString()}</p>
                        </div>
                        <Badge variant="outline" className={`text-[10px] ${CRITICALITY_STYLES[alert.severity] || ''}`}>
                          {alert.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Section>
              )}

              {incidentsQuery.data && incidentsQuery.data.length > 0 && (
                <Section title="Recent Incidents" icon={Siren}>
                  <div className="space-y-2">
                    {incidentsQuery.data.slice(0, 5).map((inc: any) => (
                      <div key={inc.id} className="flex items-center justify-between p-2 rounded-lg border border-border/50 bg-card/50 cursor-pointer"
                        onClick={() => navigate(`/incidents/${inc.id}`)}>
                        <div>
                          <p className="text-sm font-medium">{inc.title}</p>
                          <p className="text-xs text-muted-foreground">{inc.status} · {new Date(inc.created_at).toLocaleDateString()}</p>
                        </div>
                        <Badge variant="outline" className={`text-[10px] ${CRITICALITY_STYLES[inc.severity] || ''}`}>
                          {inc.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Section>
              )}
            </TabsContent>

            <TabsContent value="incidents" className="mt-6">
              <Section title="Related Incidents" icon={Siren}>
                {incidentsQuery.isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : !incidentsQuery.data || incidentsQuery.data.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No related incidents</p>
                ) : (
                  <div className="space-y-2">
                    {incidentsQuery.data.map((inc: any) => (
                      <div key={inc.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card/50 cursor-pointer hover:bg-card transition-colors"
                        onClick={() => navigate(`/incidents/${inc.id}`)}>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{inc.title}</p>
                          <p className="text-xs text-muted-foreground">{inc.status} · {new Date(inc.created_at).toLocaleDateString()}</p>
                        </div>
                        <Badge variant="outline" className={`text-[10px] ml-2 ${CRITICALITY_STYLES[inc.severity] || ''}`}>
                          {inc.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            </TabsContent>

            <TabsContent value="alerts" className="mt-6">
              <Section title="Related Alerts" icon={AlertTriangle}>
                {alertsQuery.isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : !alertsQuery.data || alertsQuery.data.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No related alerts</p>
                ) : (
                  <div className="space-y-2">
                    {alertsQuery.data.map((alert: any) => (
                      <div key={alert.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card/50">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{alert.title}</p>
                          <p className="text-xs text-muted-foreground">{alert.source_ip || ''} · {new Date(alert.created_at).toLocaleDateString()}</p>
                        </div>
                        <Badge variant="outline" className={`text-[10px] ml-2 ${CRITICALITY_STYLES[alert.severity] || ''}`}>
                          {alert.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            </TabsContent>

            <TabsContent value="ioc" className="mt-6">
              <Section title="Related IOCs" icon={Target}>
                {iocsQuery.isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : !iocsQuery.data || iocsQuery.data.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No related IOCs</p>
                ) : (
                  <div className="space-y-2">
                    {iocsQuery.data.map((ioc: any) => (
                      <div key={ioc.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card/50">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{ioc.ioc_value}</p>
                          <p className="text-xs text-muted-foreground">{ioc.ioc_type} · {ioc.severity || 'unknown'}</p>
                        </div>
                        <Badge variant="outline" className="text-[10px] ml-2">{ioc.ioc_type}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            </TabsContent>

            <TabsContent value="threat-intel" className="mt-6">
              <Section title="Threat Intelligence Matches" icon={Shield}>
                {threatIntelQuery.isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : !threatIntelQuery.data || threatIntelQuery.data.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No threat intelligence matches</p>
                ) : (
                  <div className="space-y-2">
                    {threatIntelQuery.data.map((ti: any) => (
                      <div key={ti.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card/50">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{ti.ioc_value}</p>
                          <p className="text-xs text-muted-foreground">{ti.ioc_type} · {ti.is_malicious ? 'Malicious' : 'Benign'}</p>
                        </div>
                        <Badge variant="outline" className={`text-[10px] ml-2 ${ti.is_malicious ? 'text-red-400 bg-red-500/10 border-red-500/20' : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'}`}>
                          {ti.reputation_score?.toFixed(0) || 'N/A'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            </TabsContent>

            <TabsContent value="ai" className="mt-6">
              <Section title="AI Investigation Reports" icon={Brain}>
                {aiReportsQuery.isLoading ? (
                  <Skeleton className="h-32 w-full" />
                ) : !aiReportsQuery.data || aiReportsQuery.data.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No AI investigation reports</p>
                ) : (
                  <div className="space-y-2">
                    {aiReportsQuery.data.map((report: any) => (
                      <div key={report.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-card/50 cursor-pointer"
                        onClick={() => navigate(`/ai`)}>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{report.summary?.slice(0, 100) || 'AI Report'}</p>
                          <p className="text-xs text-muted-foreground">Confidence: {report.confidence_score?.toFixed(1) || 'N/A'} · {new Date(report.created_at).toLocaleDateString()}</p>
                        </div>
                        <Badge variant="outline" className="text-[10px] ml-2">
                          {report.confidence_score ? `${report.confidence_score.toFixed(0)}%` : 'N/A'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            </TabsContent>

            <TabsContent value="history" className="mt-6">
              <Section title="Change History" icon={Activity}>
                {!asset.history || asset.history.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No change history</p>
                ) : (
                  <div className="space-y-2">
                    {asset.history.map((h: AssetHistoryItem) => (
                      <div key={h.id} className="flex items-start gap-3 p-3 rounded-lg border border-border/50 bg-card/50">
                        <Activity className="h-4 w-4 text-muted-foreground mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium">{h.field_name.replace(/_/g, ' ')}</p>
                          <p className="text-xs text-muted-foreground">
                            {h.old_value || '(empty)'} → {h.new_value || '(empty)'}
                          </p>
                          <p className="text-[10px] text-muted-foreground mt-0.5">
                            {h.changed_by || 'system'} · {new Date(h.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Section>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
