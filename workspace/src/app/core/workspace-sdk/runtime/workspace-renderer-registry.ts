/*
 * Deja Workspace UI SDK
 *
 * Workspace Renderer Registry
 *
 * Registry institucional responsável pelo gerenciamento dos
 * Renderers disponíveis no Workspace Runtime.
 */

import {
  WorkspaceRenderContext,
} from './workspace-render-context';

import {
  WorkspaceRenderer,
} from './workspace-renderer';

/**
 * Erro lançado quando um Renderer duplicado é registrado.
 */
export class WorkspaceRendererDuplicateError extends Error {

  constructor(
    readonly rendererId: string,
  ) {
    super(`Workspace renderer already registered: ${rendererId}`);
    this.name = 'WorkspaceRendererDuplicateError';
  }

}

/**
 * Erro lançado quando nenhum Renderer suporta
 * o contexto solicitado.
 */
export class WorkspaceRendererNotFoundError extends Error {

  constructor() {
    super('No Workspace Renderer supports the requested context.');
    this.name = 'WorkspaceRendererNotFoundError';
  }

}

/**
 * Registry institucional de Workspace Renderers.
 */
export class WorkspaceRendererRegistry {

  private readonly renderers = new Map<string, WorkspaceRenderer>();

  /**
   * Registra um Renderer.
   */
  register(
    renderer: WorkspaceRenderer,
  ): void {

    if (this.renderers.has(renderer.id)) {
      throw new WorkspaceRendererDuplicateError(renderer.id);
    }

    this.renderers.set(renderer.id, renderer);

  }

  /**
   * Remove um Renderer.
   */
  unregister(
    rendererId: string,
  ): boolean {

    return this.renderers.delete(rendererId);

  }

  /**
   * Remove todos os Renderers.
   */
  clear(): void {

    this.renderers.clear();

  }

  /**
   * Lista todos os Renderers registrados.
   */
  list(): readonly WorkspaceRenderer[] {

    return [...this.renderers.values()]
      .sort((left, right) =>
        (left.priority ?? Number.MAX_SAFE_INTEGER)
        - (right.priority ?? Number.MAX_SAFE_INTEGER),
      );

  }

  /**
   * Localiza o primeiro Renderer compatível
   * com o contexto informado.
   */
  resolve(
    context: WorkspaceRenderContext,
  ): WorkspaceRenderer {

    const renderer = this.list().find(
      (candidate) =>
        (candidate.enabled ?? true)
        && candidate.supports(context),
    );

    if (!renderer) {
      throw new WorkspaceRendererNotFoundError();
    }

    return renderer;

  }

}