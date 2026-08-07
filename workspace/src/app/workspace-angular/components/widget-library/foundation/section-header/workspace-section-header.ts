/*
 * Deja Workspace Angular Integration
 *
 * Workspace Section Header Component
 *
 * Cabeçalho institucional reutilizável utilizado para estruturar
 * títulos, descrições, indicadores, badges e ações em Widgets.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

@Component({
  selector: 'deja-section-header',
  standalone: true,
  templateUrl: './workspace-section-header.html',
  styleUrl: './workspace-section-header.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceSectionHeaderComponent {

  @Input()
  title = '';

  @Input()
  subtitle = '';

  @Input()
  description = '';

}