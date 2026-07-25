/*
 * Deja Workspace Angular Integration
 *
 * Workspace Grid Container Directive
 *
 * Diretiva responsável pela configuração visual institucional
 * dos containers utilizados pelo Workspace Grid Renderer.
 */

import {
  Directive,
  HostBinding,
} from '@angular/core';

/**
 * Configura um elemento visual como container institucional
 * do Workspace Grid Renderer.
 *
 * A diretiva encapsula completamente a infraestrutura CSS Grid,
 * permanecendo independente dos componentes responsáveis pela
 * composição dos Dashboards e Widgets.
 *
 * A configuração visual utiliza variáveis CSS institucionais,
 * permitindo futuras integrações com o Workspace Layout Engine,
 * redimensionamento, drag-and-drop e persistência de Layout.
 */
@Directive({
  selector: '[dejaWorkspaceGridContainer]',
  standalone: true,
})
export class WorkspaceGridContainerDirective {

  /**
   * Identifica o elemento como container institucional
   * do Workspace Grid Renderer.
   */
  @HostBinding('attr.data-workspace-grid')
  protected readonly workspaceGridAttribute = 'true';

  /**
   * Ativa o CSS Grid no elemento hospedeiro.
   */
  @HostBinding('style.display')
  protected readonly display = 'grid';

  /**
   * Define a quantidade institucional de colunas da grade.
   */
  @HostBinding('style.grid-template-columns')
  protected readonly gridTemplateColumns =
    'repeat(var(--workspace-grid-columns), minmax(0, 1fr))';

  /**
   * Define a dimensão automática das linhas da grade.
   */
  @HostBinding('style.grid-auto-rows')
  protected readonly gridAutoRows =
    'var(--workspace-grid-auto-row-size)';

  /**
   * Mantém o fluxo automático dos Widgets,
   * preenchendo espaços disponíveis quando possível.
   */
  @HostBinding('style.grid-auto-flow')
  protected readonly gridAutoFlow = 'row dense';

  /**
   * Define o espaçamento horizontal institucional.
   */
  @HostBinding('style.column-gap')
  protected readonly columnGap =
    'var(--workspace-grid-column-gap)';

  /**
   * Define o espaçamento vertical institucional.
   */
  @HostBinding('style.row-gap')
  protected readonly rowGap =
    'var(--workspace-grid-row-gap)';

  /**
   * Faz os itens ocuparem integralmente a área disponível.
   */
  @HostBinding('style.align-items')
  protected readonly alignItems = 'stretch';

  /**
   * Permite que o container ocupe o espaço flexível disponível.
   */
  @HostBinding('style.flex')
  protected readonly flex = '1';

  /**
   * Evita estouro horizontal em containers flexíveis.
   */
  @HostBinding('style.min-width')
  protected readonly minWidth = '0';

  /**
   * Evita estouro vertical em containers flexíveis.
   */
  @HostBinding('style.min-height')
  protected readonly minHeight = '0';

}