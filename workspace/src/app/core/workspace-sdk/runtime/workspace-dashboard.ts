/*
 * Deja Workspace UI SDK
 *
 * Workspace Dashboard Contracts
 *
 * Contratos institucionais responsáveis pela composição de
 * Dashboards utilizando Workspace Widgets e Layouts.
 */

import {
  WorkspaceDashboardId,
  WorkspaceDashboardLayoutId,
  WorkspaceOwnerId,
  WorkspacePriority,
} from '../contracts/workspace-contracts';

import {
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Representa um Dashboard institucional.
 *
 * Um Dashboard é uma composição declarativa de Widgets associada
 * opcionalmente a um Layout institucional, permanecendo totalmente
 * independente da tecnologia de renderização.
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
   * Layout utilizado pelo Dashboard.
   *
   * Mantido opcional para preservar compatibilidade com
   * Dashboards que ainda não utilizam o Layout Engine.
   */
  readonly layoutId?: WorkspaceDashboardLayoutId;

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
   *
   * O posicionamento de cada instância permanece declarativo
   * e será interpretado pelo Layout Engine.
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