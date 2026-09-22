/*
 * Deja Fotos
 *
 * Media Bulk Actions
 */

import {
  ChangeDetectionStrategy,
  Component,
  input,
  output,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  Album,
} from '../../../albums';

export type MediaBulkActionsMode =
  | 'curation'
  | 'album_organization';

export type MediaBulkActionRequest =
  | {
      readonly operation: 'set_original_date';
      readonly originalDate: string;
    }
  | {
      readonly operation: 'verify_original_date';
    }
  | {
      readonly operation: 'clear_original_date_conflict';
    }
  | {
      readonly operation: 'set_album';
      readonly albumId: string | null;
    };

@Component({
  selector: 'deja-media-bulk-actions',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './media-bulk-actions.html',
  styleUrl: './media-bulk-actions.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MediaBulkActionsComponent {
  readonly mode =
    input<MediaBulkActionsMode>('curation');

  readonly selectedCount = input(0);

  readonly albums = input<readonly Album[]>([]);

  readonly busy = input(false);

  readonly actionRequested =
    output<MediaBulkActionRequest>();

  readonly clearSelectionRequested =
    output<void>();

  protected readonly originalDate = signal('');

  protected readonly albumSelection = signal('');

  protected readonly dateEditorVisible = signal(false);

  protected readonly albumEditorVisible = signal(false);

  protected readonly validationMessage =
    signal<string | null>(null);

  protected toggleDateEditor(): void {
    this.dateEditorVisible.update(visible => !visible);
    this.albumEditorVisible.set(false);
    this.validationMessage.set(null);
  }

  protected toggleAlbumEditor(): void {
    this.albumEditorVisible.update(visible => !visible);
    this.dateEditorVisible.set(false);
    this.validationMessage.set(null);
  }

  protected clearSelection(): void {
    this.dateEditorVisible.set(false);
    this.albumEditorVisible.set(false);
    this.validationMessage.set(null);
    this.clearSelectionRequested.emit();
  }

  protected applyOriginalDate(): void {
    const value = this.originalDate();

    if (!value) {
      this.validationMessage.set(
        'Informe a nova data original.',
      );

      return;
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      this.validationMessage.set(
        'Informe uma data original válida.',
      );

      return;
    }

    this.validationMessage.set(null);
    this.dateEditorVisible.set(false);

    this.actionRequested.emit({
      operation: 'set_original_date',
      originalDate: `${value}:00`,
    });
  }

  protected verifyOriginalDate(): void {
    this.validationMessage.set(null);

    this.actionRequested.emit({
      operation: 'verify_original_date',
    });
  }

  protected clearOriginalDateConflict(): void {
    this.validationMessage.set(null);

    this.actionRequested.emit({
      operation: 'clear_original_date_conflict',
    });
  }

  protected setAlbum(): void {
    const value = this.albumSelection();

    if (!value) {
      this.validationMessage.set(
        'Selecione um álbum ou a opção de remover associação.',
      );

      return;
    }

    this.validationMessage.set(null);
    this.albumEditorVisible.set(false);

    this.actionRequested.emit({
      operation: 'set_album',
      albumId: value === '__without_album__'
        ? null
        : value,
    });
  }
}
