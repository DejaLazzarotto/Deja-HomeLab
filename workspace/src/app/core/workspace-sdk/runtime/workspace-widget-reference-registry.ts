/*
 * Deja Workspace UI SDK
 *
 * Workspace Widget Reference Registry
 *
 * Contrato institucional responsável pela localização de
 * Widgets atualmente renderizados pelo Workspace.
 */

import {
  WorkspaceWidgetRenderReference,
} from './workspace-widget-render-reference';

/**
 * Registro institucional de referências de Widgets renderizados.
 *
 * A implementação concreta pode utilizar Angular, outra tecnologia
 * visual ou qualquer mecanismo de armazenamento.
 */
export interface WorkspaceWidgetReferenceRegistry {

  /**
   * Localiza uma referência renderizada pelo identificador
   * institucional da instância do Widget.
   */
  get(
    widgetInstanceId: string,
  ): WorkspaceWidgetRenderReference | undefined;

}