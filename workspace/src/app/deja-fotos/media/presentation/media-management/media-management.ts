/*
 * Deja Fotos
 *
 * Media Management
 *
 * Coordena filtros, paginação, seleção e curadoria em lote.
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
  Album,
  AlbumService,
} from '../../../albums';

import {
  FotosEnvironmentOption,
} from '../../../fotos-environment-option';

import {
  MediaService,
} from '../../application';

import {
  Media,
  MediaBulkOperation,
  MediaBulkResult,
  MediaFilters,
  MediaProcessingStatus,
  MediaType,
} from '../../domain';

import {
  MediaBulkActionRequest,
  MediaBulkActionsComponent,
} from '../media-bulk-actions/media-bulk-actions';

import {
  MediaGridComponent,
} from '../media-grid/media-grid';

type MediaTypeFilter =
  | 'all'
  | MediaType;

type MediaProcessingStatusFilter =
  | 'all'
  | MediaProcessingStatus;

type MediaDateStateFilter =
  | 'all'
  | 'missing'
  | 'verified'
  | 'unverified'
  | 'conflict';

interface MediaUploadFailure {
  readonly fileName: string;
  readonly message: string;
}

interface MediaUploadResult {
  readonly requestedCount: number;
  readonly succeededCount: number;
  readonly failedCount: number;
  readonly failures: readonly MediaUploadFailure[];
}

const MAX_UPLOAD_FILES = 20;

const PROCESSING_REFRESH_INTERVAL_MS = 2_000;

const PROCESSING_REFRESH_MAX_ATTEMPTS = 150;

const PROCESSING_PENDING_STATUSES =
  new Set<MediaProcessingStatus>([
    'received',
    'validating',
    'processing',
  ]);

@Component({
  selector: 'deja-media-management',
  standalone: true,
  imports: [
    FormsModule,
    MediaBulkActionsComponent,
    MediaGridComponent,
  ],
  templateUrl: './media-management.html',
  styleUrl: './media-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MediaManagementComponent implements OnInit, OnDestroy {
  readonly mediaService = input.required<MediaService>();

  readonly albumService = input.required<AlbumService>();

  readonly environments =
    input<readonly FotosEnvironmentOption[]>([]);

  readonly defaultEnvironmentId =
    input<string | null>(null);

  readonly canUpload = input(false);

  readonly canCurate = input(false);

  readonly items = signal<readonly Media[]>([]);

  readonly albums = signal<readonly Album[]>([]);

  readonly loading = signal(false);

  readonly loadingAlbums = signal(false);

  readonly bulkBusy = signal(false);

  readonly uploadFiles =
    signal<readonly File[]>([]);

  readonly uploadEnvironmentId = signal('');

  readonly uploadAlbumId = signal('');

  readonly uploadBusy = signal(false);

  readonly uploadCompletedCount = signal(0);

  readonly uploadMessage =
    signal<string | null>(null);

  readonly uploadError =
    signal<string | null>(null);

  readonly uploadResult =
    signal<MediaUploadResult | null>(null);

  readonly errorMessage = signal<string | null>(null);

  readonly albumErrorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  readonly operationError =
    signal<string | null>(null);

  readonly bulkResult =
    signal<MediaBulkResult | null>(null);

  readonly selectedIds =
    signal<ReadonlySet<string>>(
      new Set<string>(),
    );

  readonly environmentFilter = signal('');

  readonly albumFilter = signal('');

  readonly mediaTypeFilter =
    signal<MediaTypeFilter>('all');

  readonly processingStatusFilter =
    signal<MediaProcessingStatusFilter>('all');

  readonly dateStateFilter =
    signal<MediaDateStateFilter>('all');

  readonly originalYear = signal('');

  readonly originalMonth = signal('');

  readonly originalDateFrom = signal('');

  readonly originalDateTo = signal('');

  readonly convertedFilter =
    signal<'all' | 'converted' | 'original'>('all');

  readonly page = signal(1);

  readonly pageSize = signal(24);

  readonly total = signal(0);

  readonly totalPages = signal(0);

  readonly activeAlbums = computed(
    () => this.albums().filter(album => album.active),
  );

  readonly paginationLabel = computed(() => {
    const total = this.total();

    if (total === 0) {
      return 'Nenhuma mídia';
    }

    const first = (
      (this.page() - 1) * this.pageSize()
    ) + 1;

    const last = Math.min(
      this.page() * this.pageSize(),
      total,
    );

    return `${first}–${last} de ${total}`;
  });

  private requestSequence = 0;

  private readonly pendingProcessingIds =
    new Set<string>();

  private processingRefreshAttempts = 0;

  private processingRefreshTimer:
    ReturnType<typeof setTimeout> | null = null;

  private destroyed = false;

  ngOnInit(): void {
    const defaultEnvironmentId =
      this.defaultEnvironmentId();

    if (defaultEnvironmentId) {
      this.environmentFilter.set(
        defaultEnvironmentId,
      );

      this.uploadEnvironmentId.set(
        defaultEnvironmentId,
      );
    }

    void this.loadInitialData();
  }

  ngOnDestroy(): void {
    this.destroyed = true;

    if (this.processingRefreshTimer !== null) {
      clearTimeout(this.processingRefreshTimer);
      this.processingRefreshTimer = null;
    }

    this.pendingProcessingIds.clear();
  }

  async refresh(): Promise<void> {
    const requestSequence =
      this.requestSequence + 1;

    this.requestSequence = requestSequence;

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const mediaPage = await this.mediaService().list(
        this.createFilters(),
      );

      if (requestSequence !== this.requestSequence) {
        return;
      }

      this.items.set(mediaPage.items);
      this.page.set(mediaPage.page);
      this.pageSize.set(mediaPage.pageSize);
      this.total.set(mediaPage.total);
      this.totalPages.set(mediaPage.totalPages);
    } catch {
      if (requestSequence === this.requestSequence) {
        this.errorMessage.set(
          'Não foi possível carregar as mídias.',
        );
      }
    } finally {
      if (requestSequence === this.requestSequence) {
        this.loading.set(false);
      }
    }
  }

  async loadAlbums(): Promise<void> {
    this.loadingAlbums.set(true);
    this.albumErrorMessage.set(null);

    try {
      const albums = await this.albumService().list();

      this.albums.set(albums);
    } catch {
      this.albumErrorMessage.set(
        'Não foi possível carregar os álbuns.',
      );
    } finally {
      this.loadingAlbums.set(false);
    }
  }

  selectUploadFiles(
    event: Event,
  ): void {
    const inputElement =
      event.target as HTMLInputElement;

    const files = Array.from(
      inputElement.files ?? [],
    );

    inputElement.value = '';

    this.clearUploadResult();

    if (files.length > MAX_UPLOAD_FILES) {
      this.uploadFiles.set([]);

      this.uploadError.set(
        `Selecione no máximo ${MAX_UPLOAD_FILES} arquivos por envio.`,
      );

      return;
    }

    this.uploadFiles.set(files);
  }

  removeUploadFile(
    index: number,
  ): void {
    if (this.uploadBusy()) {
      return;
    }

    this.uploadFiles.update(
      files => files.filter(
        (_, fileIndex) => fileIndex !== index,
      ),
    );

    this.clearUploadResult();
  }

  clearUploadFiles(): void {
    if (this.uploadBusy()) {
      return;
    }

    this.uploadFiles.set([]);
    this.clearUploadResult();
  }

  async uploadSelectedFiles(): Promise<void> {
    if (
      !this.canUpload()
      || this.uploadBusy()
    ) {
      return;
    }

    const environmentId =
      this.uploadEnvironmentId().trim();

    const albumId =
      this.uploadAlbumId().trim() || null;

    const files = this.uploadFiles();

    this.clearUploadResult();

    if (!environmentId) {
      this.uploadError.set(
        'Selecione o ambiente de destino.',
      );

      return;
    }

    if (files.length === 0) {
      this.uploadError.set(
        'Selecione ao menos um arquivo.',
      );

      return;
    }

    this.uploadBusy.set(true);
    this.uploadCompletedCount.set(0);

    const failures: MediaUploadFailure[] = [];
    const failedFiles: File[] = [];
    const uploadedMediaIds: string[] = [];
    let succeededCount = 0;

    try {
      for (const file of files) {
        try {
          const uploadedMedia =
            await this.mediaService().upload({
              environmentId,
              albumId,
              file,
            });

          uploadedMediaIds.push(uploadedMedia.id);
          succeededCount += 1;
        } catch (error: unknown) {
          failedFiles.push(file);

          failures.push({
            fileName: file.name,
            message: this.resolveErrorMessage(error),
          });
        } finally {
          this.uploadCompletedCount.update(
            value => value + 1,
          );
        }
      }

      const failedCount = failures.length;

      this.uploadResult.set({
        requestedCount: files.length,
        succeededCount,
        failedCount,
        failures,
      });

      this.uploadFiles.set(failedFiles);

      if (succeededCount > 0) {
        this.uploadMessage.set(
          `${succeededCount} ${
            succeededCount === 1
              ? 'arquivo enviado'
              : 'arquivos enviados'
          } com sucesso.`,
        );

        this.environmentFilter.set(environmentId);
        this.albumFilter.set(albumId ?? '');
        this.page.set(1);
        this.clearSelection();

        await Promise.all([
          this.refresh(),
          this.loadAlbums(),
        ]);

        this.startProcessingRefresh(
          uploadedMediaIds,
        );
      }

      if (failedCount > 0) {
        this.uploadError.set(
          `${failedCount} ${
            failedCount === 1
              ? 'arquivo não pôde'
              : 'arquivos não puderam'
          } ser enviado.`,
        );
      }
    } finally {
      this.uploadBusy.set(false);
    }
  }

  formatFileSize(
    size: number,
  ): string {
    if (size < 1024) {
      return `${size} B`;
    }

    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    return `${
      (size / (1024 * 1024)).toFixed(1)
    } MB`;
  }

  applyFilters(): void {
    this.page.set(1);
    this.clearSelection();
    this.clearOperationState();

    void this.refresh();
  }

  clearFilters(): void {
    this.environmentFilter.set(
      this.defaultEnvironmentId() ?? '',
    );
    this.albumFilter.set('');
    this.mediaTypeFilter.set('all');
    this.processingStatusFilter.set('all');
    this.dateStateFilter.set('all');
    this.originalYear.set('');
    this.originalMonth.set('');
    this.originalDateFrom.set('');
    this.originalDateTo.set('');
    this.convertedFilter.set('all');

    this.applyFilters();
  }

  previousPage(): void {
    if (
      this.loading()
      || this.page() <= 1
    ) {
      return;
    }

    this.page.update(value => value - 1);
    this.clearSelection();

    void this.refresh();
  }

  nextPage(): void {
    if (
      this.loading()
      || this.page() >= this.totalPages()
    ) {
      return;
    }

    this.page.update(value => value + 1);
    this.clearSelection();

    void this.refresh();
  }

  changePageSize(
    value: number | string,
  ): void {
    const parsedValue = Number(value);

    if (
      !Number.isInteger(parsedValue)
      || parsedValue < 1
      || parsedValue > 200
    ) {
      return;
    }

    this.pageSize.set(parsedValue);
    this.page.set(1);
    this.clearSelection();

    void this.refresh();
  }

  toggleMediaSelection(
    change: {
      readonly mediaId: string;
      readonly selected: boolean;
    },
  ): void {
    const next = new Set(this.selectedIds());

    if (change.selected) {
      if (
        next.size >= 100
        && !next.has(change.mediaId)
      ) {
        this.operationError.set(
          'Selecione no máximo 100 mídias por operação.',
        );

        return;
      }

      next.add(change.mediaId);
    } else {
      next.delete(change.mediaId);
    }

    this.selectedIds.set(next);
    this.clearBulkResultMessages();
  }

  togglePageSelection(
    selected: boolean,
  ): void {
    const next = new Set(this.selectedIds());

    if (selected) {
      for (const media of this.items()) {
        if (next.size >= 100) {
          this.operationError.set(
            'A seleção foi limitada a 100 mídias.',
          );

          break;
        }

        next.add(media.id);
      }
    } else {
      for (const media of this.items()) {
        next.delete(media.id);
      }
    }

    this.selectedIds.set(next);
    this.clearBulkResultMessages();
  }

  clearSelection(): void {
    this.selectedIds.set(
      new Set<string>(),
    );
  }

  async executeBulkAction(
    action: MediaBulkActionRequest,
  ): Promise<void> {
    if (
      !this.canCurate()
      || this.bulkBusy()
    ) {
      return;
    }

    const mediaIds = [
      ...this.selectedIds(),
    ];

    if (mediaIds.length === 0) {
      this.operationError.set(
        'Selecione ao menos uma mídia.',
      );

      return;
    }

    const operation = this.createBulkOperation(
      action,
      mediaIds,
    );

    this.bulkBusy.set(true);
    this.operationMessage.set(null);
    this.operationError.set(null);
    this.bulkResult.set(null);

    try {
      const result = await this.mediaService().bulkUpdate(
        operation,
      );

      this.bulkResult.set(result);

      if (result.failedCount === 0) {
        this.operationMessage.set(
          `${result.succeededCount} ${
            result.succeededCount === 1
              ? 'mídia atualizada'
              : 'mídias atualizadas'
          } com sucesso.`,
        );

        this.clearSelection();
      } else {
        this.operationError.set(
          `${result.failedCount} ${
            result.failedCount === 1
              ? 'mídia não pôde'
              : 'mídias não puderam'
          } ser atualizada.`,
        );

        this.selectedIds.set(
          new Set(
            result.results
              .filter(item => !item.success)
              .map(item => item.mediaId),
          ),
        );
      }

      await Promise.all([
        this.refresh(),
        action.operation === 'set_album'
          ? this.loadAlbums()
          : Promise.resolve(),
      ]);
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.bulkBusy.set(false);
    }
  }

  private startProcessingRefresh(
    mediaIds: readonly string[],
  ): void {
    for (const mediaId of mediaIds) {
      this.pendingProcessingIds.add(mediaId);
    }

    this.processingRefreshAttempts = 0;

    if (this.processingRefreshTimer !== null) {
      clearTimeout(this.processingRefreshTimer);
      this.processingRefreshTimer = null;
    }

    this.scheduleProcessingRefresh();
  }

  private scheduleProcessingRefresh(): void {
    if (
      this.destroyed
      || this.processingRefreshTimer !== null
      || this.pendingProcessingIds.size === 0
      || (
        this.processingRefreshAttempts
        >= PROCESSING_REFRESH_MAX_ATTEMPTS
      )
    ) {
      return;
    }

    this.processingRefreshTimer = setTimeout(
      () => {
        this.processingRefreshTimer = null;

        void this.refreshProcessingMedia();
      },
      PROCESSING_REFRESH_INTERVAL_MS,
    );
  }

  private async refreshProcessingMedia(): Promise<void> {
    if (
      this.destroyed
      || this.pendingProcessingIds.size === 0
    ) {
      return;
    }

    this.processingRefreshAttempts += 1;

    const mediaIds = [
      ...this.pendingProcessingIds,
    ];

    const refreshedMedia = await Promise.all(
      mediaIds.map(async mediaId => {
        try {
          return await this.mediaService().findById(
            mediaId,
          );
        } catch {
          return undefined;
        }
      }),
    );

    if (this.destroyed) {
      return;
    }

    const refreshedById = new Map<string, Media>();

    for (const media of refreshedMedia) {
      if (!media) {
        continue;
      }

      refreshedById.set(media.id, media);

      if (
        !PROCESSING_PENDING_STATUSES.has(
          media.processingStatus,
        )
      ) {
        this.pendingProcessingIds.delete(media.id);
      }
    }

    if (refreshedById.size > 0) {
      this.items.update(items => items.map(
        media => refreshedById.get(media.id) ?? media,
      ));
    }

    this.scheduleProcessingRefresh();
  }

  private async loadInitialData(): Promise<void> {
    await Promise.all([
      this.refresh(),
      this.loadAlbums(),
    ]);
  }

  private createFilters(): MediaFilters {
    const dateState = this.dateStateFilter();
    const mediaType = this.mediaTypeFilter();
    const processingStatus = this.processingStatusFilter();
    const year = Number(this.originalYear());
    const month = Number(this.originalMonth());

    return {
      environmentId:
        this.environmentFilter() || undefined,
      albumId:
        this.albumFilter() || undefined,
      mediaType:
        mediaType === 'all'
          ? undefined
          : mediaType,
      processingStatus:
        processingStatus === 'all'
          ? undefined
          : processingStatus,
      originalDateFrom: this.toDateBoundary(
        this.originalDateFrom(),
        false,
      ),
      originalDateTo: this.toDateBoundary(
        this.originalDateTo(),
        true,
      ),
      originalYear:
        Number.isInteger(year)
        && year >= 1
        && year <= 9999
          ? year
          : undefined,
      originalMonth:
        Number.isInteger(month)
        && month >= 1
        && month <= 12
          ? month
          : undefined,
      withoutOriginalDate:
        dateState === 'missing'
          ? true
          : undefined,
      originalDateVerified:
        dateState === 'verified'
          ? true
          : dateState === 'unverified'
            ? false
            : undefined,
      originalDateConflict:
        dateState === 'conflict'
          ? true
          : undefined,
      wasConverted:
        this.convertedFilter() === 'converted'
          ? true
          : this.convertedFilter() === 'original'
            ? false
            : undefined,
      page: this.page(),
      pageSize: this.pageSize(),
    };
  }

  private createBulkOperation(
    action: MediaBulkActionRequest,
    mediaIds: readonly string[],
  ): MediaBulkOperation {
    switch (action.operation) {
      case 'set_original_date':
        return {
          operation: action.operation,
          mediaIds,
          originalDate: action.originalDate,
        };

      case 'verify_original_date':
      case 'clear_original_date_conflict':
        return {
          operation: action.operation,
          mediaIds,
        };

      case 'set_album':
        return {
          operation: action.operation,
          mediaIds,
          albumId: action.albumId,
        };
    }
  }

  private toDateBoundary(
    value: string,
    endOfDay: boolean,
  ): string | undefined {
    if (!value) {
      return undefined;
    }

    const boundary =
      `${value}T${
        endOfDay
          ? '23:59:59.999'
          : '00:00:00.000'
      }`;

    const date = new Date(boundary);

    return Number.isNaN(date.getTime())
      ? undefined
      : boundary;
  }

  private clearUploadResult(): void {
    this.uploadCompletedCount.set(0);
    this.uploadMessage.set(null);
    this.uploadError.set(null);
    this.uploadResult.set(null);
  }

  private clearOperationState(): void {
    this.operationMessage.set(null);
    this.operationError.set(null);
    this.bulkResult.set(null);
  }

  private clearBulkResultMessages(): void {
    this.operationMessage.set(null);
    this.operationError.set(null);
    this.bulkResult.set(null);
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

    const detail = error.error?.detail;

    if (
      typeof detail === 'string'
      && detail.trim()
    ) {
      return detail;
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 409) {
      return 'A operação encontrou um conflito no acervo.';
    }

    if (error.status === 422) {
      return 'Revise a seleção e os dados informados.';
    }

    return 'Não foi possível concluir a operação.';
  }
}