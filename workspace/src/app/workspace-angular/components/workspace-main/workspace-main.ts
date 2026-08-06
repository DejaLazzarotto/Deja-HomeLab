/*
 * Deja Workspace Angular Integration
 *
 * Workspace Main Component
 *
 * Área central institucional responsável por hospedar
 * a renderização dos Dashboards do Workspace.
 */

import {
  ChangeDetectionStrategy,
  Component,
  ViewChild,
} from '@angular/core';

import {
  WorkspaceRenderHostDirective,
} from '../../rendering/workspace-render-host.directive';

/**
 * Área principal permanente da Workspace Shell.
 */
@Component({
  selector: 'deja-workspace-main',
  standalone: true,
  imports: [
    WorkspaceRenderHostDirective,
  ],
  templateUrl: './workspace-main.html',
  styleUrl: './workspace-main.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceMainComponent {

  /**
   * Host oficial onde os Dashboards serão renderizados.
   */
  @ViewChild(
    WorkspaceRenderHostDirective,
    {
      static: true,
    },
  )
  private readonly renderHost!:
    WorkspaceRenderHostDirective;

  /**
   * Retorna o host de renderização da área principal.
   */
  getRenderHost(): WorkspaceRenderHostDirective {

    return this.renderHost;

  }

}