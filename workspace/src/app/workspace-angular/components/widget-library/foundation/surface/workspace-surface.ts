/*
 * Deja Workspace Angular Integration
 *
 * Workspace Surface Foundation Component
 *
 * Superfície visual institucional da Deja UI Foundation.
 *
 * Responsável por centralizar:
 *
 * - background;
 * - border;
 * - radius;
 * - padding;
 * - shadow;
 * - estados visuais de elevação.
 *
 * O componente é agnóstico ao conteúdo renderizado.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

export type WorkspaceSurfaceVariant =
  | 'default'
  | 'subtle'
  | 'card'
  | 'accent';

export type WorkspaceSurfacePadding =
  | 'none'
  | 'sm'
  | 'md'
  | 'lg';

export type WorkspaceSurfaceRadius =
  | 'sm'
  | 'md'
  | 'lg';

export type WorkspaceSurfaceElevation =
  | 'none'
  | 'sm'
  | 'md';

@Component({
  selector: 'deja-workspace-surface',
  standalone: true,
  templateUrl: './workspace-surface.html',
  styleUrl: './workspace-surface.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceSurfaceComponent {

  @Input()
  variant: WorkspaceSurfaceVariant = 'default';

  @Input()
  padding: WorkspaceSurfacePadding = 'md';

  @Input()
  radius: WorkspaceSurfaceRadius = 'md';

  @Input()
  elevation: WorkspaceSurfaceElevation = 'none';
}