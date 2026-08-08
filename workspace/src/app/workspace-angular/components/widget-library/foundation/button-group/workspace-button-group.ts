/*
 * Deja Workspace Angular Integration
 *
 * Workspace Button Group Component
 *
 * Componente institucional reutilizável responsável pelo
 * agrupamento visual e estrutural de ações relacionadas
 * dentro dos Widgets da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

export type WorkspaceButtonGroupOrientation =
  | 'horizontal'
  | 'vertical';

export type WorkspaceButtonGroupSize =
  | 'sm'
  | 'md'
  | 'lg';

@Component({
  selector: 'deja-button-group',
  standalone: true,
  templateUrl: './workspace-button-group.html',
  styleUrl: './workspace-button-group.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceButtonGroupComponent {

  @Input()
  orientation: WorkspaceButtonGroupOrientation = 'horizontal';

  @Input()
  size: WorkspaceButtonGroupSize = 'md';

  @Input()
  ariaLabel?: string;

}