/*
 * Deja Workspace Angular Integration
 *
 * Workspace Status Badge Component
 *
 * Badge institucional reutilizável utilizado para representar
 * estados semânticos em Widgets da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

export type WorkspaceStatusBadgeVariant =
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'neutral';

@Component({
  selector: 'deja-status-badge',
  standalone: true,
  templateUrl: './workspace-status-badge.html',
  styleUrl: './workspace-status-badge.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceStatusBadgeComponent {

  @Input()
  label = '';

  @Input()
  variant: WorkspaceStatusBadgeVariant = 'neutral';

}