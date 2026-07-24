/*
 * Deja Workspace Angular Integration
 *
 * Angular Workspace Renderer Provider
 *
 * Responsável pelo registro do AngularWorkspaceRenderer
 * no Workspace Runtime.
 */

import {
  Injectable,
} from '@angular/core';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  AngularWorkspaceRenderer,
} from './angular-workspace-renderer';

/**
 * Provider oficial do Angular Workspace Renderer.
 *
 * Responsabilidades:
 * - associar o Renderer à instância oficial do Runtime;
 * - registrar o Renderer Angular;
 * - impedir que a aplicação conheça detalhes internos;
 * - preservar o desacoplamento entre Angular e Workspace SDK.
 */
@Injectable({
  providedIn: 'root',
})
export class AngularWorkspaceRendererProvider {

  constructor(
    private readonly renderer: AngularWorkspaceRenderer,
  ) {}

  /**
   * Registra o Renderer Angular no Workspace Runtime.
   */
  register(
    runtime: WorkspaceRuntime,
  ): void {

    this.renderer.registerRuntime(
      runtime,
    );

    runtime.registerRenderer(
      this.renderer,
    );

  }

}