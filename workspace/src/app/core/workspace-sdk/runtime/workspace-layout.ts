/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Contracts
 *
 * Contratos institucionais responsáveis pela definição dos Layouts
 * utilizados na composição dos Dashboards do Workspace.
 */

import {
  WorkspaceDashboardLayoutId,
  WorkspaceDashboardLayoutType,
  WorkspaceDashboardRegionId,
  WorkspaceOwnerId,
  WorkspacePriority,
} from '../contracts/workspace-contracts';
import { WorkspaceLayoutCapabilities } from './workspace-layout-capabilities';

/**
 * Descrição institucional de um Workspace Layout.
 *
 * Um Layout define a organização lógica das regiões utilizadas
 * para composição de um Dashboard, permanecendo independente
 * de mecanismos de renderização, bibliotecas visuais ou unidades
 * físicas de posicionamento.
 */
export interface WorkspaceLayout {
  /**
   * Identificador institucional do Layout.
   */
  readonly id: WorkspaceDashboardLayoutId;

  /**
   * Proprietário do Layout.
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
   * Tipo lógico do Layout.
   */
  readonly type: WorkspaceDashboardLayoutType;

  /**
   * Regiões que compõem o Layout.
   *
   * As definições completas das regiões permanecem registradas
   * separadamente, evitando acoplamento entre os contratos.
   */
  readonly regionIds?: readonly WorkspaceDashboardRegionId[];

  /**
   * Versão institucional do Layout.
   */
  readonly version?: string;

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
   * Configuração inicial do Layout.
   *
   * Permanece independente de qualquer mecanismo específico
   * de renderização ou composição visual.
   */
  readonly configuration?: Readonly<Record<string, unknown>>;

  /**
   * Metadados adicionais.
   */
  readonly capabilities?: WorkspaceLayoutCapabilities;

  readonly metadata?: Readonly<Record<string, unknown>>;
}
