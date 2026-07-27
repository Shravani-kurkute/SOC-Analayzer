export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'informational';
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved' | 'false_positive';
  source: string;
  sourceIp: string;
  destinationIp: string;
  mitreTechniqueId: string | null;
  mitreTactic: string | null;
  ruleId: string;
  ruleName: string;
  rawData: Record<string, unknown>;
  enrichedData: Record<string, unknown> | null;
  assetIds: string[];
  tags: string[];
  score: number;
  createdAt: string;
  updatedAt: string;
  acknowledgedBy: string | null;
  acknowledgedAt: string | null;
  resolvedBy: string | null;
  resolvedAt: string | null;
  incidentId: string | null;
}

export interface AlertFilter {
  severity: string[];
  status: string[];
  source: string[];
  dateRange: { start: string; end: string } | null;
  search: string;
}

export interface AlertStats {
  total: number;
  bySeverity: Record<string, number>;
  byStatus: Record<string, number>;
  bySource: Record<string, number>;
  trending: { date: string; count: number }[];
  avgResponseTime: number;
  avgResolutionTime: number;
}
