/*
 * Deja Workspace UI SDK
 *
 * Workspace Renderer Contracts
 *
 * Contrato institucional responsável pela renderização de um
 * WorkspaceResolvedDashboard.
 */

import {
  WorkspaceResolvedDashboard,
} from './workspace-resolved-dashboard';

import {
  WorkspaceRenderContext,
} from './workspace-render-context';

/**
 * Contrato institucional de um Renderer.
 *
 * O Renderer é responsável exclusivamente pela transformação
 * de um WorkspaceResolvedDashboard em uma representação visual.
 *
 * Toda a resolução de Dashboards, Layouts e Widgets permanece
 * sob responsabilidade do Workspace Runtime.
 */
export interface WorkspaceRenderer {

  /**
   * Identificador institucional.
   */
  readonly id: string;

  /**
   * Nome apresentado ao usuário.
   */
  readonly name: string;

  /**
   * Ordem de prioridade.
   *
   * Quando múltiplos Renderers suportarem o mesmo contexto,
   * o de menor prioridade será selecionado.
   */
  readonly priority?: number;

  /**
   * Estado de habilitação.
   */
  readonly enabled?: boolean;

  /**
   * Verifica se o Renderer suporta o contexto informado.
   */
  supports(
    context: WorkspaceRenderContext,
  ): boolean;

  /**
   * Renderiza um Dashboard resolvido.
   */
  render(
    dashboard: WorkspaceResolvedDashboard,
    context: WorkspaceRenderContext,
  ): Promise<void>;

  /**
   * Libera recursos utilizados pelo Renderer.
   */
  dispose(): Promise<void>;
}