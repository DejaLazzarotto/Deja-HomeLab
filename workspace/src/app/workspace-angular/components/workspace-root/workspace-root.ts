/*
 * Deja Workspace Angular Integration
 *
 * Workspace Root Component
 *
 * Componente raiz responsável por compor a árvore visual do
 * Workspace e iniciar seu ciclo de renderização institucional.
 */

import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  ViewChild,
} from '@angular/core';

import {
  WorkspaceHeaderComponent,
} from '../workspace-header/workspace-header';

import {
  WorkspaceMainComponent,
} from '../workspace-main/workspace-main';

import {
  WorkspaceSidebarComponent,
} from '../workspace-sidebar/workspace-sidebar';

import {
  WorkspaceStatusBarComponent,
} from '../workspace-status-bar/workspace-status-bar';

import {
  WorkspaceShellController,
} from '../../services/workspace-shell-controller';

@Component({
  selector: 'deja-workspace-root',
  standalone: true,
  imports: [
    WorkspaceHeaderComponent,
    WorkspaceSidebarComponent,
    WorkspaceMainComponent,
    WorkspaceStatusBarComponent,
  ],
  templateUrl: './workspace-root.html',
  styleUrl: './workspace-root.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceRootComponent
  implements AfterViewInit, OnDestroy {

  /**
   * Área central oficial responsável por fornecer o host
   * de renderização dos Dashboards.
   */
  @ViewChild(
    WorkspaceMainComponent,
    {
      static: true,
    },
  )
  private readonly workspaceMain!:
    WorkspaceMainComponent;

  constructor(
    private readonly shell:
      WorkspaceShellController,
  ) {}

  /**
   * Inicia a camada visual somente depois que todos os
   * componentes permanentes da Shell estiverem disponíveis.
   */
  ngAfterViewInit(): void {

    void this.startShell();

  }

  /**
   * Libera os recursos visuais quando o componente raiz
   * for destruído.
   */
  ngOnDestroy(): void {

    void this.shell.stop();

  }

  /**
   * Solicita ao controlador institucional o início da Shell.
   */
  private async startShell(): Promise<void> {

    await this.shell.start(
      this.workspaceMain.getRenderHost(),
    );

  }

}