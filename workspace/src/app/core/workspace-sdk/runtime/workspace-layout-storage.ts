/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Storage Contracts
 *
 * Contratos institucionais responsáveis pela persistência
 * do estado dos Layouts do Workspace.
 */

import {
  WorkspaceDashboardId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceLayoutState,
} from './workspace-layout-state';

/**
 * Contrato institucional para persistência de Layouts.
 *
 * O Workspace SDK define apenas a interface de persistência,
 * permanecendo totalmente independente do mecanismo de
 * armazenamento utilizado pela aplicação.
 *
 * Exemplos de implementação:
 *
 * - LocalStorage
 * - IndexedDB
 * - REST API
 * - Electron
 * - SQLite
 * - Cloud Storage
 */
export interface WorkspaceLayoutStorage {

  /**
   * Carrega o estado persistido de um Dashboard.
   *
   * Retorna undefined caso nenhum estado tenha sido salvo.
   */
  load(
    dashboardId: WorkspaceDashboardId,
  ): Promise<WorkspaceLayoutState | undefined>;

  /**
   * Persiste o estado atual de um Dashboard.
   */
  save(
    state: WorkspaceLayoutState,
  ): Promise<void>;

  /**
   * Remove o estado persistido de um Dashboard.
   */
  remove(
    dashboardId: WorkspaceDashboardId,
  ): Promise<void>;

  /**
   * Verifica se existe estado persistido para o Dashboard.
   */
  exists(
    dashboardId: WorkspaceDashboardId,
  ): Promise<boolean>;
}