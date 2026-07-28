/*
 * Deja Workspace Angular Integration
 *
 * Workspace Widget Render Controller
 *
 * Contrato responsável pelas operações concretas de
 * renderização de uma instância Angular de Widget.
 *
 * Esta infraestrutura pertence exclusivamente à camada
 * Angular e não faz parte da API pública do Workspace SDK.
 */

/**
 * Controlador responsável pela atualização incremental
 * de uma instância renderizada de Widget.
 */
export interface WorkspaceWidgetRenderController {

  /**
   * Atualiza a posição visual do Widget.
   */
  move(): boolean;

  /**
   * Atualiza o tamanho visual do Widget.
   */
  resize(): boolean;

  /**
   * Anexa o Widget à árvore de renderização.
   */
  attach(): boolean;

  /**
   * Remove o Widget da árvore de renderização.
   */
  destroy(): boolean;

}