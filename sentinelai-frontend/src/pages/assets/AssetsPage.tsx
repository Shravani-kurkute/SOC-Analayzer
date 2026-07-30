import { useState, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Server, Search, RefreshCw, Plus, ChevronDown, ChevronUp,
  Download, Upload, MoreHorizontal, Globe, Monitor,
  HardDrive, Cloud, Container, Wifi, Database,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent, CardHeader } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Badge } from '@components/ui/badge'
import { Input } from '@components/ui/input'
import { Skeleton } from '@components/ui/skeleton'
import { StatCard } from '@components/common/StatCard'
import { assetService } from '@services/assetService'
import type { AssetListItem } from '@typings/asset'

const ASSET_TYPE_ICONS: Record<string, React.ElementType> = {
  server: Server,
  linux_server: Server,
  windows_server: Server,
  cloud_vm: Cloud,
  container: Container,
  kubernetes_node: Container,
  workstation: Monitor,
  laptop: Monitor,
  mobile_device: Monitor,
  firewall: Shield,
  router: Globe,
  switch: Wifi,
  database: Database,
  application: HardDrive,
  web_server: Server,
  iot_device: Wifi,
  virtual_machine: Server,
}

import { Shield } from 'lucide-react'

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

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

function getRiskLevel(score: number): { label: string; color: string } {
  if (score >= 70) return { label: 'Critical', color: 'text-red-400' }
  if (score >= 50) return { label: 'High', color: 'text-orange-400' }
  if (score >= 30) return { label: 'Medium', color: 'text-yellow-400' }
  return { label: 'Low', color: 'text-emerald-400' }
}

