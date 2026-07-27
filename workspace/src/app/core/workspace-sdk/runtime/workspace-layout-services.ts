/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Services
 *
 * Fachada institucional responsável pela centralização dos
 * serviços utilizados pela infraestrutura de Layout.
 */

import {
  WorkspaceDashboardState,
} from './workspace-dashboard-state';

import {
  WorkspaceLayoutEventDispatcher,
} from './workspace-layout-event-dispatcher';

import {
  WorkspaceLayoutExtensionDispatcher,
} from './workspace-layout-extension-dispatcher';

import {
  WorkspaceLayoutHookDispatcher,
} from './workspace-layout-hook-dispatcher';

import {
  WorkspaceLayoutObservability,
} from './workspace-layout-observability';

import {
  WorkspaceLayoutPersistence,
} from './workspace-layout-persistence';

/**
 * Centraliza os serviços institucionais utilizados pelo
 * Workspace Layout Controller.
 *
 * Esta fachada preserva a independência entre:
 *
 * - coordenação das sessões;
 * - estado corrente do Dashboard;
 * - persistência;
 * - eventos;
 * - hooks;
 * - extensões;
 * - observabilidade;
 * - Workspace Runtime;
 * - tecnologia de renderização.
 */
export class WorkspaceLayoutServices {
  constructor(
    readonly persistence: WorkspaceLayoutPersistence,
    readonly events: WorkspaceLayoutEventDispatcher,
    readonly hooks: WorkspaceLayoutHookDispatcher,
    readonly extensions: WorkspaceLayoutExtensionDispatcher,
    readonly observability: WorkspaceLayoutObservability,
    readonly dashboardState: WorkspaceDashboardState,
  ) {}
}