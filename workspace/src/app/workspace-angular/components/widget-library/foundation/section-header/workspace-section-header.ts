/*
 * Deja Workspace Angular Integration
 *
 * Workspace Section Header Component
 *
 * Componente institucional reutilizável responsável pela
 * apresentação de cabeçalhos semânticos de seções e Widgets
 * dentro da Deja Platform.
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
  eyebrow = '';

  @Input()
  title = '';

  @Input()
  subtitle = '';

  @Input()
  description = '';

}