/*
 * Deja Workspace UI SDK
 *
 * Workspace Context Menu API
 *
 * Contratos públicos responsáveis pela definição dos menus
 * de contexto institucionais do Workspace.
 */

import {
  WorkspaceActionId,
} from '../runtime/workspace-action';

/**
 * Identificador de um Context Menu.
 */
export type WorkspaceContextMenuId = string;

/**
 * Identificador de um item de Context Menu.
 */
export type WorkspaceContextMenuItemId = string;

/**
 * Item de Context Menu.
 */
export interface WorkspaceContextMenuItem {

  /**
   * Identificador único.
   */
  readonly id: WorkspaceContextMenuItemId;

  /**
   * Texto exibido.
   */
  readonly label: string;

  /**
   * Action executada.
   */
  readonly actionId: WorkspaceActionId;

  /**
   * Ícone opcional.
   */
  readonly icon?: string;

  /**
   * Texto de ajuda.
   */
  readonly tooltip?: string;

  /**
   * Atalho opcional.
   */
  readonly shortcut?: string;

  /**
   * Item habilitado.
   *
   * Default: true
   */
  readonly enabled?: boolean;

  /**
   * Item visível.
   *
   * Default: true
   */
  readonly visible?: boolean;
}

/**
 * Separador visual.
 */
export interface WorkspaceContextMenuSeparator {

  readonly separator: true;
}

/**
 * Grupo de itens.
 */
export interface WorkspaceContextMenuGroup {

  /**
   * Identificador do grupo.
   */
  readonly id: string;

  /**
   * Nome do grupo.
   */
  readonly label?: string;

  /**
   * Itens do grupo.
   */
  readonly items: readonly WorkspaceContextMenuEntry[];
}

/**
 * Entrada de Context Menu.
 */
export type WorkspaceContextMenuEntry =
  | WorkspaceContextMenuItem
  | WorkspaceContextMenuSeparator
  | WorkspaceContextMenuGroup;

/**
 * Context Menu institucional.
 */
export interface WorkspaceContextMenu {

  /**
   * Identificador.
   */
  readonly id: WorkspaceContextMenuId;

  /**
   * Título do Context Menu.
   */
  readonly title: string;

  /**
   * Ordem de exibição.
   */
  readonly order?: number;

  /**
   * Entradas do Context Menu.
   */
  readonly entries: readonly WorkspaceContextMenuEntry[];
}