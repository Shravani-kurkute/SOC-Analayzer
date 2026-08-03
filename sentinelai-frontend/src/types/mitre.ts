export interface MitreTechnique {
  id: string;
  technique_id: string;
  name: string;
  description: string | null;
  tactic: string;
  tactic_id: string | null;
  platform: string[] | null;
  permissions_required: string[] | null;
  detection: string | null;
  is_subtechnique: boolean;
  parent_technique_id: string | null;
  severity: string;
  score: number;
  mitre_version: string;
  detection_rules: string[] | null;
  ioc_indicators: string[] | null;
  kill_chain_phase: string | null;
  data_sources: string[] | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface MitreMapping {
  id: string;
  technique_id: string;
  mapped_type: string;
  mapped_id: string;
  mapped_name: string | null;
  confidence: number;
  source: string;
  context: string | null;
  mapped_at: string;
  created_at: string;
}

export interface CoverageStatistic {
  tactic: string;
  total_techniques: number;
  mapped_techniques: number;
  coverage_percent: number;
  total_detections: number;
  mapped_detections: number;
  avg_confidence: number;
  calculated_at: string;
}

export interface MitreCoverage {
  overall_coverage: number;
  total_techniques: number;
  total_mapped: number;
  total_detections: number;
  by_tactic: CoverageStatistic[];
  top_techniques: { technique_id: string; name: string; count: number }[];
  top_tactics: CoverageStatistic[];
  most_triggered: { technique_id: string; name: string; tactic: string; count: number }[];
}

export interface MitreTechniqueDetail {
  technique: MitreTechnique;
  mappings: MitreMapping[];
  mapped_count: number;
  detection_coverage: number;
  related_techniques: MitreTechnique[];
}

export const TACTIC_COLORS: Record<string, string> = {
  'Initial Access': '#ef4444',
  Execution: '#f97316',
  Persistence: '#eab308',
  'Privilege Escalation': '#22c55e',
  'Defense Evasion': '#14b8a6',
  'Credential Access': '#3b82f6',
  Discovery: '#6366f1',
  'Lateral Movement': '#8b5cf6',
  Collection: '#ec4899',
  'Command and Control': '#f43f5e',
  Exfiltration: '#a855f7',
  Impact: '#dc2626',
};

export const MITRE_SEVERITY_COLORS: Record<string, string> = {
  critical: 'text-red-400 bg-red-400/10 border-red-400/30',
  high: 'text-orange-400 bg-orange-400/10 border-orange-400/30',
  medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
  low: 'text-green-400 bg-green-400/10 border-green-400/30',
};
