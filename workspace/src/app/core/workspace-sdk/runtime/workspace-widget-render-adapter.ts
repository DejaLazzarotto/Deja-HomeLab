/*
 * Deja Workspace UI SDK
 *
 * Workspace Widget Render Adapter
 *
 * Contrato institucional responsável pela execução das
 * operações incrementais de renderização sobre Widgets.
 *
 * Este contrato permanece completamente independente de
 * Angular, DOM ou qualquer tecnologia concreta de interface.
 */

import {
  WorkspaceIncrementalRenderOperation,
} from './workspace-incremental-render-operation';

/**
 * Responsável pela execução institucional das operações
 * incrementais de renderização de Widgets.
 *
 * Implementações concretas pertencem exclusivamente às
 * camadas de integração (Angular, React, Blazor, etc.).
 */
export interface WorkspaceWidgetRenderAdapter {

  /**
   * Move um Widget já existente.
   *
   * Retorna true quando a operação foi executada.
   */
  move(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean;

  /**
   * Redimensiona um Widget existente.
   *
   * Retorna true quando a operação foi executada.
   */
  resize(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean;

  /**
   * Insere um novo Widget na árvore de renderização.
   *
   * Retorna true quando a operação foi executada.
   */
  insert(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean;

  /**
   * Remove um Widget da árvore de renderização.
   *
   * Retorna true quando a operação foi executada.
   */
  remove(
    operation: WorkspaceIncrementalRenderOperation,
  ): boolean;

}