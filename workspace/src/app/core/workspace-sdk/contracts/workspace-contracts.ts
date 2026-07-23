/**
 * Deja Workspace UI SDK
 *
 * Contratos fundamentais compartilhados por todos os componentes
 * públicos do Workspace SDK.
 *
 * Este arquivo não deve depender de Angular, componentes visuais
 * ou implementações concretas do Workspace Runtime.
 */

/**
 * Identificador institucional de um recurso do Workspace.
 *
 * Exemplos:
 * - core.dashboard
 * - infrastructure.servers
 * - monitoring.cpu-widget
 */
export type WorkspaceResourceId = string;

/**
 * Identificador de um domínio registrado no Workspace.
 */
export type WorkspaceDomainId = WorkspaceResourceId;

/**
 * Identificador de uma view registrada no Workspace.
 */
export type WorkspaceViewId = WorkspaceResourceId;

/**
 * Identificador de uma entrada de navegação.
 */
export type WorkspaceNavigationId = WorkspaceResourceId;

/**
 * Identificador de um widget.
 */
export type WorkspaceWidgetId = WorkspaceResourceId;

/**
 * Categoria institucional de um Workspace Widget.
 *
 * Permite classificação, descoberta e organização sem impor
 * categorias específicas aos módulos da plataforma.
 */
export type WorkspaceWidgetCategory = string;

/**
 * Capacidade declarada por um Workspace Widget.
 *
 * As capacidades descrevem comportamentos suportados pelo Widget,
 * permanecendo independentes do mecanismo de renderização.
 */
export type WorkspaceWidgetCapability =
  | 'configurable'
  | 'refreshable'
  | 'resizable'
  | 'movable'
  | 'closable'
  | 'maximizable'
  | 'exportable'
  | 'interactive'
  | 'real-time';

/**
 * Superfície institucional na qual um Workspace Widget pode ser utilizado.
 */
export type WorkspaceWidgetSurface =
  | 'dashboard'
  | 'view'
  | 'panel'
  | 'shell'
  | 'dialog'
  | 'standalone';

/**
 * Dimensão institucional sugerida para um Workspace Widget.
 *
 * Não representa pixels ou qualquer unidade específica
 * do mecanismo de renderização.
 */
export interface WorkspaceWidgetSize {
  readonly columns: number;
  readonly rows: number;
}

/**
 * Restrições institucionais de dimensionamento de um Workspace Widget.
 */
export interface WorkspaceWidgetSizeConstraints {
  readonly default?: WorkspaceWidgetSize;
  readonly minimum?: WorkspaceWidgetSize;
  readonly maximum?: WorkspaceWidgetSize;
}

/**
 * Identificador de um dashboard.
 */
export type WorkspaceDashboardId = WorkspaceResourceId;

/**
 * Identificador de um serviço disponibilizado pelo Workspace.
 */
export type WorkspaceServiceId = WorkspaceResourceId;

/**
 * Identificador de uma extensão ou módulo proprietário do recurso.
 */
export type WorkspaceOwnerId = string;

/**
 * Identificador de uma instância criada em runtime.
 */
export type WorkspaceInstanceId = string;

/**
 * Estado institucional de um recurso no Workspace Runtime.
 */
export type WorkspaceResourceState =
  | 'registered'
  | 'active'
  | 'inactive'
  | 'disabled'
  | 'error';

/**
 * Estado do ciclo de vida do Workspace Runtime.
 */
export type WorkspaceRuntimeState =
  | 'created'
  | 'initializing'
  | 'ready'
  | 'running'
  | 'stopping'
  | 'stopped'
  | 'failed';

/**
 * Prioridade usada para ordenação determinística de recursos.
 *
 * Valores menores possuem precedência sobre valores maiores.
 */
export type WorkspacePriority = number;

/**
 * Metadados institucionais comuns aos recursos do Workspace.
 */
export interface WorkspaceResourceMetadata {
  /**
   * Identificador público e único do recurso.
   */
  readonly id: WorkspaceResourceId;

  /**
   * Nome legível apresentado na interface.
   */
  readonly title: string;

  /**
   * Descrição funcional opcional.
   */
  readonly description?: string;

  /**
   * Módulo, domínio ou extensão responsável pelo recurso.
   */
  readonly owner: WorkspaceOwnerId;

  /**
   * Versão do contrato ou recurso.
   */
  readonly version?: string;

  /**
   * Prioridade de registro, resolução ou apresentação.
   */
  readonly priority?: WorkspacePriority;

  /**
   * Indica se o recurso deve ser considerado habilitado.
   */
  readonly enabled?: boolean;

  /**
   * Tags usadas para descoberta, busca e classificação.
   */
  readonly tags?: readonly string[];
}

/**
 * Contrato básico para recursos registráveis no Workspace.
 */
export interface WorkspaceResource<
  TId extends WorkspaceResourceId = WorkspaceResourceId,
> {
  readonly id: TId;
  readonly owner: WorkspaceOwnerId;
  readonly enabled?: boolean;
  readonly priority?: WorkspacePriority;
}

/**
 * Resultado padronizado de operações do Workspace SDK.
 */
export interface WorkspaceOperationResult<T = void> {
  readonly success: boolean;
  readonly data?: T;
  readonly error?: WorkspaceOperationError;
}

/**
 * Erro institucional retornado por operações do Workspace SDK.
 */
export interface WorkspaceOperationError {
  readonly code: string;
  readonly message: string;
  readonly cause?: unknown;
  readonly context?: Readonly<Record<string, unknown>>;
}

/**
 * Opções comuns para consultas aos registries.
 */
export interface WorkspaceRegistryQuery {
  readonly owner?: WorkspaceOwnerId;
  readonly enabled?: boolean;
  readonly tags?: readonly string[];
}

/**
 * Contrato mínimo de um recurso descartável.
 */
export interface WorkspaceDisposable {
  dispose(): void | Promise<void>;
}

/**
 * Factory genérica para criação desacoplada de instâncias.
 */
export interface WorkspaceFactory<TInstance, TContext = void> {
  create(context: TContext): TInstance | Promise<TInstance>;
}
