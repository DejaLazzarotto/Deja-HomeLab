/*
 * Deja Workspace UI SDK
 *
 * Workspace Layout Capabilities
 *
 * Contrato institucional responsável pelas capacidades
 * declarativas suportadas por um Workspace Layout.
 */

/**
 * Capacidades declarativas de um Workspace Layout.
 *
 * As capacidades descrevem quais comportamentos um Layout
 * suporta, permanecendo independentes da infraestrutura
 * responsável pela sua implementação.
 */
export interface WorkspaceLayoutCapabilities {

  /**
   * Permite o redimensionamento dos Widgets.
   */
  readonly resizable?: boolean;

  /**
   * Permite a movimentação dos Widgets.
   */
  readonly movable?: boolean;

  /**
   * Permite comportamento responsivo.
   */
  readonly responsive?: boolean;

  /**
   * Permite edição do Layout.
   */
  readonly editable?: boolean;

}