/*
 * Deja Workspace Angular Integration
 *
 * Workspace Status Bar Component
 *
 * Barra inferior institucional responsável por apresentar
 * informações operacionais e de contexto da Workspace Shell.
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

/**
 * Barra de status permanente da Workspace Shell.
 */
@Component({
  selector: 'deja-workspace-status-bar',
  standalone: true,
  templateUrl: './workspace-status-bar.html',
  styleUrl: './workspace-status-bar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceStatusBarComponent {

  /**
   * Estado operacional inicial da plataforma.
   */
  readonly status = 'Ready';

  /**
   * Identificação inicial do ambiente.
   */
  readonly environment = 'Local';

}