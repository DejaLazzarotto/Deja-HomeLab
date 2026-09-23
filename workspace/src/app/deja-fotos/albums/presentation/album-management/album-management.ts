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
  MediaBulkActionRequest,
  MediaBulkActionsComponent,
  MediaBulkResult,
  MediaService,
  formatMediaDate,
  formatMediaDuration,
} from '../../../media';

import {
  Person,
  PersonPanelComponent,
  PersonService,
} from '../../../people';

import {
  AlbumService,
} from '../../application';

import {
  Album,
  AlbumInput,
  AlbumPeriod,
} from '../../domain';

import {
  AlbumFormComponent,
} from '../album-form/album-form';

interface AlbumMediaPeriod {
  readonly key: string;
  readonly label: string;
  readonly year: number | null;
  readonly month: number | null;
  readonly mediaCount: number;
  readonly description: string | null;
  readonly descriptionDraft: string;
  readonly editingDescription: boolean;
  readonly savingDescription: boolean;
  readonly descriptionMessage: string | null;
  readonly descriptionError: string | null;
  readonly items: readonly Media[];
  readonly page: number;
  readonly total: number;
  readonly loaded: boolean;
  readonly loading: boolean;
  readonly loadingMore: boolean;
  readonly error: string | null;
}

const ALBUM_MEDIA_PAGE_SIZE = 100;

