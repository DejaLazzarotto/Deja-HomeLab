import {
  WorkspaceOwnerId,
} from '../contracts/workspace-contracts';

/**
 * Identificador oficial de um Workspace Command.
 *
 * Convenção recomendada:
 *
 * owner.resource.action
 *
 * Exemplos:
 *
 * workspace.navigation.open
 * infrastructure.server.restart
 * website.deployment.publish
 */
export type WorkspaceCommandId = string;

/**
 * Origem responsável por solicitar a execução do comando.
 */
export type WorkspaceCommandSource =
  | 'runtime'
  | 'module'
  | 'toolbar'
  | 'menu'
  | 'context-menu'
  | 'command-palette'
  | 'action'
  | 'keyboard'
  | 'api'
  | 'unknown';

/**
 * Contexto disponibilizado durante a execução de um comando.
 */
export interface WorkspaceCommandContext<
  TPayload = unknown,
> {
  /**
   * Identificador do comando executado.
   */
  readonly commandId: WorkspaceCommandId;

  /**
   * Módulo ou componente responsável pelo comando.
   */
  readonly ownerId: WorkspaceOwnerId;

  /**
   * Origem que solicitou a execução.
   */
  readonly source: WorkspaceCommandSource;

  /**
   * Dados enviados para o comando.
   */
  readonly payload: TPayload;

  /**
   * Instante em que a execução foi solicitada.
   */
  readonly requestedAt: Date;

  /**
   * Metadados adicionais da execução.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Resultado oficial da execução de um Workspace Command.
 */
export interface WorkspaceCommandResult<
  TValue = unknown,
> {
  /**
   * Indica se o comando foi executado com sucesso.
   */
  readonly success: boolean;

  /**
   * Valor retornado pelo comando.
   */
  readonly value?: TValue;

  /**
   * Mensagem associada ao resultado.
   */
  readonly message?: string;

  /**
   * Erro gerado durante a execução.
   */
  readonly error?: unknown;

  /**
   * Instante em que a execução terminou.
   */
  readonly completedAt: Date;
}

/**
 * Função responsável pela execução de um comando.
 */
export type WorkspaceCommandHandler<
  TPayload = unknown,
  TResult = unknown,
> = (
  context: WorkspaceCommandContext<TPayload>,
) =>
  | WorkspaceCommandResult<TResult>
  | Promise<WorkspaceCommandResult<TResult>>
  | TResult
  | Promise<TResult>;

/**
 * Função responsável por determinar se um comando pode ser executado.
 */
export type WorkspaceCommandCanExecute<
  TPayload = unknown,
> = (
  context: WorkspaceCommandContext<TPayload>,
) => boolean | Promise<boolean>;

/**
 * Definição oficial de um Workspace Command.
 */
export interface WorkspaceCommand<
  TPayload = unknown,
  TResult = unknown,
> {
  /**
   * Identificador único do comando.
   */
  readonly id: WorkspaceCommandId;

  /**
   * Módulo ou componente proprietário do comando.
   */
  readonly ownerId: WorkspaceOwnerId;

  /**
   * Nome apresentado nas interfaces gráficas.
   */
  readonly label: string;

  /**
   * Descrição funcional do comando.
   */
  readonly description?: string;

  /**
   * Nome ou identificador visual do ícone.
   */
  readonly icon?: string;

  /**
   * Atalho de teclado sugerido.
   */
  readonly shortcut?: string;

  /**
   * Palavras utilizadas por mecanismos de busca e Command Palette.
   */
  readonly keywords?: readonly string[];

  /**
   * Categoria utilizada por menus e Command Palette.
   */
  readonly category?: string;

  /**
   * Ordem visual sugerida.
   */
  readonly order?: number;

  /**
   * Determina se o comando está visível.
   */
  readonly visible?: boolean;

  /**
   * Determina se o comando está habilitado por padrão.
   */
  readonly enabled?: boolean;

  /**
   * Avaliação dinâmica de disponibilidade.
   */
  readonly canExecute?: WorkspaceCommandCanExecute<TPayload>;

  /**
   * Implementação responsável pela execução.
   */
  readonly execute: WorkspaceCommandHandler<TPayload, TResult>;

  /**
   * Metadados adicionais definidos pelo proprietário.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}

/**
 * Solicitação de execução de um Workspace Command.
 */
export interface WorkspaceCommandExecution<
  TPayload = unknown,
> {
  /**
   * Identificador do comando.
   */
  readonly commandId: WorkspaceCommandId;

  /**
   * Dados enviados para o comando.
   */
  readonly payload?: TPayload;

  /**
   * Origem da execução.
   */
  readonly source?: WorkspaceCommandSource;

  /**
   * Metadados adicionais da solicitação.
   */
  readonly metadata?: Readonly<Record<string, unknown>>;
}