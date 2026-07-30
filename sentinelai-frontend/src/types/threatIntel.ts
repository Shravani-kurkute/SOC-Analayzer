export interface ThreatIntelResult {
  id: string;
  ioc_type: string;
  ioc_value: string;
  normalized_value: string;
  reputation_score: number;
  confidence: number;
  is_malicious: boolean;
  malicious_count: number;
  harmless_count: number;
  suspicious_count: number;
  country: string | null;
  asn: string | null;
  asn_org: string | null;
  tags: string[] | null;
  first_seen: string | null;
  last_seen: string | null;
  last_analysis: string | null;
  cached: boolean;
  providers: ThreatIntelProviderResult[];
}

export interface ThreatIntelProviderResult {
  name: string;
  reputation: string | null;
  confidence: number;
  malicious: boolean;
  categories: Record<string, string> | null;
  looked_up_at: string;
}

export interface ThreatIntelListEntry {
  id: string;
  ioc_type: string;
  ioc_value: string;
  normalized_value: string;
  reputation_score: number;
  is_malicious: boolean;
  malicious_count: number;
  country: string | null;
  asn: string | null;
  last_analysis: string | null;
  tags: string[] | null;
}

export interface ThreatIntelStats {
  total_iocs: number;
  malicious_count: number;
  harmless_count: number;
  by_type: Record<string, number>;
  provider_stats: Record<string, number>;
  recent_lookups: Array<{
    id: string;
    ioc_type: string;
    ioc_value: string;
    is_malicious: boolean;
    reputation_score: number;
  }>;
}
