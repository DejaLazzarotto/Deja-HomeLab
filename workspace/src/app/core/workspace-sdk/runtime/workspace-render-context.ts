/*
 * Deja Workspace UI SDK
 *
 * Workspace Render Context Contracts
 *
 * Contrato institucional responsável por representar o contexto
 * utilizado durante a renderização de um Workspace.
 */

 /**
  * Tecnologias de renderização oficialmente suportadas.
  */
export type WorkspaceRenderTechnology =
  | 'angular'
  | 'web-components'
  | 'electron'
  | 'test';

/**
 * Contexto institucional de renderização.
 *
 * Este contrato encapsula todas as informações necessárias
 * para que um Renderer possa produzir uma representação visual,
 * permanecendo completamente desacoplado da lógica do Workspace.
 */
export interface WorkspaceRenderContext {

  /**
   * Tecnologia responsável pela renderização.
   */
  readonly technology: WorkspaceRenderTechnology;

  /**
   * Elemento raiz onde ocorrerá a renderização.
   *
   * O tipo permanece propositalmente genérico para evitar
   * dependência direta de Angular, DOM ou Electron.
   */
  readonly host: unknown;

  /**
   * Idioma utilizado durante a renderização.
   */
  readonly locale?: string;

  /**
   * Tema visual ativo.
   */
  readonly theme?: string;

  /**
   * Escala visual.
   */
  readonly scale?: number;

  /**
   * Parâmetros adicionais específicos do Renderer.
   */
  readonly parameters?: Readonly<Record<string, unknown>>;
}