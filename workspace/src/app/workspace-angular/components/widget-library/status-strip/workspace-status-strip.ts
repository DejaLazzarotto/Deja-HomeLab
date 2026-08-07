/*
 * Deja Workspace Angular Integration
 *
 * Workspace Status Strip Component
 *
 * Componente institucional reutilizável responsável pela
 * apresentação de informações resumidas de contexto e status
 * dentro dos Widgets da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

import {
  WorkspaceStatusBadgeComponent,
} from '../status-badge/workspace-status-badge';

export type WorkspaceStatusStripVariant =
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'neutral';

@Component({
  selector: 'deja-status-strip',
  standalone: true,
  imports: [
    WorkspaceStatusBadgeComponent,
  ],
  templateUrl: './workspace-status-strip.html',
  styleUrl: './workspace-status-strip.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceStatusStripComponent {

  @Input()
  icon?: string;

  @Input()
  title = '';

  @Input()
  subtitle = '';

  @Input()
  status = '';

  @Input()
  variant: WorkspaceStatusStripVariant = 'neutral';

}