/*
 * Deja Workspace Angular Integration
 *
 * Workspace Icon Button Component
 *
 * Componente institucional reutilizável responsável pela
 * representação de ações compactas baseadas em ícones
 * dentro dos Widgets da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  Output,
} from '@angular/core';

export type WorkspaceIconButtonVariant =
  | 'default'
  | 'primary'
  | 'success'
  | 'warning'
  | 'danger';

export type WorkspaceIconButtonSize =
  | 'sm'
  | 'md'
  | 'lg';

@Component({
  selector: 'deja-icon-button',
  standalone: true,
  templateUrl: './workspace-icon-button.html',
  styleUrl: './workspace-icon-button.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceIconButtonComponent {

  @Input()
  icon = '';

  @Input()
  label = '';

  @Input()
  variant: WorkspaceIconButtonVariant = 'default';

  @Input()
  size: WorkspaceIconButtonSize = 'md';

  @Input()
  disabled = false;

  @Input()
  active = false;

  @Output()
  readonly action = new EventEmitter<void>();

  handleClick(): void {
    if (this.disabled) {
      return;
    }

    this.action.emit();
  }

}