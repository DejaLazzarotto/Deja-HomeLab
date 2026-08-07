/*
 * Deja Workspace Angular Presentation
 *
 * Workspace Panel Component
 *
 * Superfície institucional fundamental da Deja UI Foundation.
 *
 * O WorkspacePanelComponent fornece exclusivamente estrutura visual,
 * estados e composição através de Content Projection.
 *
 * O componente não possui conhecimento sobre Widgets, Dashboards,
 * Runtime, dados ou regras de negócio.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';


/**
 * Níveis institucionais de elevação disponíveis para Panels.
 */
export type WorkspacePanelElevation =
  | 'none'
  | 'sm'
  | 'md'
  | 'lg';


/**
 * Espaçamentos internos institucionais disponíveis para Panels.
 */
export type WorkspacePanelPadding =
  | 'none'
  | 'sm'
  | 'md'
  | 'lg';


/**
 * Superfície visual fundamental da Deja UI Foundation.
 *
 * Responsabilidades:
 *
 * - superfície institucional;
 * - borda;
 * - radius;
 * - elevação;
 * - espaçamento;
 * - estados visuais;
 * - slots de Header, Content e Footer.
 *
 * O conteúdo é fornecido exclusivamente por Content Projection.
 */
@Component({
  selector: 'workspace-panel',
  standalone: true,
  templateUrl: './workspace-panel.html',
  styleUrl: './workspace-panel.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspacePanelComponent {

  /**
   * Nível visual de elevação.
   */
  @Input()
  elevation: WorkspacePanelElevation = 'sm';


  /**
   * Espaçamento interno aplicado ao conteúdo principal.
   */
  @Input()
  padding: WorkspacePanelPadding = 'md';


  /**
   * Habilita feedback visual de interação.
   *
   * Não adiciona comportamento ou eventos.
   */
  @Input()
  interactive = false;


  /**
   * Controla a presença da borda institucional.
   */
  @Input()
  bordered = true;


  /**
   * Representa estado selecionado.
   */
  @Input()
  selected = false;


  /**
   * Representa estado desabilitado.
   */
  @Input()
  disabled = false;


  /**
   * Representa estado de carregamento.
   *
   * Nesta primeira versão o estado é apenas semântico e visual.
   * Nenhum spinner ou conteúdo específico é imposto pelo Foundation.
   */
  @Input()
  loading = false;

}