/*
 * Deja Fotos
 *
 * Curation Management
 */

import {
  ChangeDetectionStrategy,
  Component,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

type CurationTab =
  | 'recognition'
  | 'people'
  | 'avatars';

@Component({
  selector: 'deja-curation-management',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './curation-management.html',
  styleUrl: './curation-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CurationManagementComponent {
  readonly activeTab =
    signal<CurationTab>('recognition');

  readonly situationFilter = signal('all');

  readonly personFilter = signal('');

  readonly albumFilter = signal('');

  readonly periodFilter = signal('');

  readonly filterMessage =
    signal<string | null>(null);

  selectTab(tab: CurationTab): void {
    this.activeTab.set(tab);
    this.filterMessage.set(null);
  }

  applyFilters(): void {
    this.filterMessage.set(
      'Filtros aplicados. Nenhuma mídia aguarda revisão.',
    );
  }
}