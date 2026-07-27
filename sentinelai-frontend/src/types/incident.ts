export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'contained' | 'eradiated' | 'recovered' | 'closed';
  category: string;
  alertIds: string[];
  assetIds: string[];
  assignee: string | null;
  createdAt: string;
  updatedAt: string;
  closedAt: string | null;
  timeline: TimelineEntry[];
  notes: IncidentNote[];
}

export interface TimelineEntry {
  id: string;
  timestamp: string;
  action: string;
  actor: string;
  details: string;
}

export interface IncidentNote {
  id: string;
  content: string;
  author: string;
  createdAt: string;
  isPrivate: boolean;
}

export interface IncidentFilter {
  severity?: string[];
  status?: string[];
  assignee?: string[];
  dateRange?: { start: string; end: string } | null;
  search?: string;
}
