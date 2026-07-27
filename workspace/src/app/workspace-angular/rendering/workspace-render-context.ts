/*
 * Deja Workspace UI
 *
 * Workspace Render Context
 *
 * Contexto institucional utilizado pelas estratégias de
 * renderização do Workspace.
 */

import {
  WorkspaceDashboardUpdate,
} from '../../core/workspace-sdk/runtime/workspace-dashboard-state';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceDashboardComponent,
} from '../components/workspace-dashboard/workspace-dashboard';

/**
 * Contexto institucional entregue às estratégias de
 * renderização.
 *
 * Este objeto concentra as dependências necessárias para
 * aplicar uma atualização de Dashboard através do mecanismo
 * de renderização Angular.
 *
 * O contexto permanece interno à infraestrutura Angular e
 * não introduz nenhuma nova API pública no Workspace SDK.
 */
export interface WorkspaceRenderContext {

  /**
   * Runtime proprietário da renderização.
   */
  readonly runtime: WorkspaceRuntime;

  /**
   * Atualização publicada pelo Workspace Dashboard State.
   */
  readonly update: WorkspaceDashboardUpdate;

  /**
   * Componente responsável exclusivamente pela apresentação
   * do Dashboard.
   */
  readonly dashboardComponent: WorkspaceDashboardComponent;

}