export interface IocEntry {
  id: string;
  ioc_type: string;
  ioc_value: string;
  normalized_value: string;
  confidence: number;
  source_event: string | null;
  source_log: string | null;
  source_ip: string | null;
  first_seen: string;
  last_seen: string;
  occurrences: number;
  severity: string;
  status: string;
  tags: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  source_ids: string[] | null;
  context: string | null;
  kill_chain_phase: string | null;
  created_at: string;
  updated_at: string;
}

export interface IocStats {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  top_source_ips: { source_ip: string; count: number }[];
  latest_iocs: { id: string; ioc_type: string; ioc_value: string; severity: string; last_seen: string }[];
  unique_domains: number;
  unique_ips: number;
  unique_hashes: number;
}

export interface IocExtractResult {
  extracted: number;
  new: number;
  updated: number;
  iocs: IocEntry[];
}

export const IOC_TYPE_MAP: Record<string, { label: string; color: string }> = {
  ipv4: { label: 'IPv4', color: '#3b82f6' },
  ipv6: { label: 'IPv6', color: '#6366f1' },
  domain: { label: 'Domain', color: '#10b981' },
  url: { label: 'URL', color: '#f59e0b' },
  hostname: { label: 'Hostname', color: '#14b8a6' },
  email: { label: 'Email', color: '#8b5cf6' },
  username: { label: 'Username', color: '#ec4899' },
  md5: { label: 'MD5', color: '#ef4444' },
  sha1: { label: 'SHA1', color: '#f97316' },
  sha256: { label: 'SHA256', color: '#dc2626' },
  registry_key: { label: 'Registry Key', color: '#06b6d4' },
  windows_sid: { label: 'Windows SID', color: '#84cc16' },
  process_name: { label: 'Process', color: '#22c55e' },
  executable_path: { label: 'Executable Path', color: '#eab308' },
  command_line: { label: 'Command Line', color: '#a855f7' },
  cve: { label: 'CVE', color: '#b91c1c' },
  mitre_technique: { label: 'MITRE Technique', color: '#7c3aed' },
  port: { label: 'Port', color: '#0ea5e9' },
  protocol: { label: 'Protocol', color: '#2dd4bf' },
};

export const IOC_SEVERITY_COLORS: Record<string, string> = {
  critical: 'text-red-400 bg-red-400/10 border-red-400/30',
  high: 'text-orange-400 bg-orange-400/10 border-orange-400/30',
  medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
  low: 'text-green-400 bg-green-400/10 border-green-400/30',
};
