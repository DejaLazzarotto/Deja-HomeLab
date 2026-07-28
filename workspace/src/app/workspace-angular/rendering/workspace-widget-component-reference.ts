/*
 * Deja Workspace Angular Integration
 *
 * Workspace Widget Component Reference
 *
 * Referência Angular de uma instância de Widget atualmente
 * renderizada pelo Workspace.
 */

import {
  WorkspaceWidgetRenderReference,
} from '../../core/workspace-sdk/runtime/workspace-widget-render-reference';

import {
  WorkspaceWidgetHostComponent,
} from '../components/workspace-widget-host/workspace-widget-host';

import {
  WorkspaceWidgetRenderController,
} from './workspace-widget-render-controller';

/**
 * Representa uma referência Angular para um
 * WorkspaceWidgetHostComponent atualmente ativo.
 *
 * Esta referência especializa o contrato institucional neutro
 * definido pelo Workspace SDK, acrescentando exclusivamente
 * informações pertencentes à integração Angular.
 */
export interface WorkspaceWidgetComponentReference
  extends WorkspaceWidgetRenderReference {

  /**
   * Instância Angular viva do host responsável pela
   * renderização do Widget.
   */
  readonly component:
    WorkspaceWidgetHostComponent;

  /**
   * Controlador responsável pelas operações incrementais
   * aplicáveis à instância renderizada do Widget.
   */
  readonly controller:
    WorkspaceWidgetRenderController;

}