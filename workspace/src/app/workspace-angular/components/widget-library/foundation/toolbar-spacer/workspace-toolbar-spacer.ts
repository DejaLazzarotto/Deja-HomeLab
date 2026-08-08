/*
 * Deja Workspace Angular Integration
 *
 * Workspace Toolbar Spacer Component
 *
 * Componente institucional reutilizável responsável por
 * distribuir espaço flexível entre grupos de ações dentro
 * das toolbars da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

@Component({
  selector: 'deja-toolbar-spacer',
  standalone: true,
  templateUrl: './workspace-toolbar-spacer.html',
  styleUrl: './workspace-toolbar-spacer.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceToolbarSpacerComponent {
}