/*
 * Deja Workspace Angular Integration
 *
 * Workspace Stack Foundation Component
 *
 * Responsável pela composição vertical institucional
 * da Deja UI Foundation.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

export type WorkspaceStackGap =
  | 'xs'
  | 'sm'
  | 'md'
  | 'lg'
  | 'xl';

export type WorkspaceStackAlignment =
  | 'start'
  | 'center'
  | 'stretch';

export type WorkspaceStackJustify =
  | 'start'
  | 'center'
  | 'space-between';

@Component({
  selector: 'deja-workspace-stack',
  standalone: true,
  templateUrl: './workspace-stack.html',
  styleUrl: './workspace-stack.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceStackComponent {

  @Input()
  gap: WorkspaceStackGap = 'md';

  @Input()
  align: WorkspaceStackAlignment = 'stretch';

  @Input()
  justify: WorkspaceStackJustify = 'start';
}