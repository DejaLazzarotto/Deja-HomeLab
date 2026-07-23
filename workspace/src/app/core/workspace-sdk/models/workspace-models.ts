import {
  WorkspaceDomainId,
  WorkspaceNavigationId,
  WorkspaceOwnerId,
  WorkspacePriority,
  WorkspaceResourceMetadata,
  WorkspaceResourceState,
  WorkspaceRuntimeState,
  WorkspaceServiceId,
  WorkspaceViewId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceDashboard,
} from '../runtime/workspace-dashboard';

import {
  WorkspaceWidget,
} from '../runtime/workspace-widget';

/**
 * Reexportações mantidas para compatibilidade com os imports existentes.
 */
export type {
  WorkspaceDashboard,
} from '../runtime/workspace-dashboard';

export type {
  WorkspaceGridPosition,
  WorkspaceWidget,
  WorkspaceWidgetInstance,
} from '../runtime/workspace-widget';

/**
 * Representa um domínio funcional do Workspace.
 */
export interface WorkspaceDomain {
  readonly id: WorkspaceDomainId;
  readonly owner: WorkspaceOwnerId;
  readonly title: string;
  readonly description?: string;
  readonly icon?: string;
  readonly route?: string;
  readonly priority?: WorkspacePriority;
  readonly enabled?: boolean;
  readonly tags?: readonly string[];
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Representa uma view disponibilizada pelo Workspace.
 */
export interface WorkspaceView {
  readonly id: WorkspaceViewId;
  readonly domainId: WorkspaceDomainId;
  readonly owner: WorkspaceOwnerId;
  readonly title: string;
  readonly description?: string;
  readonly route: string;
  readonly icon?: string;
  readonly priority?: WorkspacePriority;
  readonly enabled?: boolean;
  readonly tags?: readonly string[];
  readonly component?: unknown;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Representa uma entrada da navegação principal ou contextual.
 */
export interface WorkspaceNavigationItem {
  readonly id: WorkspaceNavigationId;
  readonly owner: WorkspaceOwnerId;
  readonly title: string;
  readonly icon?: string;
  readonly route?: string;
  readonly viewId?: WorkspaceViewId;
  readonly parentId?: WorkspaceNavigationId;
  readonly priority?: WorkspacePriority;
  readonly enabled?: boolean;
  readonly visible?: boolean;
  readonly tags?: readonly string[];
  readonly children?: readonly WorkspaceNavigationItem[];
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Representa um serviço público do Workspace SDK.
 */
export interface WorkspaceServiceDefinition<TService = unknown> {
  readonly id: WorkspaceServiceId;
  readonly owner: WorkspaceOwnerId;
  readonly version?: string;
  readonly priority?: WorkspacePriority;
  readonly enabled?: boolean;
  readonly factory: () => TService | Promise<TService>;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Registro interno de um recurso gerenciado pelo runtime.
 */
export interface WorkspaceResourceRecord<TResource> {
  readonly resource: TResource;
  readonly state: WorkspaceResourceState;
  readonly registeredAt: Date;
  readonly activatedAt?: Date;
  readonly error?: unknown;
}

/**
 * Snapshot imutável do Workspace Runtime.
 */
export interface WorkspaceRuntimeSnapshot {
  readonly state: WorkspaceRuntimeState;
  readonly initializedAt?: Date;
  readonly startedAt?: Date;
  readonly stoppedAt?: Date;
  readonly domains: number;
  readonly views: number;
  readonly navigationItems: number;
  readonly widgets: number;
  readonly dashboards: number;
  readonly services: number;
}

/**
 * Contexto público disponibilizado durante a inicialização.
 */
export interface WorkspaceRuntimeContext {
  readonly applicationId: string;
  readonly environment: string;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Manifesto agregado de recursos disponibilizados por um módulo.
 */
export interface WorkspaceModuleManifest {
  readonly metadata: WorkspaceResourceMetadata;
  readonly domains?: readonly WorkspaceDomain[];
  readonly views?: readonly WorkspaceView[];
  readonly navigation?: readonly WorkspaceNavigationItem[];
  readonly widgets?: readonly WorkspaceWidget[];
  readonly dashboards?: readonly WorkspaceDashboard[];
  readonly services?: readonly WorkspaceServiceDefinition[];
}
