/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Configuration
 *
 * Contrato institucional responsável pelas configurações
 * declarativas de um Workspace Layout.
 */

import {
  WorkspaceGridConfiguration,
} from './workspace-grid-configuration';

/**
 * Configuração institucional de um Workspace Layout.
 *
 * Este contrato permanece independente da infraestrutura
 * de renderização, concentrando apenas configurações
 * declarativas pertencentes ao Layout.
 */
export interface WorkspaceLayoutConfiguration {

  /**
   * Configuração institucional do Workspace Grid.
   */
  readonly grid?: WorkspaceGridConfiguration;

}