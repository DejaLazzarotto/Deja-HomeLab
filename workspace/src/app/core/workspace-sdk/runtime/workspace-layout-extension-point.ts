/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Extension Point
 *
 * Contratos institucionais responsáveis pela definição
 * das extensões do Workspace Layout.
 */

import {
  WorkspaceOwnerId,
  WorkspacePriority,
  WorkspaceResourceId,
} from '../contracts/workspace-contracts';

/**
 * Identificador público de um ponto de extensão
 * do Workspace Layout.
 */
export type WorkspaceLayoutExtensionPointId =
  WorkspaceResourceId;

/**
 * Identificador único de uma extensão de Layout.
 */
export type WorkspaceLayoutExtensionId =
  WorkspaceResourceId;

/**
 * Contexto fornecido durante a execução de uma
 * Workspace Layout Extension.
 */
export interface WorkspaceLayoutExtensionContext<
  TPayload = unknown,
> {

  /**
   * Ponto de extensão atualmente executado.
   */
  readonly extensionPoint:
    WorkspaceLayoutExtensionPointId;

  /**
   * Dados fornecidos pelo chamador.
   */
  readonly payload: TPayload;

}

/**
 * Handler executável de uma Workspace Layout Extension.
 */
export type WorkspaceLayoutExtensionHandler<
  TPayload = unknown,
  TResult = unknown,
> = (
  context: WorkspaceLayoutExtensionContext<TPayload>,
) => TResult | Promise<TResult>;

/**
 * Extensão concreta registrada em um ponto de extensão
 * do Workspace Layout.
 */
export interface WorkspaceLayoutExtension<
  TPayload = unknown,
  TResult = unknown,
> {

  /**
   * Identificador público e único da extensão.
   */
  readonly id: WorkspaceLayoutExtensionId;

  /**
   * Ponto de extensão ao qual esta implementação pertence.
   */
  readonly extensionPoint:
    WorkspaceLayoutExtensionPointId;

  /**
   * Módulo, domínio ou extensão proprietária.
   */
  readonly owner: WorkspaceOwnerId;

  /**
   * Prioridade de execução.
   *
   * Valores menores são executados primeiro.
   */
  readonly priority?: WorkspacePriority;

  /**
   * Indica se a extensão está habilitada.
   *
   * Quando omitido, considera-se habilitada.
   */
  readonly enabled?: boolean;

  /**
   * Handler executado pelo dispatcher.
   */
  readonly handler:
    WorkspaceLayoutExtensionHandler<TPayload, TResult>;

}