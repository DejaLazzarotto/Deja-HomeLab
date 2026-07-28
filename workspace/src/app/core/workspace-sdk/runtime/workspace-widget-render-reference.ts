/*
 * Deja Workspace UI SDK
 *
 * Workspace Widget Render Reference
 *
 * Contrato institucional responsável pela representação
 * neutra de uma instância de Widget atualmente renderizada.
 */

import {
  WorkspaceWidgetInstance,
} from './workspace-widget';

/**
 * Referência institucional neutra para uma instância de
 * Workspace Widget atualmente renderizada.
 *
 * O contrato permanece independente:
 *
 * - do Angular;
 * - de componentes visuais;
 * - de ComponentRef;
 * - da tecnologia concreta de renderização.
 */
export interface WorkspaceWidgetRenderReference {

  /**
   * Identificador institucional da instância renderizada.
   */
  readonly widgetInstanceId:
    WorkspaceWidgetInstance['id'];

}