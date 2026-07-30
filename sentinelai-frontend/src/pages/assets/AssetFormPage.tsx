import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Save } from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Card, CardContent } from '@components/ui/card'
import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'
import { Label } from '@components/ui/label'
import { Skeleton } from '@components/ui/skeleton'
import { assetService } from '@services/assetService'
import toast from 'react-hot-toast'

const ASSET_TYPES = [
  'server', 'linux_server', 'windows_server', 'cloud_vm', 'container',
  'kubernetes_node', 'workstation', 'laptop', 'mobile_device', 'firewall',
  'router', 'switch', 'database', 'application', 'web_server', 'iot_device',
  'virtual_machine',
]

export default function AssetFormPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEdit = !!id

  const [form, setForm] = useState({
    hostname: '', ip_address: '', mac_address: '', os: '', os_version: '',
    asset_type: 'server', criticality: 'medium', environment: '', status: 'unknown',
    location: '', department: '', owner: '', vendor: '', serial_number: '',
    tags: '', notes: '',
  })

  const existingQuery = useQuery({
    queryKey: ['asset-edit', id],
    queryFn: () => assetService.getAsset(id!),
    enabled: isEdit,
  })

  useEffect(() => {
    if (existingQuery.data) {
      const a = existingQuery.data
      setForm({
        hostname: a.hostname || '',
        ip_address: a.ip_address || '',
        mac_address: a.mac_address || '',
        os: a.os || '',
        os_version: a.os_version || '',
        asset_type: a.asset_type || 'server',
        criticality: a.criticality || 'medium',
        environment: a.environment || '',
        status: a.status || 'unknown',
        location: a.location || '',
        department: a.department || '',
        owner: a.owner || '',
        vendor: a.vendor || '',
        serial_number: a.serial_number || '',
        tags: (a.tags || []).join(', '),
        notes: a.notes || '',
      })
    }
  }, [existingQuery.data])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const data = {
      ...form,
      tags: form.tags ? form.tags.split(',').map(t => t.trim()).filter(Boolean) : [],
    }

    try {
      if (isEdit) {
        await assetService.updateAsset(id!, data)
        toast.success('Asset updated successfully')
        navigate(`/assets/${id}`)
      } else {
        const created = await assetService.createAsset(data)
        toast.success('Asset created successfully')
        navigate(`/assets/${created.id}`)
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.message || 'Failed to save asset')
    }
  }

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(prev => ({ ...prev, [field]: e.target.value }))

  if (isEdit && existingQuery.isLoading) {
    return <div className="space-y-6"><Skeleton className="h-8 w-64" /><Skeleton className="h-96 w-full" /></div>
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title={isEdit ? 'Edit Asset' : 'Add Asset'}
        description={isEdit ? `Editing ${form.hostname}` : 'Create a new asset record'}
        actions={
          <Button variant="outline" size="sm" onClick={() => navigate(isEdit ? `/assets/${id}` : '/assets')}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back
          </Button>
        }
      />

      <form onSubmit={handleSubmit}>
        <Card>
          <CardContent className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>Hostname *</Label>
                <Input value={form.hostname} onChange={set('hostname')} required placeholder="asset-hostname-01" />
              </div>
              <div className="space-y-2">
                <Label>IP Address</Label>
                <Input value={form.ip_address} onChange={set('ip_address')} placeholder="192.168.1.100" />
              </div>
              <div className="space-y-2">
                <Label>MAC Address</Label>
                <Input value={form.mac_address} onChange={set('mac_address')} placeholder="00:1A:2B:3C:4D:5E" />
              </div>
              <div className="space-y-2">
                <Label>Asset Type</Label>
                <select value={form.asset_type} onChange={set('asset_type')}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                  {ASSET_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Criticality</Label>
                <select value={form.criticality} onChange={set('criticality')}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Status</Label>
                <select value={form.status} onChange={set('status')}
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50">
                  <option value="online">Online</option>
                  <option value="offline">Offline</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>OS</Label>
                <Input value={form.os} onChange={set('os')} placeholder="Ubuntu" />
              </div>
              <div className="space-y-2">
                <Label>OS Version</Label>
                <Input value={form.os_version} onChange={set('os_version')} placeholder="22.04" />
              </div>
              <div className="space-y-2">
                <Label>Environment</Label>
                <Input value={form.environment} onChange={set('environment')} placeholder="Production / Staging / Dev" />
              </div>
              <div className="space-y-2">
                <Label>Department</Label>
                <Input value={form.department} onChange={set('department')} placeholder="Engineering" />
              </div>
              <div className="space-y-2">
                <Label>Owner</Label>
                <Input value={form.owner} onChange={set('owner')} placeholder="John Doe" />
              </div>
              <div className="space-y-2">
                <Label>Location</Label>
                <Input value={form.location} onChange={set('location')} placeholder="Data Center A" />
              </div>
              <div className="space-y-2">
                <Label>Vendor</Label>
                <Input value={form.vendor} onChange={set('vendor')} placeholder="Dell" />
              </div>
              <div className="space-y-2">
                <Label>Serial Number</Label>
                <Input value={form.serial_number} onChange={set('serial_number')} placeholder="SN-12345" />
              </div>
              <div className="space-y-2">
                <Label>Tags (comma separated)</Label>
                <Input value={form.tags} onChange={set('tags')} placeholder="web, production, critical" />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Notes</Label>
              <textarea value={form.notes} onChange={set('notes')}
                className="w-full h-24 rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00F5FF]/50 resize-none"
                placeholder="Additional notes..." />
            </div>
            <div className="flex justify-end gap-3 pt-4 border-t border-border/50">
              <Button variant="outline" type="button" onClick={() => navigate(isEdit ? `/assets/${id}` : '/assets')}>Cancel</Button>
              <Button type="submit"><Save className="mr-2 h-4 w-4" /> {isEdit ? 'Update Asset' : 'Create Asset'}</Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
