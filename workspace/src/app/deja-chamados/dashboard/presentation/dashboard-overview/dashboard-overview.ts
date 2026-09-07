/*
 * Deja Chamados
 *
 * Dashboard Presentation
 *
 * Exibe os indicadores operacionais, de SLA e gerenciais
 * consolidados do módulo de Chamados.
 */

import {
  ChangeDetectionStrategy,
  Component,
  input,
} from '@angular/core';

import {
  DashboardData,
  DashboardManagerData,
  DashboardSlaData,
} from '../../domain';

@Component({
  selector: 'deja-dashboard-overview',
  standalone: true,
  templateUrl: './dashboard-overview.html',
  styleUrl: './dashboard-overview.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardOverviewComponent {

  readonly dashboardData =
    input.required<DashboardData>();

  readonly slaData =
    input.required<DashboardSlaData>();

  readonly managerData =
    input.required<DashboardManagerData>();

}