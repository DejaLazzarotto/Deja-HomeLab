/*
 * Deja Workspace UI SDK
 *
 * Workspace Menu API
 *
 * Contratos públicos responsáveis pela definição dos menus
 * institucionais do Workspace.
 */

import {
  WorkspaceActionId,
} from '../runtime/workspace-action';

/**
 * Identificador de um menu.
 */
export type WorkspaceMenuId = string;

/**
 * Identificador de um item de menu.
 */
export type WorkspaceMenuItemId = string;

/**
 * Localização onde um menu pode ser exibido.
 */
export type WorkspaceMenuLocation =
  | 'application'
  | 'main'
  | 'user'
  | 'dashboard'
  | 'widget'
  | 'context'
  | 'toolbar'
  | 'command-palette';

/**
 * Item de menu.
 */
export interface WorkspaceMenuItem {

  /**
   * Identificador único.
   */
  readonly id: WorkspaceMenuItemId;

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
export interface WorkspaceMenuSeparator {

  readonly separator: true;
}

/**
 * Grupo de itens.
 */
export interface WorkspaceMenuGroup {

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
  readonly items: readonly WorkspaceMenuEntry[];
}

/**
 * Entrada de menu.
 */
export type WorkspaceMenuEntry =
  | WorkspaceMenuItem
  | WorkspaceMenuSeparator
  | WorkspaceMenuGroup;

/**
 * Menu institucional.
 */
export interface WorkspaceMenu {

  /**
   * Identificador.
   */
  readonly id: WorkspaceMenuId;

  /**
   * Local onde será exibido.
   */
  readonly location: WorkspaceMenuLocation;

  /**
   * Título do menu.
   */
  readonly title: string;

  /**
   * Ordem de exibição.
   */
  readonly order?: number;

  /**
   * Entradas do menu.
   */
  readonly entries: readonly WorkspaceMenuEntry[];
}