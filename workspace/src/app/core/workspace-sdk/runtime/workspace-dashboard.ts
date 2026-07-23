/*
 * Deja Workspace UI SDK
 *
 * Workspace Dashboard Contracts
 *
 * Contratos institucionais responsáveis pela composição de
 * Dashboards utilizando Workspace Widgets.
 */

import {
  WorkspaceDashboardId,
  WorkspaceOwnerId,
  WorkspacePriority,
} from '../contracts/workspace-contracts';

import {
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Representa um Dashboard institucional.
 *
 * Um Dashboard é uma composição declarativa de Widgets,
 * permanecendo totalmente independente da tecnologia de
 * renderização.
 */
export interface WorkspaceDashboard {

  /**
   * Identificador institucional.
   */
  readonly id: WorkspaceDashboardId;

  /**
   * Proprietário.
   */
  readonly owner: WorkspaceOwnerId;

  /**
   * Título.
   */
  readonly title: string;

  /**
   * Descrição.
   */
  readonly description?: string;

  /**
   * Ícone.
   */
  readonly icon?: string;

  /**
   * Rota opcional.
   */
  readonly route?: string;

  /**
   * Prioridade.
   */
  readonly priority?: WorkspacePriority;

  /**
   * Estado de habilitação.
   */
  readonly enabled?: boolean;

  /**
   * Tags institucionais.
   */
  readonly tags?: readonly string[];

  /**
   * Widgets pertencentes ao Dashboard.
   */
  readonly widgets?: readonly WorkspaceWidgetInstance[];

  /**
   * Configuração padrão.
   */
  readonly defaultConfiguration?: Readonly<Record<string, unknown>>;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}