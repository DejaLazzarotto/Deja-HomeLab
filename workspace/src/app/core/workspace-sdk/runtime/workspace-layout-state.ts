/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout State Contracts
 *
 * Contratos institucionais responsáveis pela persistência
 * do estado de um Dashboard e seu Layout.
 */

import {
  WorkspaceDashboardId,
  WorkspaceDashboardLayoutId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Estado persistido de um Dashboard.
 *
 * Este contrato representa exclusivamente informações
 * serializáveis, permanecendo independente do mecanismo
 * de armazenamento e da tecnologia de renderização.
 */
export interface WorkspaceLayoutState {

  /**
   * Dashboard ao qual pertence o estado.
   */
  readonly dashboardId: WorkspaceDashboardId;

  /**
   * Layout atualmente utilizado.
   */
  readonly layoutId: WorkspaceDashboardLayoutId;

  /**
   * Versão do estado persistido.
   *
   * Utilizada para migrações futuras.
   */
  readonly version?: number;

  /**
   * Composição persistida de instâncias de Widgets.
   *
   * Permite restaurar movimentações, redimensionamentos,
   * inserções, remoções e configurações personalizadas sem
   * alterar a definição institucional original do Dashboard.
   *
   * Quando omitida, a composição institucional do Dashboard
   * deverá ser preservada.
   */
  readonly widgets?: readonly WorkspaceWidgetInstance[];

  /**
   * Configuração persistida do Dashboard.
   */
  readonly configuration?: Readonly<Record<string, unknown>>;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}