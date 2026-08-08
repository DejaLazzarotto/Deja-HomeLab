/*
 * Deja Workspace Angular Integration
 *
 * Workspace KPI Card Component
 *
 * Componente institucional reutilizável responsável pela
 * apresentação resumida de indicadores e métricas dentro
 * dos Widgets da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

@Component({
  selector: 'deja-kpi-card',
  standalone: true,
  templateUrl: './workspace-kpi-card.html',
  styleUrl: './workspace-kpi-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceKpiCardComponent {

  @Input()
  label = '';

  @Input()
  value = '';

  @Input()
  description = '';

}