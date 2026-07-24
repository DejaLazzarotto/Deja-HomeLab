/*
 * Deja Workspace Angular Integration
 *
 * Workspace Bootstrap
 *
 * Orquestrador oficial de inicialização do Workspace Runtime.
 */

import {
  WorkspaceRuntimeContext,
} from '../../core/workspace-sdk/models/workspace-models';

import {
  WorkspaceBootstrapService,
} from './workspace-bootstrap.service';

/**
 * Executa o bootstrap oficial do Workspace.
 */
export async function bootstrapWorkspace(
  bootstrap: WorkspaceBootstrapService,
  context: WorkspaceRuntimeContext,
): Promise<void> {

  const runtime = bootstrap.getRuntime();

  bootstrap.configure();

  await runtime.initialize(
    context,
  );

  await runtime.start();

}