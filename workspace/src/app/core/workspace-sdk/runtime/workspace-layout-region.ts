/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Region Contracts
 *
 * Contratos institucionais responsáveis pela definição das regiões
 * utilizadas pelos Layouts do Workspace.
 */

import {
  WorkspaceDashboardRegionId,
  WorkspaceOwnerId,
  WorkspacePriority,
} from '../contracts/workspace-contracts';

/**
 * Descrição institucional de uma região pertencente a um Workspace Layout.
 *
 * Uma região representa uma área lógica de composição, permanecendo
 * totalmente independente de mecanismos de renderização, bibliotecas
 * visuais ou implementação de docking.
 */
export interface WorkspaceLayoutRegion {

  /**
   * Identificador institucional da região.
   */
  readonly id: WorkspaceDashboardRegionId;

  /**
   * Proprietário da região.
   */
  readonly owner: WorkspaceOwnerId;

  /**
   * Título apresentado ao usuário.
   */
  readonly title: string;

  /**
   * Descrição institucional.
   */
  readonly description?: string;

  /**
   * Tipo lógico da região.
   *
   * Permanece livre para definição pelos módulos consumidores.
   */
  readonly regionType: string;

  /**
   * Prioridade institucional.
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
   * Configuração inicial da região.
   *
   * Não representa qualquer implementação específica
   * de renderização.
   */
  readonly configuration?: Readonly<Record<string, unknown>>;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}