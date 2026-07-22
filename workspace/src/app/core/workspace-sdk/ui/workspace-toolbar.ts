import {
  WorkspaceActionId,
} from '../runtime/workspace-action';

/**
 * Identificador único de uma Toolbar.
 */
export type WorkspaceToolbarId = string;

/**
 * Item de Toolbar.
 *
 * Cada botão referencia exclusivamente
 * uma Workspace Action.
 */
export interface WorkspaceToolbarItem {

  readonly id: string;

  readonly label: string;

  readonly icon?: string;

  readonly tooltip?: string;

  readonly actionId: WorkspaceActionId;

  readonly order?: number;

  readonly visible?: boolean;

  readonly enabled?: boolean;
}

/**
 * Contrato público de uma Workspace Toolbar.
 */
export interface WorkspaceToolbar {

  readonly id: WorkspaceToolbarId;

  readonly label: string;

  readonly order?: number;

  readonly items: readonly WorkspaceToolbarItem[];
}