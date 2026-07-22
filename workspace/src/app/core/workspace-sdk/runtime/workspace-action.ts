import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';

import {
  WorkspaceCommandId,
} from './workspace-command';

/**
 * Identificador oficial de uma Workspace Action.
 *
 * Convenção recomendada:
 *
 * owner.area.action
 *
 * Exemplos:
 *
 * toolbar.file.save
 * menu.file.open
 * context.copy
 * widget.refresh
 * dashboard.export
 */
export type WorkspaceActionId = string;

/**
 * Origem responsável por solicitar a execução da Action.
 */
export type WorkspaceActionSource =
  | 'runtime'
  | 'toolbar'
  | 'menu'
  | 'context-menu'
  | 'widget'
  | 'dashboard'
  | 'command-palette'
  | 'keyboard'
  | 'api'
  | 'unknown';

/**
 * Contexto oficial de execução de uma Workspace Action.
 */
export interface WorkspaceActionContext<
  TPayload = unknown,
> {
  /**
   * Identificador da Action.
   */
  readonly actionId: WorkspaceActionId;

  /**
   * Proprietário da Action.
   */
  readonly ownerId: WorkspaceOwnerId;

  /**
   * Origem da execução.
   */
  readonly source: WorkspaceActionSource;

  /**
   * Dados enviados para execução.
   */
  readonly payload: TPayload;

  /**
   * Instante em que a execução foi solicitada.
   */
  readonly requestedAt: Date;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Resultado oficial de uma Workspace Action.
 */
export interface WorkspaceActionResult<
  TValue = unknown,
> {
  /**
   * Indica se a execução foi concluída com sucesso.
   */
  readonly success: boolean;

  /**
   * Valor retornado.
   */
  readonly value?: TValue;

  /**
   * Mensagem associada ao resultado.
   */
  readonly message?: string;

  /**
   * Erro ocorrido durante a execução.
   */
  readonly error?: unknown;

  /**
   * Instante da conclusão.
   */
  readonly completedAt: Date;
}

/**
 * Implementação responsável pela execução da Action.
 */
export type WorkspaceActionHandler<
  TPayload = unknown,
  TResult = unknown,
> = (
  context: WorkspaceActionContext<TPayload>,
) =>
  | WorkspaceActionResult<TResult>
  | Promise<WorkspaceActionResult<TResult>>
  | TResult
  | Promise<TResult>;

/**
 * Avaliação dinâmica da disponibilidade da Action.
 */
export type WorkspaceActionCanExecute<
  TPayload = unknown,
> = (
  context: WorkspaceActionContext<TPayload>,
) => boolean | Promise<boolean>;

/**
 * Definição oficial de uma Workspace Action.
 *
 * Uma Action representa uma interação da interface do Workspace.
 * Opcionalmente pode estar associada a um Workspace Command.
 */
export interface WorkspaceAction<
  TPayload = unknown,
  TResult = unknown,
> {
  /**
   * Identificador único.
   */
  readonly id: WorkspaceActionId;

  /**
   * Proprietário.
   */
  readonly ownerId: WorkspaceOwnerId;

  /**
   * Nome apresentado na interface.
   */
  readonly label: string;

  /**
   * Descrição funcional.
   */
  readonly description?: string;

  /**
   * Ícone apresentado pela interface.
   */
  readonly icon?: string;

  /**
   * Atalho sugerido.
   */
  readonly shortcut?: string;

  /**
   * Categoria utilizada pela interface.
   */
  readonly category?: string;

  /**
   * Palavras utilizadas pela busca.
   */
  readonly keywords?: readonly string[];

  /**
   * Ordem visual.
   */
  readonly order?: number;

  /**
   * Determina se a Action está visível.
   */
  readonly visible?: boolean;

  /**
   * Determina se a Action está habilitada.
   */
  readonly enabled?: boolean;

  /**
   * Command associado.
   *
   * Quando informado, o Dispatcher poderá encaminhar
   * automaticamente a execução para o Workspace Command.
   */
  readonly commandId?: WorkspaceCommandId;

  /**
   * Avaliação dinâmica da disponibilidade.
   */
  readonly canExecute?: WorkspaceActionCanExecute<TPayload>;

  /**
   * Handler próprio da Action.
   *
   * Caso commandId seja informado, este handler torna-se opcional.
   */
  readonly execute?: WorkspaceActionHandler<
    TPayload,
    TResult
  >;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Solicitação oficial de execução.
 */
export interface WorkspaceActionExecution<
  TPayload = unknown,
> {
  /**
   * Action a ser executada.
   */
  readonly actionId: WorkspaceActionId;

  /**
   * Dados enviados.
   */
  readonly payload?: TPayload;

  /**
   * Origem da execução.
   */
  readonly source?: WorkspaceActionSource;

  /**
   * Metadados adicionais.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}
