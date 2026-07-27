/*
 * Deja Workspace Angular Integration
 *
 * Workspace Widget Component Reference
 *
 * Referência institucional de uma instância de Widget
 * atualmente renderizada pelo Workspace.
 */

import {
  WorkspaceWidgetInstance,
} from '../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetHostComponent,
} from '../components/workspace-widget-host/workspace-widget-host';

/**
 * Representa uma referência institucional para um
 * WorkspaceWidgetHostComponent atualmente ativo.
 *
 * O cache utiliza o identificador da instância do Widget,
 * permitindo distinguir múltiplas utilizações de uma mesma
 * definição institucional de Widget.
 *
 * Como os hosts são criados declarativamente pela árvore
 * Angular, esta estrutura mantém a instância viva do
 * componente, sem depender de um ComponentRef externo.
 */
export interface WorkspaceWidgetComponentReference {

  /**
   * Identificador institucional da instância do Widget.
   */
  readonly widgetInstanceId:
    WorkspaceWidgetInstance['id'];

  /**
   * Instância Angular viva do host responsável pela
   * renderização do Widget.
   */
  readonly component:
    WorkspaceWidgetHostComponent;

}