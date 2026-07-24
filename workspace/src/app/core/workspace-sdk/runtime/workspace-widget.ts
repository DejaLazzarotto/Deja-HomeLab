/*
 * Deja Workspace UI SDK
 *
 * Workspace Widget Contracts
 *
 * Contratos institucionais responsáveis pela definição dos Widgets
 * reutilizáveis do Workspace.
 */

import {
  WorkspaceOwnerId,
  WorkspacePriority,
  WorkspaceWidgetCapability,
  WorkspaceWidgetCategory,
  WorkspaceWidgetId,
  WorkspaceWidgetSizeConstraints,
  WorkspaceWidgetSurface,
  WorkspaceDashboardRegionId,
} from '../contracts/workspace-contracts';

import { WorkspaceActionId } from './workspace-action';

/**
 * Descrição institucional de um Workspace Widget.
 *
 * Um Widget representa uma unidade reutilizável de composição
 * visual do Workspace, permanecendo totalmente independente do
 * mecanismo de renderização.
 */
export interface WorkspaceWidget {
  /**
   * Identificador institucional.
   */
  readonly id: WorkspaceWidgetId;

  /**
   * Proprietário do Widget.
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
   * Categoria institucional.
   */
  readonly category?: WorkspaceWidgetCategory;

  /**
   * Tipo lógico utilizado para classificação.
   */
  readonly widgetType: string;

  /**
   * Superfícies suportadas.
   */
  readonly supportedSurfaces?: readonly WorkspaceWidgetSurface[];

  /**
   * Capacidades declaradas.
   */
  readonly capabilities?: readonly WorkspaceWidgetCapability[];

  /**
   * Action principal.
   */
  readonly primaryActionId?: WorkspaceActionId;

  /**
   * Actions auxiliares.
   */
  readonly actionIds?: readonly WorkspaceActionId[];

  /**
   * Restrições de dimensionamento.
   */
  readonly size?: WorkspaceWidgetSizeConstraints;

  /**
   * Adaptador de renderização.
   *
   * Mantido temporariamente para integração futura
   * com os adaptadores de UI.
   */
  readonly component?: unknown;

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
   * Configuração inicial.
   */
  readonly defaultConfiguration?: Readonly<Record<string, unknown>>;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Representa uma instância de Widget dentro de um Dashboard.
 */
export interface WorkspaceWidgetInstance {
  /**
   * Identificador da instância.
   */
  readonly id: string;

  /**
   * Widget utilizado.
   */
  readonly widgetId: WorkspaceWidgetId;

  /**
   * Título opcional sobrescrito.
   */
  readonly title?: string;

  /**
   * Região do Layout à qual esta instância pertence.
   *
   * O Layout Engine será responsável por determinar a
   * posição física da região durante a composição do Dashboard.
   */
  readonly regionId?: WorkspaceDashboardRegionId;

  /**
   * Posição declarativa na grade.
   *
   * Mantida temporariamente para compatibilidade durante
   * a transição para o Layout Engine.
   */
  readonly position?: WorkspaceGridPosition;

  /**
   * Configuração específica da instância.
   */
  readonly configuration?: Readonly<Record<string, unknown>>;

  /**
   * Estado de habilitação.
   */
  readonly enabled?: boolean;
}

/**
 * Define a posição de um item na grade do Workspace.
 */
export interface WorkspaceGridPosition {
  /**
   * Coluna inicial.
   */
  readonly column: number;

  /**
   * Linha inicial.
   */
  readonly row: number;

  /**
   * Quantidade de colunas ocupadas.
   */
  readonly columnSpan?: number;

  /**
   * Quantidade de linhas ocupadas.
   */
  readonly rowSpan?: number;
}
