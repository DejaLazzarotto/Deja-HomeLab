/*
 * Deja Workspace Angular Integration
 *
 * Workspace Grid Item Directive
 *
 * Diretiva responsável pela interpretação visual institucional
 * da posição declarativa de uma instância de Workspace Widget.
 */

import {
  Directive,
  HostBinding,
  Input,
} from '@angular/core';

import {
  WorkspaceGridPosition,
} from '../../core/workspace-sdk/runtime/workspace-widget';

/**
 * Aplica posicionamento CSS Grid a um elemento visual
 * pertencente ao Workspace.
 *
 * A diretiva permanece independente do componente hospedado,
 * interpretando exclusivamente o contrato institucional
 * WorkspaceGridPosition.
 *
 * Widgets sem posição declarada permanecem sob responsabilidade
 * do posicionamento automático do CSS Grid.
 */
@Directive({
  selector: '[dejaWorkspaceGridItem]',
  standalone: true,
})
export class WorkspaceGridItemDirective {

  /**
   * Posição declarativa do item na grade.
   */
  @Input('dejaWorkspaceGridItem')
  position?: WorkspaceGridPosition;

  /**
   * Coluna inicial e quantidade de colunas ocupadas.
   */
  @HostBinding('style.grid-column')
  protected get gridColumn(): string | null {

    if (!this.position) {
      return null;
    }

    const column = this.normalizeIndex(
      this.position.column,
    );

    const columnSpan = this.normalizeSpan(
      this.position.columnSpan,
    );

    return `${column} / span ${columnSpan}`;

  }

  /**
   * Linha inicial e quantidade de linhas ocupadas.
   */
  @HostBinding('style.grid-row')
  protected get gridRow(): string | null {

    if (!this.position) {
      return null;
    }

    const row = this.normalizeIndex(
      this.position.row,
    );

    const rowSpan = this.normalizeSpan(
      this.position.rowSpan,
    );

    return `${row} / span ${rowSpan}`;

  }

  /**
   * Identifica visualmente um item posicionado
   * pelo Workspace Grid Renderer.
   */
  @HostBinding('attr.data-workspace-grid-positioned')
  protected get positionedAttribute(): string | null {

    return this.position
      ? 'true'
      : null;

  }

  /**
   * Normaliza índices de linha e coluna.
   *
   * CSS Grid utiliza índices iniciados em 1.
   */
  private normalizeIndex(
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

  /**
   * Normaliza a quantidade de linhas ou colunas ocupadas.
   */
  private normalizeSpan(
    value: number | undefined,
  ): number {

    if (
      value === undefined
      || !Number.isFinite(value)
      || value < 1
    ) {
      return 1;
    }

    return Math.trunc(value);

  }

}