/*
 * Deja Workspace Angular Integration
 *
 * Workspace Grid Foundation Component
 *
 * Infraestrutura institucional responsável pela composição
 * visual de conteúdos organizados em Grid.
 *
 * Este componente pertence exclusivamente à Deja UI Foundation.
 *
 * Não possui conhecimento sobre:
 *
 * - Widgets
 * - Dashboards
 * - Workspace Runtime
 * - Workspace SDK
 * - Layout Engine
 * - WorkspaceGridPosition
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

/**
 * Configurações institucionais de colunas suportadas
 * pelo WorkspaceGridComponent.
 *
 * "auto" utiliza distribuição responsiva automática.
 */
export type WorkspaceGridColumns =
  | 'auto'
  | 1
  | 2
  | 3
  | 4;

/**
 * Layouts proporcionais institucionais disponíveis.
 */
export type WorkspaceGridLayout =
  | 'equal'
  | 'content-sidebar';

/**
 * Espaçamentos institucionais disponíveis para grids.
 */
export type WorkspaceGridGap =
  | 'sm'
  | 'md'
  | 'lg';

/**
 * Alinhamentos institucionais disponíveis.
 */
export type WorkspaceGridAlignment =
  | 'start'
  | 'center'
  | 'stretch';

/**
 * Grid institucional da Deja UI Foundation.
 *
 * Responsabilidades:
 *
 * - centralizar definição de CSS Grid;
 * - padronizar espaçamentos;
 * - fornecer comportamento responsivo;
 * - centralizar alinhamento dos itens;
 * - oferecer layouts proporcionais institucionais;
 * - eliminar grids visuais duplicados em Widgets.
 *
 * O componente é intencionalmente agnóstico ao conteúdo.
 */
@Component({
  selector: 'deja-workspace-grid',
  standalone: true,
  templateUrl: './workspace-grid.html',
  styleUrl: './workspace-grid.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceGridComponent {

  /**
   * Estratégia de distribuição das colunas.
   *
   * "auto" representa o comportamento institucional padrão
   * e adapta automaticamente a quantidade de colunas
   * conforme o espaço disponível.
   */
  @Input()
  columns: WorkspaceGridColumns = 'auto';

  /**
   * Layout proporcional institucional.
   *
   * "equal":
   * distribui igualmente as colunas.
   *
   * "content-sidebar":
   * prioriza a área principal de conteúdo
   * em relação à área secundária.
   */
  @Input()
  layout: WorkspaceGridLayout = 'equal';

  /**
   * Espaçamento institucional entre células.
   */
  @Input()
  gap: WorkspaceGridGap = 'md';

  /**
   * Alinhamento vertical dos itens.
   */
  @Input()
  align: WorkspaceGridAlignment = 'stretch';
}