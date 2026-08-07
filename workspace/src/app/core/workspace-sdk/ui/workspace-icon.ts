/*
 * Deja Workspace UI SDK
 *
 * Workspace Icon
 *
 * Contrato institucional utilizado para identificação
 * de ícones da plataforma.
 *
 * O Workspace Runtime nunca referencia arquivos físicos,
 * SVGs ou recursos específicos da interface. Toda resolução
 * visual é responsabilidade da camada de apresentação.
 */

export interface WorkspaceIcon {

  /**
   * Identificador institucional do ícone.
   *
   * Exemplos:
   *
   * dashboard
   * analytics
   * indicators
   * reports
   * users
   * settings
   */
  readonly id: string;

}