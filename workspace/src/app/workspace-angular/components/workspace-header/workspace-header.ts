/*
 * Deja Workspace Angular Integration
 *
 * Workspace Header Component
 *
 * Cabeçalho institucional responsável pela identificação visual
 * principal da Deja Platform.
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

/**
 * Cabeçalho permanente da Workspace Shell.
 */
@Component({
  selector: 'deja-workspace-header',
  standalone: true,
  templateUrl: './workspace-header.html',
  styleUrl: './workspace-header.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceHeaderComponent {

  /**
   * Nome institucional exibido pela Shell.
   */
  readonly platformName = 'Deja Platform';

  /**
   * Nome da aplicação atualmente hospedada.
   */
  readonly applicationName = 'Workspace';

}