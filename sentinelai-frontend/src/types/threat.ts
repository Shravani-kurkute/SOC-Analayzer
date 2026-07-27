export interface Threat {
  id: string;
  name: string;
  type: 'malware' | 'phishing' | 'ransomware' | 'apt' | 'insider' | 'ddos' | 'vulnerability';
  severity: 'critical' | 'high' | 'medium' | 'low';
  score: number;
  mitreId: string;
  mitreTactic: string;
  mitreTechnique: string;
  indicators: Indicator[];
  affectedAssets: string[];
  firstSeen: string;
  lastSeen: string;
  status: 'active' | 'monitoring' | 'contained' | 'resolved';
  description: string;
  remediation: string;
  references: string[];
}

export interface Indicator {
  id: string;
  type: 'ip' | 'domain' | 'url' | 'hash' | 'email' | 'registry' | 'file';
  value: string;
  confidence: number;
  firstSeen: string;
  lastSeen: string;
  tags: string[];
}

export interface ThreatIntelFeed {
  id: string;
  name: string;
  provider: string;
  type: 'stix' | 'taxii' | 'misp' | 'custom';
  enabled: boolean;
  lastFetch: string | null;
  fetchInterval: number;
}
