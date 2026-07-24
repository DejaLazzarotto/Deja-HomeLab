/*
 * Deja Workspace Angular Integration
 *
 * Workspace Render Host Directive
 *
 * Diretiva responsável por expor o host oficial de renderização
 * Angular para o Workspace Rendering.
 */

import {
  Directive,
  EnvironmentInjector,
  ViewContainerRef,
} from '@angular/core';

import {
  AngularWorkspaceRenderHost,
} from './angular-workspace-render-host';

/**
 * Host oficial de renderização do Workspace.
 *
 * Expõe o ViewContainerRef e o EnvironmentInjector utilizados
 * pela infraestrutura de renderização Angular.
 */
@Directive({
  selector: '[dejaWorkspaceRenderHost]',
  standalone: true,
  exportAs: 'dejaWorkspaceRenderHost',
})
export class WorkspaceRenderHostDirective
  implements AngularWorkspaceRenderHost {

  constructor(
    public readonly viewContainerRef: ViewContainerRef,
    public readonly environmentInjector: EnvironmentInjector,
  ) {}

}