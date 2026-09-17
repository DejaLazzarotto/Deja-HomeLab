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
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceBootstrapService,
} from './workspace-bootstrap.service';

/**
 * Mantém uma única tarefa de inicialização para cada Runtime.
 *
 * Mudanças de rota podem recriar o WorkspacePageComponent,
 * mas não devem reinicializar um Runtime que já está ativo.
 */
const bootstrapTasks =
  new WeakMap<WorkspaceRuntime, Promise<void>>();

/**
 * Executa o bootstrap oficial do Workspace.
 */
export async function bootstrapWorkspace(
  bootstrap: WorkspaceBootstrapService,
  context: WorkspaceRuntimeContext,
): Promise<void> {

  const runtime = bootstrap.getRuntime();

  if (runtime.getState() === 'running') {
    return;
  }

  const currentTask = bootstrapTasks.get(runtime);

  if (currentTask) {
    await currentTask;

    return;
  }

  const task = startWorkspace(
    bootstrap,
    runtime,
    context,
  );

  bootstrapTasks.set(
    runtime,
    task,
  );

  try {
    await task;
  } catch (error: unknown) {
    bootstrapTasks.delete(runtime);

    throw error;
  }

}

/**
 * Executa as transições necessárias sem repetir
 * operações já concluídas.
 */
async function startWorkspace(
  bootstrap: WorkspaceBootstrapService,
  runtime: WorkspaceRuntime,
  context: WorkspaceRuntimeContext,
): Promise<void> {

  if (runtime.getState() === 'created') {
    bootstrap.configure();

    await runtime.initialize(
      context,
    );
  }

  if (runtime.getState() === 'ready') {
    await runtime.start();
  }

}