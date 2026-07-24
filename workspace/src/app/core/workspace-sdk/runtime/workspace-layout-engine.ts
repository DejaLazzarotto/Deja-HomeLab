/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Engine Contracts
 *
 * Contrato institucional responsável pela resolução lógica
 * dos Layouts do Workspace.
 */

import {
  WorkspaceDashboardId,
  WorkspaceDashboardLayoutId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceDashboard,
} from './workspace-dashboard';

import {
  WorkspaceLayout,
} from './workspace-layout';

import {
  WorkspaceLayoutState,
} from './workspace-layout-state';

/**
 * Contrato institucional do Workspace Layout Engine.
 *
 * O Layout Engine é responsável por resolver a composição
 * lógica entre Dashboards, Layouts e Widgets, permanecendo
 * totalmente independente de qualquer mecanismo de
 * renderização.
 */
export interface WorkspaceLayoutEngine {

  /**
   * Obtém um Layout pelo seu identificador.
   */
  getLayout(
    layoutId: WorkspaceDashboardLayoutId,
  ): WorkspaceLayout | undefined;

  /**
   * Obtém o Layout associado a um Dashboard.
   */
  resolveLayout(
    dashboard: WorkspaceDashboard,
  ): WorkspaceLayout | undefined;

  /**
   * Carrega o estado persistido de um Dashboard.
   */
  loadState(
    dashboardId: WorkspaceDashboardId,
  ): Promise<WorkspaceLayoutState | undefined>;

  /**
   * Persiste o estado atual de um Dashboard.
   */
  saveState(
    state: WorkspaceLayoutState,
  ): Promise<void>;

  /**
   * Verifica se o Dashboard possui um Layout válido.
   */
  validate(
    dashboard: WorkspaceDashboard,
  ): boolean;
}