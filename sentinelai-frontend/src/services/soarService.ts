import api from './api';
import type {
  ApiResponse, Playbook, PlaybookListItem, PlaybookExecution,
  PlaybookExecutionLog, ApprovalRequest, PlaybookStats,
  ActionDefinition, TemplateDefinition, ExecuteResponse,
  PaginatedData,
} from '@typings/soar';

export const soarService = {
  async getPlaybooks(params?: Record<string, any>): Promise<ApiResponse<PaginatedData<PlaybookListItem>>> {
    const response = await api.get('/playbooks', { params });
    return response.data;
  },

  async getPlaybook(id: string): Promise<Playbook> {
    const response = await api.get(`/playbooks/${id}`);
    return (response.data as ApiResponse<Playbook>).data;
  },

  async createPlaybook(data: Partial<Playbook>): Promise<Playbook> {
    const response = await api.post('/playbooks', data);
    return (response.data as ApiResponse<Playbook>).data;
  },

  async updatePlaybook(id: string, data: Partial<Playbook>): Promise<Playbook> {
    const response = await api.put(`/playbooks/${id}`, data);
    return (response.data as ApiResponse<Playbook>).data;
  },

  async deletePlaybook(id: string): Promise<void> {
    await api.delete(`/playbooks/${id}`);
  },

  async executePlaybook(id: string, incidentId?: string): Promise<ExecuteResponse> {
    const params: Record<string, any> = {};
    if (incidentId) params.incident_id = incidentId;
    const response = await api.post(`/playbooks/${id}/execute`, null, { params });
    return (response.data as ApiResponse<ExecuteResponse>).data;
  },

  async retryPlaybook(id: string, incidentId?: string): Promise<ExecuteResponse> {
    const params: Record<string, any> = {};
    if (incidentId) params.incident_id = incidentId;
    const response = await api.post(`/playbooks/${id}/retry`, null, { params });
    return (response.data as ApiResponse<ExecuteResponse>).data;
  },

  async getExecutions(params?: Record<string, any>): Promise<ApiResponse<PaginatedData<PlaybookExecution>>> {
    const response = await api.get('/playbooks/executions', { params });
    return response.data;
  },

  async getExecution(id: string): Promise<PlaybookExecution> {
    const response = await api.get(`/playbooks/executions/${id}`);
    return (response.data as ApiResponse<PlaybookExecution>).data;
  },

  async getExecutionLogs(id: string): Promise<PlaybookExecutionLog[]> {
    const response = await api.get(`/playbooks/executions/${id}/logs`);
    return (response.data as ApiResponse<PlaybookExecutionLog[]>).data;
  },

  async getStats(): Promise<PlaybookStats> {
    const response = await api.get('/playbooks/stats');
    return (response.data as ApiResponse<PlaybookStats>).data;
  },

  async getActions(): Promise<ActionDefinition[]> {
    const response = await api.get('/playbooks/actions');
    return (response.data as ApiResponse<ActionDefinition[]>).data;
  },

  async getTemplates(): Promise<TemplateDefinition[]> {
    const response = await api.get('/playbooks/templates');
    return (response.data as ApiResponse<TemplateDefinition[]>).data;
  },

  async instantiateTemplate(templateType: string, name?: string): Promise<Playbook> {
    const params: Record<string, any> = {};
    if (name) params.name = name;
    const response = await api.post(`/playbooks/templates/${templateType}/instantiate`, null, { params });
    return (response.data as ApiResponse<Playbook>).data;
  },

  async getPendingApprovals(params?: Record<string, any>): Promise<ApiResponse<PaginatedData<ApprovalRequest>>> {
    const response = await api.get('/playbooks/approvals/pending', { params });
    return response.data;
  },

  async resolveApproval(id: string, approve: boolean, reason?: string): Promise<ApprovalRequest> {
    const response = await api.post(`/playbooks/approvals/${id}/resolve`, { approve, reason });
    return (response.data as ApiResponse<ApprovalRequest>).data;
  },
};