export default function AssetsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterCriticality, setFilterCriticality] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterDepartment, setFilterDepartment] = useState('')
  const [filterRiskLevel, setFilterRiskLevel] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [showImport, setShowImport] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const params: Record<string, any> = { page, page_size: 20, sort_by: sortBy, sort_order: sortOrder }
  if (search) params.search = search
  if (filterType) params.asset_type = filterType
  if (filterCriticality) params.criticality = filterCriticality
  if (filterStatus) params.status = filterStatus
  if (filterDepartment) params.department = filterDepartment
  if (filterRiskLevel) params.risk_level = filterRiskLevel

  const listQuery = useQuery({
    queryKey: ['assets-list', page, search, filterType, filterCriticality, filterStatus, filterDepartment, filterRiskLevel, sortBy, sortOrder],
    queryFn: () => assetService.getAssets(params),
    refetchInterval: 30000,
  })

  const statsQuery = useQuery({
    queryKey: ['assets-stats'],
    queryFn: assetService.getStats,
    refetchInterval: 30000,
  })

  const data = listQuery.data?.data
  const stats = statsQuery.data

  const handleFileImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      if (file.name.endsWith('.csv')) {
        await assetService.importCsv(file)
      } else {
        await assetService.importJson(file)
      }
      listQuery.refetch()
      statsQuery.refetch()
    } catch (err) {
      console.error('Import failed', err)
    }
    setShowImport(false)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Asset Inventory"
        description="Manage and monitor all enterprise assets"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => { listQuery.refetch(); statsQuery.refetch() }}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowImport(!showImport)}>
              <Upload className="mr-2 h-4 w-4" /> Import
            </Button>
            <Button size="sm" onClick={() => navigate('/assets/new')}>
              <Plus className="mr-2 h-4 w-4" /> Add Asset
            </Button>
          </div>
        }
      />

      {showImport && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <p className="text-sm text-muted-foreground">Import assets from CSV or JSON file</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.json"
                onChange={handleFileImport}
                className="hidden"
              />
              <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()}>
                <Download className="mr-2 h-4 w-4" /> Choose File
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
        <StatCard title="Total Assets" value={formatNumber(stats?.total_assets ?? 0)} icon={Server} variant="info" />
        <StatCard title="Healthy" value={formatNumber(stats?.healthy_assets ?? 0)} icon={Server} variant="success" />
        <StatCard title="Critical" value={formatNumber(stats?.critical_assets ?? 0)} icon={Server} variant="danger" />
        <StatCard title="Offline" value={formatNumber(stats?.offline_assets ?? 0)} icon={Server} variant="warning" />
        <StatCard title="High Risk" value={formatNumber(stats?.high_risk_assets ?? 0)} icon={Shield} variant="danger" />
        <StatCard title="Risk Score" value={stats?.risk_distribution ? `${Object.values(stats.risk_distribution).reduce((a, b) => a + b, 0)}` : '0'} icon={Shield} variant="default" />
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search assets..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                  className="pl-9 h-9 w-56"
                />
              </div>
              <select value={filterType} onChange={(e) => { setFilterType(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                <option value="">All Types</option>
                <option value="server">Server</option>
                <option value="linux_server">Linux Server</option>
                <option value="windows_server">Windows Server</option>
                <option value="cloud_vm">Cloud VM</option>
                <option value="container">Container</option>
                <option value="kubernetes_node">K8s Node</option>
                <option value="workstation">Workstation</option>
                <option value="laptop">Laptop</option>
                <option value="mobile_device">Mobile</option>
                <option value="firewall">Firewall</option>
                <option value="router">Router</option>
                <option value="switch">Switch</option>
                <option value="database">Database</option>
                <option value="application">Application</option>
                <option value="web_server">Web Server</option>
                <option value="iot_device">IoT</option>
                <option value="virtual_machine">VM</option>
              </select>
              <select value={filterCriticality} onChange={(e) => { setFilterCriticality(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                <option value="">All Criticality</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <select value={filterStatus} onChange={(e) => { setFilterStatus(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                <option value="">All Status</option>
                <option value="online">Online</option>
                <option value="offline">Offline</option>
                <option value="maintenance">Maintenance</option>
                <option value="unknown">Unknown</option>
              </select>
              <select value={filterRiskLevel} onChange={(e) => { setFilterRiskLevel(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                <option value="">All Risk</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <select value={filterDepartment} onChange={(e) => { setFilterDepartment(e.target.value); setPage(1) }}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                <option value="">All Dept</option>
                <option value="Engineering">Engineering</option>
                <option value="IT">IT</option>
                <option value="Security">Security</option>
                <option value="Finance">Finance</option>
                <option value="HR">HR</option>
                <option value="Operations">Operations</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
                className="h-9 rounded-lg border border-border bg-background px-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                <option value="created_at">Created</option>
                <option value="hostname">Hostname</option>
                <option value="risk_score">Risk Score</option>
                <option value="asset_type">Type</option>
                <option value="criticality">Criticality</option>
                <option value="status">Status</option>
                <option value="last_seen">Last Seen</option>
              </select>
              <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="h-9 px-2 rounded-lg border border-border bg-background hover:bg-accent transition-colors">
                {sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {listQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : !data || data.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Server className="h-12 w-12 mb-3 opacity-20" />
              <p className="text-sm font-medium">No assets found</p>
              <p className="text-xs mt-1">Add assets manually or import them via CSV/JSON.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-muted-foreground">
                      <th className="pb-2.5 font-medium pr-3">Hostname</th>
                      <th className="pb-2.5 font-medium pr-3">Type</th>
                      <th className="pb-2.5 font-medium pr-3">IP Address</th>
                      <th className="pb-2.5 font-medium pr-3">OS</th>
                      <th className="pb-2.5 font-medium pr-3">Criticality</th>
                      <th className="pb-2.5 font-medium pr-3">Status</th>
                      <th className="pb-2.5 font-medium pr-3">Risk</th>
                      <th className="pb-2.5 font-medium pr-3">Dept</th>
                      <th className="pb-2.5 font-medium pr-3">Owner</th>
                      <th className="pb-2.5 font-medium pr-3">Last Seen</th>
                      <th className="pb-2.5 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((asset: AssetListItem) => {
                      const risk = getRiskLevel(asset.risk_score)
                      const TypeIcon = ASSET_TYPE_ICONS[asset.asset_type] || Server
                      return (
                        <tr
                          key={asset.id}
                          className="border-b border-border/50 hover:bg-card/50 transition-colors cursor-pointer"
                          onClick={() => navigate(`/assets/${asset.id}`)}
                        >
                          <td className="py-3 pr-3">
                            <div className="flex items-center gap-2">
                              <TypeIcon className="h-4 w-4 text-muted-foreground" />
                              <span className="font-medium text-foreground text-sm">{asset.hostname}</span>
                            </div>
                          </td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{asset.asset_type.replace(/_/g, ' ')}</td>
                          <td className="py-3 pr-3 text-xs font-mono text-muted-foreground">{asset.ip_address || '-'}</td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{asset.os || '-'}</td>
                          <td className="py-3 pr-3">
                            <Badge variant="outline" className={`text-[10px] h-4 px-1 ${CRITICALITY_STYLES[asset.criticality] || ''}`}>
                              {asset.criticality}
                            </Badge>
                          </td>
                          <td className="py-3 pr-3">
                            <Badge variant="outline" className={`text-[10px] h-4 px-1 ${STATUS_STYLES[asset.status] || ''}`}>
                              {asset.status}
                            </Badge>
                          </td>
                          <td className="py-3 pr-3">
                            <span className={`text-xs font-mono font-medium ${risk.color}`}>
                              {asset.risk_score.toFixed(1)}
                            </span>
                          </td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{asset.department || '-'}</td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{asset.owner || '-'}</td>
                          <td className="py-3 pr-3 text-xs text-muted-foreground">{timeAgo(asset.last_seen)}</td>
                          <td className="py-3">
                            <Button variant="ghost" size="icon-sm" onClick={(e) => { e.stopPropagation(); navigate(`/assets/${asset.id}`) }}>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              {data.total_pages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <span className="text-xs text-muted-foreground">Page {page} of {data.total_pages}</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Previous</Button>
                    <Button variant="outline" size="sm" disabled={page >= data.total_pages} onClick={() => setPage(p => p + 1)}>Next</Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
