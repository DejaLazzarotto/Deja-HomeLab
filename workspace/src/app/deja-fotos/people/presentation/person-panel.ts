import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  effect,
  input,
  untracked,
  output,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  FotosEnvironmentOption,
} from '../../fotos-environment-option';

import {
  Media,
  MediaService,
  formatMediaDate,
} from '../../media';

import {
  Person,
  PersonInput,
} from '../domain/person';

import {
  PersonService,
} from '../application/person-service';

const PAGE_SIZE = 24;

@Component({
  selector: 'deja-person-panel',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './person-panel.html',
  styleUrl: './person-panel.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonPanelComponent implements OnDestroy {
  readonly service = input.required<PersonService>();
  readonly mediaService = input.required<MediaService>();
  readonly person = input<Person | null>(null);
  readonly creating = input(false);
  readonly environments =
    input<readonly FotosEnvironmentOption[]>([]);
  readonly defaultEnvironmentId =
    input<string | null>(null);
  readonly canEdit = input(false);
  readonly canOrganize = input(false);
  readonly canDelete = input(false);

  readonly saved = output<Person>();
  readonly deleted = output<string>();
  readonly cancelled = output<void>();

  readonly editing = signal(false);
  readonly saving = signal(false);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);
  readonly message = signal<string | null>(null);

  readonly environmentId = signal('');
  readonly name = signal('');
  readonly description = signal('');
  readonly active = signal(true);

  readonly avatarUrl = signal<string | null>(null);
  readonly items = signal<readonly Media[]>([]);
  readonly total = signal(0);
  readonly page = signal(0);
  readonly loading = signal(false);

  readonly pickerOpen = signal(false);
  readonly pickerItems = signal<readonly Media[]>([]);
  readonly pickerTotal = signal(0);
  readonly pickerPage = signal(0);
  readonly pickerLoading = signal(false);

  readonly thumbnails =
    signal<ReadonlyMap<string, string>>(
      new Map<string, string>(),
    );

  readonly thumbnailFailures =
    signal<ReadonlySet<string>>(
      new Set<string>(),
    );

  protected readonly formatMediaDate =
    formatMediaDate;

  private readonly pendingThumbnails =
    new Set<string>();

  private sequence = 0;
  private destroyed = false;

  constructor() {
    effect(() => {
      const person = this.person();
      const creating = this.creating();

      untracked(() => this.resetView());

      if (person) {
        this.environmentId.set(
          person.environmentId,
        );
        this.name.set(person.name);
        this.description.set(
          person.description ?? '',
        );
        this.active.set(person.active);
        void untracked(() => this.loadMore());
        void untracked(() => this.loadAvatar(person));
      } else if (creating) {
        this.environmentId.set(
          this.defaultEnvironmentId()
          || this.environments()[0]?.id
          || '',
        );
        this.name.set('');
        this.description.set('');
        this.active.set(true);
        this.editing.set(true);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.sequence += 1;
    this.clearObjectUrls();
  }

  startEdit(): void {
    if (this.canEdit()) {
      this.editing.set(true);
      this.error.set(null);
    }
  }

  cancelEdit(): void {
    if (this.creating()) {
      this.cancelled.emit();
      return;
    }

    const person = this.person();
    if (person) {
      this.name.set(person.name);
      this.description.set(
        person.description ?? '',
      );
      this.active.set(person.active);
    }

    this.editing.set(false);
    this.error.set(null);
  }

  async save(): Promise<void> {
    if (!this.canEdit() || this.saving()) {
      return;
    }

    const input: PersonInput = {
      environmentId: this.environmentId(),
      name: this.name(),
      description: this.description(),
      active: this.active(),
    };

    this.saving.set(true);
    this.error.set(null);

    try {
      const person = this.person();
      const saved = person
        ? await this.service().update(
            person.id,
            input,
          )
        : await this.service().create(input);

      this.editing.set(false);
      this.saved.emit(saved);
      this.message.set(
        person
          ? 'Pessoa atualizada com sucesso.'
          : 'Pessoa cadastrada com sucesso.',
      );
    } catch (error: unknown) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.saving.set(false);
    }
  }

  async uploadAvatar(file: File | null): Promise<void> {
    const person = this.person();
    if (
      !person
      || !file
      || !this.canEdit()
      || this.busy()
    ) {
      return;
    }

    this.busy.set(true);
    this.error.set(null);

    try {
      const updated =
        await this.service().uploadAvatar(
          person.id,
          file,
        );
      this.saved.emit(updated);
      await this.loadAvatar(updated);
      this.message.set('Avatar atualizado.');
    } catch (error: unknown) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.busy.set(false);
    }
  }

  async removeAvatar(): Promise<void> {
    const person = this.person();
    if (
      !person
      || !this.canEdit()
      || this.busy()
    ) {
      return;
    }

    this.busy.set(true);
    this.error.set(null);

    try {
      const updated =
        await this.service().removeAvatar(
          person.id,
        );
      this.replaceAvatarUrl(null);
      this.saved.emit(updated);
      this.message.set('Avatar removido.');
    } catch (error: unknown) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.busy.set(false);
    }
  }

  async deletePerson(): Promise<void> {
    const person = this.person();
    if (
      !person
      || !this.canDelete()
      || this.busy()
      || !window.confirm(
        `Excluir ${person.name} e seus vínculos com mídias?`,
      )
    ) {
      return;
    }

    this.busy.set(true);
    this.error.set(null);

    try {
      await this.service().delete(person.id);
      this.deleted.emit(person.id);
    } catch (error: unknown) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.busy.set(false);
    }
  }

  async loadMore(): Promise<void> {
    const person = this.person();
    if (
      !person
      || this.loading()
      || (
        this.page() > 0
        && this.items().length >= this.total()
      )
    ) {
      return;
    }

    const sequence = this.sequence;
    const nextPage = this.page() + 1;
    this.loading.set(true);
    this.error.set(null);

    try {
      const result =
        await this.mediaService().listByPerson(
          person.id,
          nextPage,
          PAGE_SIZE,
        );

      if (
        this.destroyed
        || sequence !== this.sequence
      ) {
        return;
      }

      this.items.update(current => [
        ...current,
        ...result.items,
      ]);
      this.page.set(result.page);
      this.total.set(result.total);
      this.loadThumbnails(result.items);
    } catch (error: unknown) {
      if (sequence === this.sequence) {
        this.error.set(this.errorMessage(error));
      }
    } finally {
      if (sequence === this.sequence) {
        this.loading.set(false);
      }
    }
  }

  openPicker(): void {
    if (!this.canOrganize() || !this.person()) {
      return;
    }

    this.pickerOpen.set(true);
    if (this.pickerPage() === 0) {
      void this.loadMorePicker();
    }
  }

  closePicker(): void {
    this.pickerOpen.set(false);
  }

  async loadMorePicker(): Promise<void> {
    const person = this.person();
    if (
      !person
      || this.pickerLoading()
      || (
        this.pickerPage() > 0
        && this.pickerItems().length
          >= this.pickerTotal()
      )
    ) {
      return;
    }

    const sequence = this.sequence;
    const nextPage = this.pickerPage() + 1;
    this.pickerLoading.set(true);

    try {
      const result = await this.mediaService().list({
        organizationId: person.organizationId,
        tenantId: person.tenantId,
        environmentId: person.environmentId,
        page: nextPage,
        pageSize: PAGE_SIZE,
      });

      if (
        this.destroyed
        || sequence !== this.sequence
      ) {
        return;
      }

      this.pickerItems.update(current => [
        ...current,
        ...result.items,
      ]);
      this.pickerPage.set(result.page);
      this.pickerTotal.set(result.total);
      this.loadThumbnails(result.items);
    } catch (error: unknown) {
      if (sequence === this.sequence) {
        this.error.set(this.errorMessage(error));
      }
    } finally {
      if (sequence === this.sequence) {
        this.pickerLoading.set(false);
      }
    }
  }

  isLinked(mediaId: string): boolean {
    return this.items().some(
      item => item.id === mediaId,
    );
  }

  async link(mediaId: string): Promise<void> {
    const person = this.person();
    if (
      !person
      || !this.canOrganize()
      || this.busy()
    ) {
      return;
    }

    this.busy.set(true);
    this.error.set(null);

    try {
      await this.service().linkMedia(
        person.id,
        mediaId,
      );
      this.resetGallery();
      await this.loadMore();
      this.message.set(
        'Mídia vinculada à pessoa.',
      );
    } catch (error: unknown) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.busy.set(false);
    }
  }

  async unlink(mediaId: string): Promise<void> {
    const person = this.person();
    if (
      !person
      || !this.canOrganize()
      || this.busy()
      || !window.confirm(
        'Retirar esta mídia da pessoa?',
      )
    ) {
      return;
    }

    this.busy.set(true);
    this.error.set(null);

    try {
      await this.service().unlinkMedia(
        person.id,
        mediaId,
      );
      this.resetGallery();
      await this.loadMore();
      this.message.set(
        'Vínculo com a mídia removido.',
      );
    } catch (error: unknown) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.busy.set(false);
    }
  }

  thumbnailUrl(
    mediaId: string,
  ): string | undefined {
    return this.thumbnails().get(mediaId);
  }

  private async loadAvatar(
    person: Person,
  ): Promise<void> {
    const sequence = this.sequence;

    if (!person.avatarContentType) {
      this.replaceAvatarUrl(null);
      return;
    }

    try {
      const blob = await this.service().loadAvatar(
        person.id,
      );
      if (
        this.destroyed
        || sequence !== this.sequence
      ) {
        return;
      }

      this.replaceAvatarUrl(
        URL.createObjectURL(blob),
      );
    } catch {
      if (sequence === this.sequence) {
        this.replaceAvatarUrl(null);
      }
    }
  }

  private loadThumbnails(
    items: readonly Media[],
  ): void {
    for (const media of items) {
      if (
        media.processingStatus === 'ready'
        && !this.thumbnails().has(media.id)
        && !this.thumbnailFailures().has(media.id)
        && !this.pendingThumbnails.has(media.id)
      ) {
        void this.loadThumbnail(media);
      }
    }
  }

  private async loadThumbnail(
    media: Media,
  ): Promise<void> {
    const sequence = this.sequence;
    this.pendingThumbnails.add(media.id);

    try {
      const blob =
        await this.mediaService().loadThumbnail(
          media.id,
          media.mediaType,
        );
      if (
        this.destroyed
        || sequence !== this.sequence
      ) {
        return;
      }

      const url = URL.createObjectURL(blob);
      this.thumbnails.update(current => {
        const next = new Map(current);
        next.set(media.id, url);
        return next;
      });
    } catch {
      if (sequence === this.sequence) {
        this.thumbnailFailures.update(current => {
          const next = new Set(current);
          next.add(media.id);
          return next;
        });
      }
    } finally {
      this.pendingThumbnails.delete(media.id);
    }
  }

  private resetGallery(): void {
    this.items.set([]);
    this.total.set(0);
    this.page.set(0);
  }

  private resetView(): void {
    this.sequence += 1;
    this.resetGallery();
    this.pickerOpen.set(false);
    this.pickerItems.set([]);
    this.pickerTotal.set(0);
    this.pickerPage.set(0);
    this.error.set(null);
    this.message.set(null);
    this.editing.set(false);
    this.clearObjectUrls();
  }

  private replaceAvatarUrl(url: string | null): void {
    const previous = this.avatarUrl();
    if (previous) {
      URL.revokeObjectURL(previous);
    }
    this.avatarUrl.set(url);
  }

  private clearObjectUrls(): void {
    this.replaceAvatarUrl(null);

    for (const url of this.thumbnails().values()) {
      URL.revokeObjectURL(url);
    }

    this.thumbnails.set(
      new Map<string, string>(),
    );
    this.thumbnailFailures.set(
      new Set<string>(),
    );
    this.pendingThumbnails.clear();
  }

  private errorMessage(error: unknown): string {
    if (
      error instanceof HttpErrorResponse
      && typeof error.error?.detail === 'string'
    ) {
      return error.error.detail;
    }

    if (error instanceof Error) {
      return error.message;
    }

    return 'Não foi possível concluir a operação.';
  }
}