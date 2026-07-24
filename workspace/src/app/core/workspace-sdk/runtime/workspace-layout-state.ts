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
   * Configuração persistida do Dashboard.
   */
  readonly configuration?: Readonly<Record<string, unknown>>;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}