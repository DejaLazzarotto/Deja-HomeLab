/*
 * Deja Workspace Angular Integration
 *
 * Angular Workspace Renderer
 *
 * Implementação concreta do contrato institucional
 * WorkspaceRenderer para aplicações Angular.
 */

import {
  Injectable,
} from '@angular/core';

import {
  WorkspaceRenderContext,
} from '../../core/workspace-sdk/runtime/workspace-render-context';

import {
  WorkspaceRenderer,
} from '../../core/workspace-sdk/runtime/workspace-renderer';

import {
  WorkspaceResolvedDashboard,
} from '../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceAngularRenderingService,
} from '../services/workspace-angular-rendering.service';

import {
  AngularWorkspaceRenderHost,
} from './angular-workspace-render-host';

/**
 * Implementação Angular do Workspace Renderer.
 *
 * Responsabilidades:
 * - identificar suporte à tecnologia Angular;
 * - validar o host recebido;
 * - preservar a referência do Runtime registrado;
 * - adaptar o contrato do Workspace SDK para a camada Angular;
 * - delegar a criação e destruição da árvore visual ao serviço
 *   oficial de renderização Angular.
 */
@Injectable({
  providedIn: 'root',
})
export class AngularWorkspaceRenderer implements WorkspaceRenderer {

  readonly id = 'angular';

  readonly name = 'Angular Workspace Renderer';

  readonly priority = 100;

  readonly enabled = true;

  /**
   * Runtime ao qual este Renderer foi registrado.
   */
  private runtime?: WorkspaceRuntime;

  constructor(
    private readonly renderingService: WorkspaceAngularRenderingService,
  ) {}

  /**
   * Associa o Renderer à instância oficial do Workspace Runtime.
   */
  registerRuntime(
    runtime: WorkspaceRuntime,
  ): void {

    this.runtime = runtime;

  }

  /**
   * Retorna obrigatoriamente o Runtime associado.
   */
  getRuntime(): WorkspaceRuntime {

    if (!this.runtime) {
      throw new Error(
        'Angular Workspace Renderer is not associated with a Workspace Runtime.',
      );
    }

    return this.runtime;

  }

  /**
   * Verifica se o contexto é suportado.
   */
  supports(
    context: WorkspaceRenderContext,
  ): boolean {

    return context.technology === 'angular';

  }

  /**
   * Renderiza um Dashboard resolvido.
   */
  async render(
    dashboard: WorkspaceResolvedDashboard,
    context: WorkspaceRenderContext,
  ): Promise<void> {

    const host = this.getHost(context);
    const runtime = this.getRuntime();

    await this.renderingService.render(
      runtime,
      dashboard,
      host,
    );

  }

  /**
   * Libera os recursos utilizados pela renderização Angular.
   */
  async dispose(): Promise<void> {

    await this.renderingService.dispose();

  }

  /**
   * Obtém e valida o host Angular.
   */
  private getHost(
    context: WorkspaceRenderContext,
  ): AngularWorkspaceRenderHost {

    if (!this.supports(context)) {
      throw new Error(
        'Angular Workspace Renderer does not support the requested technology.',
      );
    }

    if (!this.isAngularRenderHost(context.host)) {
      throw new Error(
        'Invalid Angular Workspace Render Host.',
      );
    }

    return context.host;

  }

  /**
   * Verifica estruturalmente se o valor informado representa
   * um host válido da integração Angular.
   */
  private isAngularRenderHost(
    host: unknown,
  ): host is AngularWorkspaceRenderHost {

    if (
      typeof host !== 'object'
      || host === null
    ) {
      return false;
    }

    const candidate = host as Partial<AngularWorkspaceRenderHost>;

    return (
      candidate.viewContainerRef !== undefined
      && candidate.environmentInjector !== undefined
    );

  }

}