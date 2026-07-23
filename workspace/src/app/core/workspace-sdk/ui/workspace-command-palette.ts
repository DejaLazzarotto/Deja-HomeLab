/*
 * Deja Workspace UI SDK
 *
 * Workspace Command Palette
 *
 * Contratos oficiais da infraestrutura institucional da
 * Workspace Command Palette.
 */

import {
  WorkspaceActionId,
} from '../runtime/workspace-action';

/**
 * Identificador único de um item da Command Palette.
 */
export type WorkspaceCommandPaletteId = string;

/**
 * Item oficial da Workspace Command Palette.
 *
 * A Command Palette referencia exclusivamente Workspace Actions,
 * preservando o desacoplamento entre a interface do usuário e
 * a lógica de negócio.
 */
export interface WorkspaceCommandPalette {

  /**
   * Identificador único.
   */
  readonly id: WorkspaceCommandPaletteId;

  /**
   * Título apresentado ao usuário.
   */
  readonly title: string;

  /**
   * Descrição opcional.
   */
  readonly description?: string;

  /**
   * Palavras-chave utilizadas durante a pesquisa.
   */
  readonly keywords?: readonly string[];

  /**
   * Ícone apresentado pela interface.
   */
  readonly icon?: string;

  /**
   * Categoria utilizada para agrupamento.
   */
  readonly category?: string;

  /**
   * Ordem de exibição.
   */
  readonly order?: number;

  /**
   * Indica se o item encontra-se habilitado.
   *
   * Padrão:
   * true
   */
  readonly enabled?: boolean;

  /**
   * Indica se o item encontra-se visível.
   *
   * Padrão:
   * true
   */
  readonly visible?: boolean;

  /**
   * Workspace Action executada pela Command Palette.
   */
  readonly actionId: WorkspaceActionId;
}