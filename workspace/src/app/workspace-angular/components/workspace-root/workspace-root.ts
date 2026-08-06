/*
 * Deja Workspace Angular Integration
 *
 * Workspace Root Component
 *
 * Componente raiz responsável por hospedar a árvore visual do
 * Workspace. Atua como ponto de entrada da renderização Angular,
 * permanecendo desacoplado do Workspace SDK.
 */

import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  ViewChild,
} from '@angular/core';

import {
  WorkspaceRenderHostDirective,
} from '../../rendering/workspace-render-host.directive';

import {
  WorkspaceShellController,
} from '../../services/workspace-shell-controller';

@Component({
  selector: 'deja-workspace-root',
  standalone: true,
  imports: [
    WorkspaceRenderHostDirective,
  ],
  templateUrl: './workspace-root.html',
  styleUrl: './workspace-root.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceRootComponent
  implements AfterViewInit, OnDestroy {

  /**
   * Host oficial onde a árvore visual do Workspace será
   * renderizada.
   */
  @ViewChild(
    WorkspaceRenderHostDirective,
    {
      static: true,
    },
  )
  private readonly renderHost!:
    WorkspaceRenderHostDirective;

  constructor(
    private readonly shell:
      WorkspaceShellController,
  ) {}

  /**
   * Inicia a camada visual somente depois que o host Angular
   * estiver disponível.
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
      this.renderHost,
    );

  }

}