/*
 * Deja Workspace Angular Integration
 *
 * Workspace Toolbar Component
 *
 * Container institucional reutilizável responsável pela
 * organização de ações contextuais, comandos e controles
 * utilizados pelos Widgets da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

@Component({
  selector: 'deja-workspace-toolbar',
  standalone: true,
  templateUrl: './workspace-toolbar.html',
  styleUrl: './workspace-toolbar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceToolbarComponent {
}