/*
 * Deja Fotos
 *
 * Album Management
 */

import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  computed,
  input,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  FotosEnvironmentOption,
} from '../../../fotos-environment-option';

import {
  Media,
  MediaService,
  formatMediaDate,
  formatMediaDuration,
} from '../../../media';

import {
  AlbumService,
} from '../../application';

import {
  Album,
  AlbumInput,
} from '../../domain';

import {
  AlbumFormComponent,
} from '../album-form/album-form';

interface AlbumMediaPeriod {
  readonly key: string;
  readonly label: string;
  readonly sortValue: number;
  readonly items: readonly Media[];
}

const ALBUM_MEDIA_PAGE_SIZE = 100;

@Component({
  selector: 'deja-album-management',
  standalone: true,
  imports: [
    FormsModule,
    AlbumFormComponent,
  ],
  templateUrl: './album-management.html',
  styleUrl: './album-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlbumManagementComponent
  implements OnDestroy, OnInit {
  readonly service = input.required<AlbumService>();

  readonly mediaService =
    input.required<MediaService>();

  readonly environments =
    input<readonly FotosEnvironmentOption[]>([]);

  readonly defaultEnvironmentId =
    input<string | null>(null);

  readonly canEdit = input(false);

  readonly canDelete = input(false);

  readonly albums = signal<readonly Album[]>([]);

  readonly photoCount = signal(0);

  readonly videoCount = signal(0);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly deletingAlbumId =
    signal<string | null>(null);

  readonly errorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  readonly operationError =
    signal<string | null>(null);


  readonly selectedAlbum =
    signal<Album | null>(null);

  readonly selectedDashboardAlbumId = signal('');

  readonly formVisible = signal(false);

  readonly albumMedia = signal<readonly Media[]>([]);

  readonly albumMediaTotal = signal(0);

  readonly albumMediaPage = signal(0);

  readonly albumMediaLoading = signal(false);

  readonly albumMediaLoadingMore = signal(false);

  readonly albumMediaError =
    signal<string | null>(null);

  readonly expandedPeriodKeys =
    signal<ReadonlySet<string>>(
      new Set<string>(),
    );

  protected readonly thumbnailUrls =
    signal<ReadonlyMap<string, string>>(
      new Map<string, string>(),
    );

  protected readonly thumbnailFailures =
    signal<ReadonlySet<string>>(
      new Set<string>(),
    );

  protected readonly formatMediaDate =
    formatMediaDate;

  protected readonly formatMediaDuration =
    formatMediaDuration;

  readonly activeAlbums = computed(() => (
    this.albums().filter(album => album.active)
  ));

  readonly selectedDashboardAlbum = computed(() => {
    const albumId = this.selectedDashboardAlbumId();

    if (!albumId) {
      return null;
    }

    return this.albums().find(
      album => album.id === albumId,
    ) ?? null;
  });

  readonly albumMediaPeriods = computed(() => (
    this.buildMediaPeriods(this.albumMedia())
  ));

  readonly albumMediaHasMore = computed(() => (
    this.albumMedia().length < this.albumMediaTotal()
  ));

  private readonly pendingThumbnailIds =
    new Set<string>();

  private requestSequence = 0;

  private mediaRequestSequence = 0;

  private destroyed = false;

  ngOnInit(): void {
    void this.refresh();
    void this.loadMediaSummary();
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.clearThumbnailUrls();
  }

  async refresh(): Promise<void> {
    const requestSequence =
      this.requestSequence + 1;

    this.requestSequence = requestSequence;

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const albums = await this.service().list({});

      if (requestSequence === this.requestSequence) {
        this.albums.set(albums);

        const selectedAlbumId =
          this.selectedDashboardAlbumId();

        if (
          selectedAlbumId
          && !albums.some(
            album => album.id === selectedAlbumId,
          )
        ) {
          this.selectedDashboardAlbumId.set('');
        }
      }
    } catch {
      if (requestSequence === this.requestSequence) {
        this.errorMessage.set(
          'Não foi possível carregar os álbuns.',
        );
      }
    } finally {
      if (requestSequence === this.requestSequence) {
        this.loading.set(false);
      }
    }
  }

  selectDashboardAlbum(
    albumId: string,
  ): void {
    this.selectedDashboardAlbumId.set(albumId);
    this.resetAlbumMedia();

    if (albumId) {
      void this.loadSelectedAlbumMedia(true);
    }
  }

  async loadMoreAlbumMedia(): Promise<void> {
    if (
      !this.albumMediaHasMore()
      || this.albumMediaLoading()
      || this.albumMediaLoadingMore()
    ) {
      return;
    }

    await this.loadSelectedAlbumMedia(false);
  }

  retryAlbumMedia(): void {
    void this.loadSelectedAlbumMedia(true);
  }

  togglePeriod(
    periodKey: string,
  ): void {
    this.expandedPeriodKeys.update(current => {
      const next = new Set(current);

      if (next.has(periodKey)) {
        next.delete(periodKey);
      } else {
        next.add(periodKey);
      }

      return next;
    });
  }

  periodExpanded(
    periodKey: string,
  ): boolean {
    return this.expandedPeriodKeys().has(periodKey);
  }

  protected thumbnailUrl(
    mediaId: string,
  ): string | undefined {
    return this.thumbnailUrls().get(mediaId);
  }

  openCreate(): void {
    if (!this.canEdit()) {
      return;
    }

    this.selectedAlbum.set(null);
    this.clearOperationMessages();
    this.formVisible.set(true);
    this.scrollToForm();
  }

  openEdit(
    album: Album,
  ): void {
    if (!this.canEdit()) {
      return;
    }

    this.selectedAlbum.set(album);
    this.clearOperationMessages();
    this.formVisible.set(true);
    this.scrollToForm();
  }

  closeForm(): void {
    if (this.saving()) {
      return;
    }

    this.selectedAlbum.set(null);
    this.formVisible.set(false);
  }

  async saveAlbum(
    input: AlbumInput,
  ): Promise<void> {
    if (
      !this.canEdit()
      || this.saving()
    ) {
      return;
    }

    this.saving.set(true);
    this.clearOperationMessages();

    try {
      const selectedAlbum =
        this.selectedAlbum();

      if (selectedAlbum) {
        await this.service().update(
          selectedAlbum.id,
          input,
        );

        this.operationMessage.set(
          'Álbum atualizado com sucesso.',
        );
      } else {
        await this.service().create(input);

        this.operationMessage.set(
          'Álbum criado com sucesso.',
        );
      }

      this.selectedAlbum.set(null);
      this.formVisible.set(false);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  async deleteAlbum(
    album: Album,
  ): Promise<void> {
    if (
      !this.canDelete()
      || this.deletingAlbumId()
    ) {
      return;
    }

    if (
      !window.confirm(
        `Excluir o álbum "${album.name}"? A exclusão só será permitida se ele estiver vazio.`,
      )
    ) {
      return;
    }

    this.deletingAlbumId.set(album.id);
    this.clearOperationMessages();

    try {
      await this.service().delete(album.id);

      if (
        this.selectedAlbum()?.id === album.id
      ) {
        this.selectedAlbum.set(null);
        this.formVisible.set(false);
      }

      if (
        this.selectedDashboardAlbumId()
        === album.id
      ) {
        this.selectedDashboardAlbumId.set('');
      }

      this.operationMessage.set(
        'Álbum excluído com sucesso.',
      );

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.deletingAlbumId.set(null);
    }
  }

  environmentName(
    environmentId: string,
  ): string {
    return this.environments().find(
      environment => environment.id === environmentId,
    )?.name ?? environmentId;
  }

  formatDate(
    value: string,
  ): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return 'Data inválida';
    }

    return new Intl.DateTimeFormat(
      'pt-BR',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      },
    ).format(date);
  }


  private async loadMediaSummary(): Promise<void> {
    try {
      const [
        photos,
        videos,
      ] = await Promise.all([
        this.mediaService().list({
          mediaType: 'image',
          page: 1,
          pageSize: 1,
        }),
        this.mediaService().list({
          mediaType: 'video',
          page: 1,
          pageSize: 1,
        }),
      ]);

      if (!this.destroyed) {
        this.photoCount.set(photos.total);
        this.videoCount.set(videos.total);
      }
    } catch {
      if (!this.destroyed) {
        this.photoCount.set(0);
        this.videoCount.set(0);
      }
    }
  }

  private async loadSelectedAlbumMedia(
    reset: boolean,
  ): Promise<void> {
    const albumId = this.selectedDashboardAlbumId();
    const album = this.selectedDashboardAlbum();

    if (!albumId || !album) {
      this.resetAlbumMedia();

      return;
    }

    const requestSequence =
      this.mediaRequestSequence + 1;

    this.mediaRequestSequence = requestSequence;

    const page = reset
      ? 1
      : this.albumMediaPage() + 1;

    if (reset) {
      this.albumMediaLoading.set(true);
      this.albumMediaLoadingMore.set(false);
      this.albumMediaError.set(null);
      this.albumMedia.set([]);
      this.albumMediaTotal.set(0);
      this.albumMediaPage.set(0);
      this.expandedPeriodKeys.set(
        new Set<string>(),
      );
      this.clearThumbnailUrls();
    } else {
      this.albumMediaLoadingMore.set(true);
      this.albumMediaError.set(null);
    }

    try {
      const result = await this.mediaService().list({
        environmentId: album.environmentId,
        albumId,
        page,
        pageSize: ALBUM_MEDIA_PAGE_SIZE,
      });

      if (
        requestSequence !== this.mediaRequestSequence
        || albumId !== this.selectedDashboardAlbumId()
      ) {
        return;
      }

      const nextItems = reset
        ? result.items
        : [
            ...this.albumMedia(),
            ...result.items,
          ];

      this.albumMedia.set(nextItems);
      this.albumMediaTotal.set(result.total);
      this.albumMediaPage.set(result.page);
      this.synchronizeThumbnails(nextItems);

      if (reset) {
        const firstPeriod =
          this.buildMediaPeriods(nextItems)[0];

        this.expandedPeriodKeys.set(
          new Set(
            firstPeriod
              ? [firstPeriod.key]
              : [],
          ),
        );
      }
    } catch {
      if (
        requestSequence === this.mediaRequestSequence
        && albumId === this.selectedDashboardAlbumId()
      ) {
        this.albumMediaError.set(
          'Não foi possível carregar as mídias deste álbum.',
        );
      }
    } finally {
      if (requestSequence === this.mediaRequestSequence) {
        this.albumMediaLoading.set(false);
        this.albumMediaLoadingMore.set(false);
      }
    }
  }

  private resetAlbumMedia(): void {
    this.mediaRequestSequence += 1;
    this.albumMedia.set([]);
    this.albumMediaTotal.set(0);
    this.albumMediaPage.set(0);
    this.albumMediaLoading.set(false);
    this.albumMediaLoadingMore.set(false);
    this.albumMediaError.set(null);
    this.expandedPeriodKeys.set(
      new Set<string>(),
    );
    this.clearThumbnailUrls();
  }

  private buildMediaPeriods(
    items: readonly Media[],
  ): readonly AlbumMediaPeriod[] {
    const periods = new Map<
      string,
      {
        label: string;
        sortValue: number;
        items: Media[];
      }
    >();

    for (const media of items) {
      const dateMatch = media.originalDate?.match(
        /^(\d{4})-(\d{2})/,
      );

      let key = 'without-date';
      let label = 'Sem data';
      let sortValue = Number.NEGATIVE_INFINITY;

      if (dateMatch) {
        const year = Number(dateMatch[1]);
        const month = Number(dateMatch[2]);

        key = `${year}-${String(month).padStart(2, '0')}`;
        sortValue = year * 100 + month;

        const formattedLabel =
          new Intl.DateTimeFormat(
            'pt-BR',
            {
              month: 'long',
              year: 'numeric',
            },
          ).format(
            new Date(year, month - 1, 1),
          );

        label = formattedLabel.charAt(0)
          .toLocaleUpperCase('pt-BR')
          + formattedLabel.slice(1);
      }

      const period = periods.get(key);

      if (period) {
        period.items.push(media);
      } else {
        periods.set(
          key,
          {
            label,
            sortValue,
            items: [media],
          },
        );
      }
    }

    return Array.from(
      periods,
      ([key, period]) => ({
        key,
        label: period.label,
        sortValue: period.sortValue,
        items: period.items,
      }),
    ).sort(
      (left, right) => (
        right.sortValue - left.sortValue
      ),
    );
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

    for (const media of items) {
      if (
        media.processingStatus === 'ready'
        && !currentUrls.has(media.id)
        && !this.thumbnailFailures().has(media.id)
        && !this.pendingThumbnailIds.has(media.id)
      ) {
        void this.loadThumbnail(media);
      }
    }
  }

  private async loadThumbnail(
    media: Media,
  ): Promise<void> {
    this.pendingThumbnailIds.add(media.id);

    try {
      const thumbnail =
        await this.mediaService().loadThumbnail(
          media.id,
          media.mediaType,
        );

      if (
        this.destroyed
        || !this.albumMedia().some(
          item => item.id === media.id,
        )
      ) {
        return;
      }

      const objectUrl = URL.createObjectURL(thumbnail);

      this.thumbnailUrls.update(current => {
        const next = new Map(current);
        const previousUrl = next.get(media.id);

        if (previousUrl) {
          URL.revokeObjectURL(previousUrl);
        }

        next.set(media.id, objectUrl);

        return next;
      });
    } catch {
      if (!this.destroyed) {
        this.thumbnailFailures.update(current => {
          const next = new Set(current);

          next.add(media.id);

          return next;
        });
      }
    } finally {
      this.pendingThumbnailIds.delete(media.id);
    }
  }

  private clearThumbnailUrls(): void {
    for (
      const objectUrl
      of this.thumbnailUrls().values()
    ) {
      URL.revokeObjectURL(objectUrl);
    }

    this.thumbnailUrls.set(
      new Map<string, string>(),
    );
    this.thumbnailFailures.set(
      new Set<string>(),
    );
    this.pendingThumbnailIds.clear();
  }

  private clearOperationMessages(): void {
    this.operationMessage.set(null);
    this.operationError.set(null);
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error
        ? error.message
        : 'Não foi possível concluir a operação.';
    }

    if (error.status === 0) {
      return 'Não foi possível acessar a API.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'O álbum não foi encontrado.';
    }

    if (error.status === 409) {
      return 'O álbum não pode ser excluído enquanto possuir mídias associadas.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

  private scrollToForm(): void {
    setTimeout(() => {
      document
        .querySelector('deja-album-form')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
    });
  }
}
