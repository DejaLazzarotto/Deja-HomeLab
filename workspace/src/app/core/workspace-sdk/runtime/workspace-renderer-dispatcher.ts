/*
 * Deja Workspace UI SDK
 *
 * Workspace Renderer Dispatcher
 *
 * Responsável pela seleção e despacho do Renderer
 * apropriado para um determinado contexto de renderização.
 */

import {
  WorkspaceRenderContext,
} from './workspace-render-context';

import {
  WorkspaceRenderer,
} from './workspace-renderer';

import {
  WorkspaceRendererRegistry,
} from './workspace-renderer-registry';

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

/**
 * Dispatcher institucional dos Workspace Renderers.
 *
 * Centraliza a seleção do Renderer apropriado e delega
 * a execução da renderização.
 */
export class WorkspaceRendererDispatcher {

  constructor(
    private readonly registry: WorkspaceRendererRegistry,
  ) {}

  /**
   * Localiza o Renderer apropriado para o contexto.
   */
  resolveRenderer(
    context: WorkspaceRenderContext,
  ): WorkspaceRenderer {

    return this.registry.resolve(context);

  }

  /**
   * Renderiza um Dashboard resolvido.
   */
  async render(
    dashboard: WorkspaceResolvedDashboard,
    context: WorkspaceRenderContext,
  ): Promise<void> {

    const renderer = this.resolveRenderer(context);

    await renderer.render(
      dashboard,
      context,
    );

  }

  /**
   * Libera os recursos do Renderer utilizado.
   */
  async dispose(
    context: WorkspaceRenderContext,
  ): Promise<void> {

    const renderer = this.resolveRenderer(context);

    await renderer.dispose();

  }

}