import {
  WorkspaceRuntimeState,
} from '../contracts/workspace-contracts';
import {
  WorkspaceModuleManifest,
  WorkspaceRuntimeContext,
  WorkspaceRuntimeSnapshot,
} from '../models/workspace-models';
import { WorkspaceRegistries } from '../registries/workspace-registries';

/**
 * Erro lançado quando uma operação não é permitida
 * no estado atual do Workspace Runtime.
 */
export class WorkspaceRuntimeStateError extends Error {
  constructor(
    readonly currentState: WorkspaceRuntimeState,
    readonly operation: string,
  ) {
    super(
      `Workspace runtime operation "${operation}" is not allowed in state "${currentState}"`,
    );

    this.name = 'WorkspaceRuntimeStateError';
  }
}

/**
 * Fundação oficial do Workspace Runtime.
 *
 * Responsabilidades:
 * - manter o estado do runtime;
 * - registrar manifestos de módulos;
 * - controlar inicialização, execução e encerramento;
 * - fornecer snapshots imutáveis;
 * - preservar independência de Angular.
 */
export class WorkspaceRuntime {
  private state: WorkspaceRuntimeState = 'created';

  private context?: WorkspaceRuntimeContext;

  private initializedAt?: Date;

  private startedAt?: Date;

  private stoppedAt?: Date;

  constructor(
    readonly registries: WorkspaceRegistries = new WorkspaceRegistries(),
  ) {}

  getState(): WorkspaceRuntimeState {
    return this.state;
  }

  getContext(): WorkspaceRuntimeContext | undefined {
    return this.context;
  }

  initialize(context: WorkspaceRuntimeContext): void {
    this.assertState('initialize', ['created', 'stopped']);

    this.state = 'initializing';
    this.context = context;
    this.initializedAt = new Date();
    this.startedAt = undefined;
    this.stoppedAt = undefined;
    this.state = 'ready';
  }

  registerManifest(manifest: WorkspaceModuleManifest): void {
    this.assertState('registerManifest', [
      'created',
      'initializing',
      'ready',
    ]);

    if (manifest.domains?.length) {
      this.registries.domains.registerMany(manifest.domains);
    }

    if (manifest.views?.length) {
      this.registries.views.registerMany(manifest.views);
    }

    if (manifest.navigation?.length) {
      this.registries.navigation.registerMany(manifest.navigation);
    }

    if (manifest.widgets?.length) {
      this.registries.widgets.registerMany(manifest.widgets);
    }

    if (manifest.dashboards?.length) {
      this.registries.dashboards.registerMany(manifest.dashboards);
    }

    if (manifest.services?.length) {
      this.registries.services.registerMany(manifest.services);
    }
  }

  start(): void {
    this.assertState('start', ['ready']);

    this.startedAt = new Date();
    this.stoppedAt = undefined;
    this.state = 'running';
  }

  stop(): void {
    this.assertState('stop', ['ready', 'running']);

    this.state = 'stopping';
    this.stoppedAt = new Date();
    this.state = 'stopped';
  }

  reset(): void {
    this.registries.clear();
    this.context = undefined;
    this.initializedAt = undefined;
    this.startedAt = undefined;
    this.stoppedAt = undefined;
    this.state = 'created';
  }

  fail(): void {
    this.state = 'failed';
  }

  snapshot(): WorkspaceRuntimeSnapshot {
    return {
      state: this.state,
      initializedAt: this.initializedAt,
      startedAt: this.startedAt,
      stoppedAt: this.stoppedAt,
      domains: this.registries.domains.count(),
      views: this.registries.views.count(),
      navigationItems: this.registries.navigation.count(),
      widgets: this.registries.widgets.count(),
      dashboards: this.registries.dashboards.count(),
      services: this.registries.services.count(),
    };
  }

  private assertState(
    operation: string,
    allowedStates: readonly WorkspaceRuntimeState[],
  ): void {
    if (!allowedStates.includes(this.state)) {
      throw new WorkspaceRuntimeStateError(this.state, operation);
    }
  }
}
