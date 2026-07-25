/*
 * Deja Workspace UI SDK
 *
 * Workspace Resolved Dashboard Contracts
 *
 * Representa um Dashboard completamente resolvido pelo
 * Workspace Dashboard Resolver.
 */

import { WorkspaceDashboard } from './workspace-dashboard';

import { WorkspaceGridConfiguration } from './workspace-grid-configuration';

import { WorkspaceLayout } from './workspace-layout';

import { WorkspaceLayoutRegion } from './workspace-layout-region';

import { WorkspaceLayoutState } from './workspace-layout-state';

import { WorkspaceWidgetInstance } from './workspace-widget';
import { WorkspaceLayoutCapabilities } from './workspace-layout-capabilities';

/**
 * Representa um Dashboard totalmente resolvido.
 *
 * Este contrato é o resultado final do processo de resolução
 * realizado pelo WorkspaceDashboardResolver e constitui o único
 * modelo consumido pela camada de renderização.
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
   * Regiões efetivamente resolvidas para o Layout.
   *
   * Permanece vazio quando:
   *
   * - o Dashboard não possui Layout;
   * - o Layout não possui regiões;
   * - nenhuma região válida foi resolvida.
   */
  readonly regions: readonly WorkspaceLayoutRegion[];

  /**
   * Widgets efetivamente resolvidos.
   */
  readonly widgets: readonly WorkspaceWidgetInstance[];

  /**
   * Estado persistido carregado.
   */
  readonly state?: WorkspaceLayoutState;

  /**
   * Configuração efetivamente resolvida do Workspace Grid.
   */
  readonly gridConfiguration: WorkspaceGridConfiguration;

  /**
   * Capacidades resolvidas do Layout.
   */
  readonly layoutCapabilities: WorkspaceLayoutCapabilities;

  /**
   * Indica se a resolução foi considerada válida.
   */
  readonly valid: boolean;

  /**
   * Mensagens produzidas durante a resolução.
   *
   * Permite reportar Widgets inexistentes,
   * Layout ausente, regiões inexistentes,
   * incompatibilidades, etc.
   */
  readonly diagnostics: readonly string[];
}
