/*
 * Deja Workspace UI SDK
 *
 * Workspace Navigation Contracts
 *
 * Contratos institucionais responsáveis pela navegação entre
 * Workspace Dashboards, permanecendo independentes da tecnologia
 * de renderização e da aplicação hospedeira.
 */

import {
  WorkspaceDashboardId,
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';

/**
 * Identificador oficial de um item de navegação.
 */
export type WorkspaceNavigationId = string;

/**
 * Item institucional de navegação do Workspace.
 *
 * Representa uma entrada navegável da Workspace Application.
 */
export interface WorkspaceNavigation {

  /**
   * Identificador único.
   */
  readonly id: WorkspaceNavigationId;

  /**
   * Proprietário.
   */
  readonly ownerId: WorkspaceOwnerId;

  /**
   * Dashboard associado.
   */
  readonly dashboardId: WorkspaceDashboardId;

  /**
   * Título apresentado na interface.
   */
  readonly title: string;

  /**
   * Descrição opcional.
   */
  readonly description?: string;

  /**
   * Ícone institucional.
   */
  readonly icon?: string;

  /**
   * Ordem sugerida para apresentação.
   */
  readonly order?: number;

  /**
   * Determina se o item está habilitado.
   */
  readonly enabled?: boolean;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}