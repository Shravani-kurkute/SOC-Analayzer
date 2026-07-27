export const SEVERITY_COLORS = {
  critical: 'text-red-500 bg-red-500/10 border-red-500/20',
  high: 'text-orange-500 bg-orange-500/10 border-orange-500/20',
  medium: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
  low: 'text-green-500 bg-green-500/10 border-green-500/20',
  informational: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
} as const;

export const STATUS_COLORS = {
  new: 'text-blue-500 bg-blue-500/10',
  acknowledged: 'text-yellow-500 bg-yellow-500/10',
  investigating: 'text-purple-500 bg-purple-500/10',
  resolved: 'text-green-500 bg-green-500/10',
  false_positive: 'text-gray-500 bg-gray-500/10',
  open: 'text-red-500 bg-red-500/10',
  contained: 'text-orange-500 bg-orange-500/10',
  eradiated: 'text-yellow-500 bg-yellow-500/10',
  recovered: 'text-green-500 bg-green-500/10',
  closed: 'text-gray-500 bg-gray-500/10',
} as const;

export const SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'informational'] as const;

export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100] as const;
export const DEFAULT_PAGE_SIZE = 25;

export const REFRESH_INTERVALS = {
  DASHBOARD: 30000,
  ALERTS: 15000,
  INCIDENTS: 30000,
  THREATS: 60000,
  ASSETS: 60000,
} as const;

export const MITRE_TACTICS = [
  'Reconnaissance',
  'Resource Development',
  'Initial Access',
  'Execution',
  'Persistence',
  'Privilege Escalation',
  'Defense Evasion',
  'Credential Access',
  'Discovery',
  'Lateral Movement',
  'Collection',
  'Command and Control',
  'Exfiltration',
  'Impact',
] as const;

export const ROLES = [
  { value: 'admin', label: 'Administrator' },
  { value: 'analyst', label: 'Security Analyst' },
  { value: 'viewer', label: 'Viewer' },
] as const;
