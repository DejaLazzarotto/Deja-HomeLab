/*
 * Deja Workspace Angular Integration
 *
 * Workspace Root Component
 *
 * Componente raiz responsável por hospedar a árvore visual do
 * Workspace. Atua como ponto de entrada da renderização Angular,
 * permanecendo desacoplado do Workspace SDK.
 */

import {
  ChangeDetectionStrategy,
  Component,
} from '@angular/core';

@Component({
  selector: 'deja-workspace-root',
  standalone: true,
  templateUrl: './workspace-root.html',
  styleUrl: './workspace-root.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceRootComponent {}