/*
 * Deja Workspace UI SDK
 *
 * Workspace Resolved Dashboard Contracts
 *
 * Representa um Dashboard completamente resolvido pelo
 * Workspace Dashboard Resolver.
 */

import {
  WorkspaceDashboard,
} from './workspace-dashboard';

import {
  WorkspaceLayout,
} from './workspace-layout';

import {
  WorkspaceLayoutState,
} from './workspace-layout-state';

import {
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Representa um Dashboard totalmente resolvido.
 *
 * Este contrato é o resultado final do processo de resolução
 * realizado pelo WorkspaceDashboardResolver e constitui o único
 * modelo consumido pela futura camada de renderização.
 */
export interface WorkspaceResolvedDashboard {

  /**
   * Dashboard institucional.
   */
  readonly dashboard: WorkspaceDashboard;

  /**
   * Layout resolvido.
   *
   * Pode ser undefined para Dashboards legados.
   */
  readonly layout?: WorkspaceLayout;

  /**
   * Widgets efetivamente resolvidos.
   */
  readonly widgets: readonly WorkspaceWidgetInstance[];

  /**
   * Estado persistido carregado.
   */
  readonly state?: WorkspaceLayoutState;

  /**
   * Indica se a resolução foi considerada válida.
   */
  readonly valid: boolean;

  /**
   * Mensagens produzidas durante a resolução.
   *
   * Permite reportar Widgets inexistentes,
   * Layout ausente, incompatibilidades, etc.
   */
  readonly diagnostics: readonly string[];
}