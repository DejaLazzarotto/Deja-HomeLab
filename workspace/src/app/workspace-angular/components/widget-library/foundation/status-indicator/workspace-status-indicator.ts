/*
 * Deja Workspace Angular Integration
 *
 * Workspace Status Indicator Foundation Component
 *
 * Indicador visual semântico reutilizável da Deja UI Foundation.
 *
 * Responsável exclusivamente por representar visualmente um estado
 * através de cor, tamanho e animação.
 *
 * O componente não possui conhecimento sobre Widgets, Dashboards,
 * Runtime, dados ou regras de negócio.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

export type WorkspaceStatusIndicatorStatus =
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'neutral';

export type WorkspaceStatusIndicatorSize =
  | 'sm'
  | 'md'
  | 'lg';

@Component({
  selector: 'deja-status-indicator',
  standalone: true,
  templateUrl: './workspace-status-indicator.html',
  styleUrl: './workspace-status-indicator.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceStatusIndicatorComponent {

  @Input()
  status: WorkspaceStatusIndicatorStatus = 'neutral';

  @Input()
  size: WorkspaceStatusIndicatorSize = 'md';

  @Input()
  animated = false;

}