@Component({
  selector: 'deja-album-management',
  standalone: true,
  imports: [
    FormsModule,
    AlbumFormComponent,
    MediaBulkActionsComponent,
    PersonPanelComponent,
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

  readonly personService =
    input.required<PersonService>();

  readonly environments =
    input<readonly FotosEnvironmentOption[]>([]);

  readonly defaultEnvironmentId =
    input<string | null>(null);

  readonly canEdit = input(false);

  readonly canOrganize = input(false);

  readonly canDelete = input(false);

  readonly albums = signal<readonly Album[]>([]);

  readonly people = signal<readonly Person[]>([]);

  readonly peopleTotal = signal(0);

  readonly peoplePage = signal(0);

  readonly peopleLoading = signal(false);

  readonly peopleError = signal<string | null>(null);

  readonly selectedPerson = signal<Person | null>(null);

  readonly creatingPerson = signal(false);

  readonly photoCount = signal(0);

  readonly videoCount = signal(0);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly bulkBusy = signal(false);

  readonly bulkResult =
    signal<MediaBulkResult | null>(null);

  readonly selectedMediaIds =
    signal<ReadonlySet<string>>(
      new Set<string>(),
    );

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

  readonly albumMediaPeriods =
    signal<readonly AlbumMediaPeriod[]>([]);

  readonly albumMediaLoading = signal(false);

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

  readonly destinationAlbums = computed(() => {
    const selectedAlbum =
      this.selectedDashboardAlbum();

    if (!selectedAlbum) {
      return [];
    }

    return this.activeAlbums().filter(album => (
      album.id !== selectedAlbum.id
      && album.organizationId
        === selectedAlbum.organizationId
      && album.tenantId
        === selectedAlbum.tenantId
      && album.environmentId
        === selectedAlbum.environmentId
    ));
  });

  readonly selectedDashboardAlbum = computed(() => {
    const albumId = this.selectedDashboardAlbumId();

    if (!albumId) {
      return null;
    }

    return this.albums().find(
      album => album.id === albumId,
    ) ?? null;
  });

  readonly albumMedia = computed(() => (
    this.albumMediaPeriods().flatMap(
      period => period.items,
    )
  ));

  readonly albumMediaTotal = computed(() => (
    this.albumMediaPeriods().reduce(
      (total, period) => total + period.mediaCount,
      0,
    )
  ));

  readonly albumMediaLoadingMore = computed(() => (
    this.albumMediaPeriods().some(
      period => period.loadingMore,
    )
  ));

  readonly albumMediaHasMore = computed(() => (
    this.albumMediaPeriods().some(
      period => (
        period.loaded
        && period.items.length < period.total
      ),
    )
  ));

  private readonly pendingThumbnailIds =
    new Set<string>();

  private readonly periodRequestSequences =
    new Map<string, number>();

  private requestSequence = 0;

  private periodsRequestSequence = 0;

  private destroyed = false;

  ngOnInit(): void {
    void this.refresh();
    void this.loadMediaSummary();
    void this.loadPeople(true);
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.periodsRequestSequence += 1;
    this.periodRequestSequences.clear();
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
          this.resetAlbumMedia();
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

  async loadPeople(reset = false): Promise<void> {
    if (
      this.peopleLoading()
      || (
        !reset
        && this.peoplePage() > 0
        && this.people().length >= this.peopleTotal()
      )
    ) {
      return;
    }

    this.peopleLoading.set(true);
    this.peopleError.set(null);

    try {
      const page = reset
        ? 1
        : this.peoplePage() + 1;

      const result = await this.personService().list({
        page,
        pageSize: 50,
      });

      if (this.destroyed) {
        return;
      }

      this.people.update(current => (
        reset
          ? result.items
          : [
              ...current,
              ...result.items.filter(
                person => !current.some(
                  item => item.id === person.id,
                ),
              ),
            ]
      ));
      this.peoplePage.set(result.page);
      this.peopleTotal.set(result.total);
    } catch {
      this.peopleError.set(
        'Não foi possível carregar pessoas.',
      );
    } finally {
      this.peopleLoading.set(false);
    }
  }

  selectDashboardPerson(personId: string): void {
    this.creatingPerson.set(false);
    this.selectedPerson.set(
      this.people().find(
        person => person.id === personId,
      ) ?? null,
    );

    if (personId) {
      this.selectedDashboardAlbumId.set('');
      this.clearSelection();
      this.resetAlbumMedia();
    }
  }

  openPersonCreate(): void {
    if (!this.canEdit()) {
      return;
    }

    this.formVisible.set(false);
    this.selectedDashboardAlbumId.set('');
    this.selectedPerson.set(null);
    this.clearSelection();
    this.resetAlbumMedia();
    this.creatingPerson.set(true);
  }

  closePersonCreate(): void {
    this.creatingPerson.set(false);
  }

  onPersonSaved(person: Person): void {
    const wasCreating = this.creatingPerson();
    this.creatingPerson.set(false);
    this.selectedPerson.set(person);
    this.people.update(current => {
      const withoutPerson = current.filter(
        item => item.id !== person.id,
      );

      return [...withoutPerson, person].sort(
        (left, right) => left.name.localeCompare(
          right.name,
          'pt-BR',
        ),
      );
    });

    if (wasCreating) {
      this.peopleTotal.update(total => total + 1);
    }
  }

  onPersonDeleted(personId: string): void {
    this.selectedPerson.set(null);
    this.people.update(current => current.filter(
      person => person.id !== personId,
    ));
    this.peopleTotal.update(total => Math.max(
      0,
      total - 1,
    ));
  }

  selectDashboardAlbum(
    albumId: string,
  ): void {
    if (this.bulkBusy()) {
      return;
    }

    this.selectedPerson.set(null);
    this.creatingPerson.set(false);
    this.selectedDashboardAlbumId.set(albumId);
    this.clearSelection();
    this.clearOperationMessages();
    this.resetAlbumMedia();

    if (albumId) {
      void this.loadSelectedAlbumPeriods();
    }
  }

  retryAlbumMedia(): void {
    void this.loadSelectedAlbumPeriods();
  }

  togglePeriod(
    periodKey: string,
  ): void {
    const expanded =
      this.expandedPeriodKeys().has(periodKey);

    this.expandedPeriodKeys.update(current => {
      const next = new Set(current);

      if (expanded) {
        next.delete(periodKey);
      } else {
        next.add(periodKey);
      }

      return next;
    });

    if (!expanded) {
      const period = this.findPeriod(periodKey);

      if (
        period
        && !period.loaded
        && !period.loading
      ) {
        void this.loadPeriodMedia(
          periodKey,
          true,
        );
      }
    }
  }

  periodExpanded(
    periodKey: string,
  ): boolean {
    return this.expandedPeriodKeys().has(periodKey);
  }

  periodHasMore(
    period: AlbumMediaPeriod,
  ): boolean {
    return (
      period.loaded
      && period.items.length < period.total
    );
  }

  retryPeriod(
    periodKey: string,
  ): void {
    void this.loadPeriodMedia(
      periodKey,
      true,
    );
  }

  loadMorePeriod(
    periodKey: string,
  ): void {
    void this.loadPeriodMedia(
      periodKey,
      false,
    );
  }

  async loadMoreAlbumMedia(): Promise<void> {
    const period = this.albumMediaPeriods().find(
      candidate => (
        this.periodExpanded(candidate.key)
        && this.periodHasMore(candidate)
      ),
    );

    if (period) {
      await this.loadPeriodMedia(
        period.key,
        false,
      );
    }
  }

  mediaSelected(
    mediaId: string,
  ): boolean {
    return this.selectedMediaIds().has(mediaId);
  }

  allLoadedPeriodMediaSelected(
    period: AlbumMediaPeriod,
  ): boolean {
    return (
      period.items.length > 0
      && period.items.every(
        media => this.mediaSelected(media.id),
      )
    );
  }

  toggleMediaSelection(
    mediaId: string,
    selected: boolean,
  ): void {
    if (
      !this.canOrganize()
      || this.bulkBusy()
    ) {
      return;
    }

    const next =
      new Set(this.selectedMediaIds());

    if (selected) {
      if (
        next.size >= 100
        && !next.has(mediaId)
      ) {
        this.operationError.set(
          'Selecione no máximo 100 mídias por operação.',
        );

        return;
      }

      next.add(mediaId);
    } else {
      next.delete(mediaId);
    }

    this.selectedMediaIds.set(next);
    this.bulkResult.set(null);
    this.operationMessage.set(null);
    this.operationError.set(null);
  }

  toggleLoadedPeriodSelection(
    periodKey: string,
    selected: boolean,
  ): void {
    if (
      !this.canOrganize()
      || this.bulkBusy()
    ) {
      return;
    }

    const period = this.findPeriod(periodKey);

    if (!period) {
      return;
    }

    const next =
      new Set(this.selectedMediaIds());

    if (selected) {
      for (const media of period.items) {
        if (next.size >= 100) {
          this.operationError.set(
            'A seleção foi limitada a 100 mídias.',
          );

          break;
        }

        next.add(media.id);
      }
    } else {
      for (const media of period.items) {
        next.delete(media.id);
      }
    }

    this.selectedMediaIds.set(next);
    this.bulkResult.set(null);
    this.operationMessage.set(null);
  }

  clearSelection(): void {
    this.selectedMediaIds.set(
      new Set<string>(),
    );
    this.bulkResult.set(null);
  }

  async executeAlbumBulkAction(
    action: MediaBulkActionRequest,
  ): Promise<void> {
    if (
      action.operation !== 'set_album'
      || !this.canOrganize()
      || this.bulkBusy()
    ) {
      return;
    }

    const mediaIds = [
      ...this.selectedMediaIds(),
    ];

    if (mediaIds.length === 0) {
      this.operationError.set(
        'Selecione ao menos uma mídia.',
      );

      return;
    }

    if (
      action.albumId === null
      && !window.confirm(
        `Retirar ${
          mediaIds.length
        } ${
          mediaIds.length === 1
            ? 'mídia'
            : 'mídias'
        } deste álbum?`,
      )
    ) {
      return;
    }

    this.bulkBusy.set(true);
    this.operationMessage.set(null);
    this.operationError.set(null);
    this.bulkResult.set(null);

    try {
      const result =
        await this.mediaService().bulkUpdate({
          operation: 'set_album',
          mediaIds,
          albumId: action.albumId,
        });

      this.bulkResult.set(result);

      if (result.failedCount === 0) {
        this.operationMessage.set(
          action.albumId === null
            ? `${
                result.succeededCount
              } ${
                result.succeededCount === 1
                  ? 'mídia retirada'
                  : 'mídias retiradas'
              } do álbum.`
            : `${
                result.succeededCount
              } ${
                result.succeededCount === 1
                  ? 'mídia movida'
                  : 'mídias movidas'
              } com sucesso.`,
        );

        this.selectedMediaIds.set(
          new Set<string>(),
        );
      } else {
        this.operationError.set(
          `${result.failedCount} ${
            result.failedCount === 1
              ? 'mídia não pôde'
              : 'mídias não puderam'
          } ser organizada.`,
        );

        this.selectedMediaIds.set(
          new Set(
            result.results
              .filter(item => !item.success)
              .map(item => item.mediaId),
          ),
        );
      }

      await this.reloadAlbumTimelinePreservingExpansion();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.bulkBusy.set(false);
    }
  }

  beginPeriodDescriptionEdit(
    periodKey: string,
  ): void {
    if (!this.canEdit()) {
      return;
    }

    this.updatePeriod(
      periodKey,
      period => ({
        ...period,
        descriptionDraft:
          period.description ?? '',
        editingDescription: true,
        descriptionMessage: null,
        descriptionError: null,
      }),
    );
  }

  cancelPeriodDescriptionEdit(
    periodKey: string,
  ): void {
    this.updatePeriod(
      periodKey,
      period => ({
        ...period,
        descriptionDraft:
          period.description ?? '',
        editingDescription: false,
        descriptionMessage: null,
        descriptionError: null,
      }),
    );
  }

  updatePeriodDescriptionDraft(
    periodKey: string,
    descriptionDraft: string,
  ): void {
    this.updatePeriod(
      periodKey,
      period => ({
        ...period,
        descriptionDraft,
        descriptionMessage: null,
        descriptionError: null,
      }),
    );
  }

  async savePeriodDescription(
    periodKey: string,
  ): Promise<void> {
    const album = this.selectedDashboardAlbum();
    const period = this.findPeriod(periodKey);

    if (
      !this.canEdit()
      || !album
      || !period
      || period.year === null
      || period.month === null
      || period.savingDescription
    ) {
      return;
    }

    this.updatePeriod(
      periodKey,
      current => ({
        ...current,
        savingDescription: true,
        descriptionMessage: null,
        descriptionError: null,
      }),
    );

    try {
      const updated =
        await this.service().updatePeriodDescription(
          album.id,
          period.year,
          period.month,
          period.descriptionDraft,
        );

      if (
        album.id
        !== this.selectedDashboardAlbumId()
      ) {
        return;
      }

      this.updatePeriod(
        periodKey,
        current => ({
          ...current,
          description: updated.description,
          descriptionDraft:
            updated.description ?? '',
          editingDescription: false,
          savingDescription: false,
          descriptionMessage: null,
          descriptionError: null,
        }),
      );
    } catch (error: unknown) {
      if (
        album.id
        === this.selectedDashboardAlbumId()
      ) {
        this.updatePeriod(
          periodKey,
          current => ({
            ...current,
            savingDescription: false,
            descriptionMessage: null,
            descriptionError:
              this.resolvePeriodDescriptionError(
                error,
              ),
          }),
        );
      }
    }
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

    this.selectedPerson.set(null);
    this.creatingPerson.set(false);
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
        this.resetAlbumMedia();
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

  private async reloadAlbumTimelinePreservingExpansion():
    Promise<void> {
    const expandedKeys = [
      ...this.expandedPeriodKeys(),
    ];

    await this.loadSelectedAlbumPeriods();

    const availableKeys = new Set(
      this.albumMediaPeriods().map(
        period => period.key,
      ),
    );

    const restoredKeys = expandedKeys.filter(
      periodKey => availableKeys.has(periodKey),
    );

    this.expandedPeriodKeys.set(
      new Set(restoredKeys),
    );

    await Promise.all(
      restoredKeys.map(
        periodKey => this.loadPeriodMedia(
          periodKey,
          true,
        ),
      ),
    );
  }

  private async loadSelectedAlbumPeriods(): Promise<void> {
    const albumId = this.selectedDashboardAlbumId();

    if (!albumId || !this.selectedDashboardAlbum()) {
      this.resetAlbumMedia();

      return;
    }

    const requestSequence =
      this.periodsRequestSequence + 1;

    this.periodsRequestSequence = requestSequence;

    this.albumMediaLoading.set(true);
    this.albumMediaError.set(null);
    this.albumMediaPeriods.set([]);
    this.expandedPeriodKeys.set(
      new Set<string>(),
    );
    this.periodRequestSequences.clear();
    this.clearThumbnailUrls();

    try {
      const periods =
        await this.service().listPeriods(albumId);

      if (
        requestSequence
        !== this.periodsRequestSequence
        || albumId
        !== this.selectedDashboardAlbumId()
      ) {
        return;
      }

      this.albumMediaPeriods.set(
        periods.map(
          period => this.createMediaPeriod(period),
        ),
      );
    } catch {
      if (
        requestSequence
        === this.periodsRequestSequence
        && albumId
        === this.selectedDashboardAlbumId()
      ) {
        this.albumMediaError.set(
          'Não foi possível carregar os períodos deste álbum.',
        );
      }
    } finally {
      if (
        requestSequence
        === this.periodsRequestSequence
      ) {
        this.albumMediaLoading.set(false);
      }
    }
  }

  private async loadPeriodMedia(
    periodKey: string,
    reset: boolean,
  ): Promise<void> {
    const album = this.selectedDashboardAlbum();
    const period = this.findPeriod(periodKey);

    if (
      !album
      || !period
      || period.loading
      || period.loadingMore
      || (
        !reset
        && !this.periodHasMore(period)
      )
    ) {
      return;
    }

    const requestSequence =
      (
        this.periodRequestSequences.get(periodKey)
        ?? 0
      ) + 1;

    this.periodRequestSequences.set(
      periodKey,
      requestSequence,
    );

    const page = reset
      ? 1
      : period.page + 1;

    this.updatePeriod(
      periodKey,
      current => ({
        ...current,
        items: reset
          ? []
          : current.items,
        page: reset
          ? 0
          : current.page,
        loaded: reset
          ? false
          : current.loaded,
        loading: reset,
        loadingMore: !reset,
        error: null,
      }),
    );

    try {
      const result = await this.mediaService().list({
        environmentId: album.environmentId,
        albumId: album.id,
        originalYear:
          period.year ?? undefined,
        originalMonth:
          period.month ?? undefined,
        withoutOriginalDate:
          period.year === null,
        page,
        pageSize: ALBUM_MEDIA_PAGE_SIZE,
      });

      if (
        this.periodRequestSequences.get(periodKey)
        !== requestSequence
        || album.id
        !== this.selectedDashboardAlbumId()
      ) {
        return;
      }

      this.updatePeriod(
        periodKey,
        current => ({
          ...current,
          items: reset
            ? result.items
            : [
                ...current.items,
                ...result.items,
              ],
          page: result.page,
          total: result.total,
          loaded: true,
          loading: false,
          loadingMore: false,
          error: null,
        }),
      );

      this.synchronizeThumbnails(
        this.albumMedia(),
      );
    } catch {
      if (
        this.periodRequestSequences.get(periodKey)
        === requestSequence
        && album.id
        === this.selectedDashboardAlbumId()
      ) {
        this.updatePeriod(
          periodKey,
          current => ({
            ...current,
            loaded: false,
            loading: false,
            loadingMore: false,
            error:
              'Não foi possível carregar as mídias deste período.',
          }),
        );
      }
    }
  }

  private createMediaPeriod(
    period: AlbumPeriod,
  ): AlbumMediaPeriod {
    return {
      key: this.periodKey(period),
      label: this.periodLabel(period),
      year: period.year,
      month: period.month,
      mediaCount: period.mediaCount,
      description: period.description,
      descriptionDraft:
        period.description ?? '',
      editingDescription: false,
      savingDescription: false,
      descriptionMessage: null,
      descriptionError: null,
      items: [],
      page: 0,
      total: period.mediaCount,
      loaded: false,
      loading: false,
      loadingMore: false,
      error: null,
    };
  }

  private periodKey(
    period: AlbumPeriod,
  ): string {
    if (
      period.year === null
      || period.month === null
    ) {
      return 'without-date';
    }

    return (
      `${period.year}-`
      + String(period.month).padStart(2, '0')
    );
  }

  private periodLabel(
    period: AlbumPeriod,
  ): string {
    if (
      period.year === null
      || period.month === null
    ) {
      return 'Sem data';
    }

    const formattedLabel =
      new Intl.DateTimeFormat(
        'pt-BR',
        {
          month: 'long',
          year: 'numeric',
        },
      ).format(
        new Date(
          period.year,
          period.month - 1,
          1,
        ),
      );

    return (
      formattedLabel.charAt(0)
        .toLocaleUpperCase('pt-BR')
      + formattedLabel.slice(1)
    );
  }

  private findPeriod(
    periodKey: string,
  ): AlbumMediaPeriod | undefined {
    return this.albumMediaPeriods().find(
      period => period.key === periodKey,
    );
  }

  private updatePeriod(
    periodKey: string,
    update: (
      period: AlbumMediaPeriod,
    ) => AlbumMediaPeriod,
  ): void {
    this.albumMediaPeriods.update(
      periods => periods.map(
        period => (
          period.key === periodKey
            ? update(period)
            : period
        ),
      ),
    );
  }

  private resetAlbumMedia(): void {
    this.periodsRequestSequence += 1;
    this.periodRequestSequences.clear();
    this.albumMediaPeriods.set([]);
    this.albumMediaLoading.set(false);
    this.albumMediaError.set(null);
    this.expandedPeriodKeys.set(
      new Set<string>(),
    );
    this.clearThumbnailUrls();
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

  private resolvePeriodDescriptionError(
    error: unknown,
  ): string {
    if (
      error instanceof HttpErrorResponse
      && error.status === 404
    ) {
      return (
        'Este período não existe mais. '
        + 'Atualize a linha do tempo.'
      );
    }

    return 'Não foi possível salvar a descrição mensal.';
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
