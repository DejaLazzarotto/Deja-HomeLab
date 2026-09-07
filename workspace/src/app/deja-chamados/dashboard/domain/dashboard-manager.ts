/*
 * Deja Chamados
 *
 * Dashboard Domain
 *
 * Contratos gerenciais usados pelos indicadores analíticos
 * do Dashboard de Chamados.
 */

export interface DashboardTopClient {
  clientId: string;
  clientName: string;
  totalTickets: number;
}

export interface DashboardOldestTicket {
  ticketId: string;
  title: string;
  clientName: string;
  createdAt: string;
  daysOpen: number;
}

export interface DashboardAverageResolutionTime {
  totalClosedTickets: number;
  averageHours: number;
  averageDays: number;
  formattedValue: string;
}

export interface DashboardMttr {
  totalClosedTickets: number;
  averageHours: number;
  averageDays: number;
  formattedValue: string;
}

export interface DashboardResponsibleMttr {
  assignedTo: string;
  totalClosedTickets: number;
  averageHours: number;
  averageDays: number;
  formattedValue: string;
}

export interface DashboardReopenRate {
  reopenedTickets: number;
  totalClosedTickets: number;
  percentage: number;
}

export interface DashboardResponsibleReopenRate {
  assignedTo: string;
  reopenedTickets: number;
  totalClosedTickets: number;
  percentage: number;
}

export interface DashboardBacklog {
  totalTickets: number;
}

export interface DashboardResponsibleBacklog {
  assignedTo: string;
  totalTickets: number;
}

export interface DashboardPriorityBacklog {
  priority: string;
  totalTickets: number;
}

export interface DashboardResponsibleRanking {
  assignedTo: string;
  backlog: number;
  mttr: string;
  reopenRate: number;
}

export interface DashboardManagerMetricData {
  title: string;
  value: string;
  description: string;
  icon: string;
}

export interface DashboardManagerData {
  topClients: DashboardTopClient[];
  oldestOpenTickets: DashboardOldestTicket[];

  averageResolutionTime: DashboardAverageResolutionTime;
  mttr: DashboardMttr;
  responsibleMttr: DashboardResponsibleMttr[];

  reopenRate: DashboardReopenRate;
  responsibleReopenRate: DashboardResponsibleReopenRate[];

  backlog: DashboardBacklog;
  responsibleBacklog: DashboardResponsibleBacklog[];
  priorityBacklog: DashboardPriorityBacklog[];

  responsibleRanking: DashboardResponsibleRanking[];

  metrics: DashboardManagerMetricData[];
  responsibleMetrics: DashboardManagerMetricData[];
  reopenMetrics: DashboardManagerMetricData[];
  backlogMetrics: DashboardManagerMetricData[];
  priorityBacklogMetrics: DashboardManagerMetricData[];
}