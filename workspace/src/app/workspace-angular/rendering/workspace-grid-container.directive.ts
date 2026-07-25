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
  Input,
} from '@angular/core';

import {
  WorkspaceGridConfiguration,
} from '../../core/workspace-sdk/runtime/workspace-grid-configuration';

/**
 * Configura um elemento visual como container institucional
 * do Workspace Grid Renderer.
 *
 * A diretiva encapsula completamente a infraestrutura CSS Grid,
 * permanecendo independente dos componentes responsáveis pela
 * composição dos Dashboards e Widgets.
 *
 * A configuração visual é recebida por contrato institucional,
 * permitindo integração com o Workspace Layout Engine,
 * redimensionamento, drag-and-drop e persistência de Layout.
 */
@Directive({
  selector: '[dejaWorkspaceGridContainer]',
  standalone: true,
})
export class WorkspaceGridContainerDirective {

  /**
   * Configuração resolvida do Workspace Grid.
   */
  @Input({
    alias: 'dejaWorkspaceGridContainer',
    required: true,
  })
  configuration!: WorkspaceGridConfiguration;

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
  protected get gridTemplateColumns(): string {

    const columns = this.normalizeColumns(
      this.configuration.columns,
    );

    return `repeat(${columns}, minmax(0, 1fr))`;

  }

  /**
   * Define a dimensão automática das linhas da grade.
   */
  @HostBinding('style.grid-auto-rows')
  protected get gridAutoRows(): string {

    return this.configuration.autoRowSize;

  }

  /**
   * Mantém o fluxo automático dos Widgets.
   */
  @HostBinding('style.grid-auto-flow')
  protected get gridAutoFlow(): string {

    return this.configuration.autoFlow ?? 'row dense';

  }

  /**
   * Define o espaçamento horizontal institucional.
   */
  @HostBinding('style.column-gap')
  protected get columnGap(): string {

    return this.configuration.columnGap;

  }

  /**
   * Define o espaçamento vertical institucional.
   */
  @HostBinding('style.row-gap')
  protected get rowGap(): string {

    return this.configuration.rowGap;

  }

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

  /**
   * Normaliza a quantidade de colunas do Grid.
   */
  private normalizeColumns(
    value: number,
  ): number {

    if (
      !Number.isFinite(value)
      || value < 1
    ) {
      return 1;
    }

    return Math.trunc(value);

  }

}