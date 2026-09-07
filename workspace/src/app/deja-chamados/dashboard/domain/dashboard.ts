/*
 * Deja Chamados
 *
 * Dashboard Domain
 *
 * Contratos principais para os indicadores e listagens
 * apresentados no Dashboard de Chamados.
 */

export interface DashboardSummaryItem {
  title: string;
  value: number;
  icon: string;
  description: string;
  suffix?: string;
}

export interface DashboardTicket {
  id: string;
  title: string;
  clientName: string;
  status: string;
  priority: string;
  updatedAt: string;
}

export interface DashboardData {
  summary: DashboardSummaryItem[];
  latestTickets: DashboardTicket[];
}

export interface DashboardSlaChartItem {
  label: string;
  total: number;
  withinSla: number;
  expiredSla: number;
  complied: number;
  violated: number;
  compliedPercentage: number;
  violatedPercentage: number;
}

export interface DashboardSlaMonthlyTrend {
  month: string;
  opened: number;
  closed: number;
  complied: number;
  violated: number;
}

export interface DashboardSlaData {
  byPriority: DashboardSlaChartItem[];
  byResponsible: DashboardSlaChartItem[];
  monthlyTrend: DashboardSlaMonthlyTrend[];
}