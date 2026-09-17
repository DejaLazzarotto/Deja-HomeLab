/*
 * Deja Fotos
 *
 * Media Grid
 *
 * Exibe as mídias, controla a seleção visual e administra
 * Object URLs das miniaturas autenticadas.
 */

import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  effect,
  input,
  output,
  signal,
} from '@angular/core';

import {
  Media,
} from '../../domain';

import {
  MediaService,
} from '../../application';

import {
  MEDIA_ORIGINAL_DATE_SOURCE_LABELS,
  MEDIA_PROCESSING_STATUS_LABELS,
  MEDIA_TYPE_LABELS,
  formatMediaDate,
  formatMediaDuration,
  formatMediaFileSize,
} from '../media-presentation';

@Component({
  selector: 'deja-media-grid',
  standalone: true,
  templateUrl: './media-grid.html',
  styleUrl: './media-grid.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MediaGridComponent implements OnDestroy {
  readonly items = input<readonly Media[]>([]);

  readonly service = input.required<MediaService>();

  readonly selectedIds = input<ReadonlySet<string>>(
    new Set<string>(),
  );

  readonly selectionChange = output<{
    readonly mediaId: string;
    readonly selected: boolean;
  }>();

  readonly pageSelectionChange = output<boolean>();

  protected readonly thumbnailUrls =
    signal<ReadonlyMap<string, string>>(
      new Map<string, string>(),
    );

  protected readonly thumbnailFailures =
    signal<ReadonlySet<string>>(
      new Set<string>(),
    );

  protected readonly typeLabels = MEDIA_TYPE_LABELS;

  protected readonly statusLabels =
    MEDIA_PROCESSING_STATUS_LABELS;

  protected readonly dateSourceLabels =
    MEDIA_ORIGINAL_DATE_SOURCE_LABELS;

  protected readonly formatDate = formatMediaDate;

  protected readonly formatFileSize = formatMediaFileSize;

  protected readonly formatDuration = formatMediaDuration;

  private readonly pendingThumbnailIds = new Set<string>();

  private destroyed = false;

  constructor() {
    effect(() => {
      this.synchronizeThumbnails(this.items());
    });
  }

  ngOnDestroy(): void {
    this.destroyed = true;

    for (
      const objectUrl
      of this.thumbnailUrls().values()
    ) {
      URL.revokeObjectURL(objectUrl);
    }
  }

  protected thumbnailUrl(
    mediaId: string,
  ): string | undefined {
    return this.thumbnailUrls().get(mediaId);
  }

  protected isSelected(
    mediaId: string,
  ): boolean {
    return this.selectedIds().has(mediaId);
  }

  protected allPageItemsSelected(): boolean {
    const items = this.items();

    return (
      items.length > 0
      && items.every(item => this.isSelected(item.id))
    );
  }

  protected somePageItemsSelected(): boolean {
    const items = this.items();

    return (
      !this.allPageItemsSelected()
      && items.some(item => this.isSelected(item.id))
    );
  }

  protected toggleSelection(
    mediaId: string,
    event: Event,
  ): void {
    const checkbox = event.target as HTMLInputElement;

    this.selectionChange.emit({
      mediaId,
      selected: checkbox.checked,
    });
  }

  protected togglePageSelection(
    event: Event,
  ): void {
    const checkbox = event.target as HTMLInputElement;

    this.pageSelectionChange.emit(checkbox.checked);
  }

  private synchronizeThumbnails(
    items: readonly Media[],
  ): void {
    const visibleIds = new Set(
      items.map(item => item.id),
    );

    const currentUrls = new Map(
      this.thumbnailUrls(),
    );

    let urlsChanged = false;

    for (
      const [mediaId, objectUrl]
      of currentUrls.entries()
    ) {
      if (!visibleIds.has(mediaId)) {
        URL.revokeObjectURL(objectUrl);
        currentUrls.delete(mediaId);
        urlsChanged = true;
      }
    }

    if (urlsChanged) {
      this.thumbnailUrls.set(currentUrls);
    }

    const currentFailures = new Set(
      this.thumbnailFailures(),
    );

    let failuresChanged = false;

    for (const mediaId of currentFailures) {
      if (!visibleIds.has(mediaId)) {
        currentFailures.delete(mediaId);
        failuresChanged = true;
      }
    }

    if (failuresChanged) {
      this.thumbnailFailures.set(currentFailures);
    }

    for (const media of items) {
      if (
        media.processingStatus === 'ready'
        && !currentUrls.has(media.id)
        && !currentFailures.has(media.id)
        && !this.pendingThumbnailIds.has(media.id)
      ) {
        void this.loadThumbnail(media.id);
      }
    }
  }

  private async loadThumbnail(
    mediaId: string,
  ): Promise<void> {
    this.pendingThumbnailIds.add(mediaId);

    try {
      const thumbnail = await this.service().loadThumbnail(
        mediaId,
      );

      if (
        this.destroyed
        || !this.items().some(item => item.id === mediaId)
      ) {
        return;
      }

      const objectUrl = URL.createObjectURL(thumbnail);

      this.thumbnailUrls.update(current => {
        const next = new Map(current);
        const previousUrl = next.get(mediaId);

        if (previousUrl) {
          URL.revokeObjectURL(previousUrl);
        }

        next.set(mediaId, objectUrl);

        return next;
      });
    } catch {
      if (!this.destroyed) {
        this.thumbnailFailures.update(current => {
          const next = new Set(current);

          next.add(mediaId);

          return next;
        });
      }
    } finally {
      this.pendingThumbnailIds.delete(mediaId);
    }
  }
}