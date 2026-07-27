export interface Asset {
  id: string;
  hostname: string;
  ipAddress: string;
  macAddress: string | null;
  os: string;
  osVersion: string;
  type: 'server' | 'workstation' | 'network' | 'cloud' | 'container' | 'iot';
  criticality: 'critical' | 'high' | 'medium' | 'low';
  status: 'online' | 'offline' | 'maintenance' | 'unknown';
  tags: string[];
  vulnerabilities: number;
  openPorts: number;
  lastSeen: string;
  createdAt: string;
  location: string | null;
  department: string | null;
  owner: string | null;
  notes: string;
}

export interface AssetFilter {
  type?: string[];
  status?: string[];
  criticality?: string[];
  search?: string;
  tags?: string[];
}
