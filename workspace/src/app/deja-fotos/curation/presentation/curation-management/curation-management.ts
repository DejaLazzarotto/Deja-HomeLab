import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, OnDestroy, computed, effect, inject, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { FotosEnvironmentOption } from '../../../fotos-environment-option';

interface Page<T> {
  readonly items: readonly T[];
  readonly page: number;
  readonly total: number;
  readonly total_pages: number;
}
interface MediaItem {
  readonly id: string;
  readonly original_name: string;
  readonly media_type: 'image' | 'video';
  readonly original_date: string | null;
  readonly description?: string | null;
}
interface PersonItem {
  readonly id: string;
  readonly name: string;
  readonly avatar_content_type: string | null;
}
interface AlbumItem { readonly id: string; readonly name: string; }
interface FaceItem {
  readonly id: string;
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly origin: 'detected' | 'manual';
  readonly status: 'unknown' | 'suggested' | 'confirmed' | 'rejected';
  readonly person_id: string | null;
  readonly confidence: number | null;
}
interface ReferenceItem {
  readonly id: string;
  readonly face_id: string;
  readonly person_id: string;
}
interface PersonMediaItem {
  readonly id: string;
  readonly original_name: string;
  readonly media_type: 'image' | 'video';
}
interface PersonMediaPage {
  readonly items: readonly PersonMediaItem[];
  readonly page: number;
  readonly total: number;
  readonly total_pages: number;
}
interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}
type CurationTab = 'recognition' | 'people' | 'avatars';

@Component({
  selector: 'deja-curation-management',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './curation-management.html',
  styleUrl: './curation-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CurationManagementComponent implements OnDestroy {
  readonly environments = input<readonly FotosEnvironmentOption[]>([]);
  readonly defaultEnvironmentId = input<string | null>(null);
  readonly canManage = input(false);
  readonly activeTab = signal<CurationTab>(this.restoreActiveTab());
  readonly environmentId = signal('');
  readonly situationFilter = signal('all');
  readonly personFilter = signal('');
  readonly albumFilter = signal('');
  readonly yearFilter = signal('');
  readonly monthFilter = signal('');
  readonly people = signal<readonly PersonItem[]>([]);
  readonly peopleTotal = signal(0);
  readonly peoplePage = signal(0);
  readonly albums = signal<readonly AlbumItem[]>([]);
  readonly media = signal<readonly MediaItem[]>([]);
  readonly mediaTotal = signal(0);
  readonly mediaPage = signal(0);
  readonly selectedMedia = signal<MediaItem | null>(null);
  readonly selectedMediaSupportsFaces = computed(() => this.selectedMedia()?.media_type === 'image');
  readonly mediaDescription = signal('');
  readonly imageUrl = signal<string | null>(null);
  readonly faces = signal<readonly FaceItem[]>([]);
  readonly faceTotal = signal(0);
  readonly facePage = signal(0);
  readonly selectedFaceId = signal<string | null>(null);
  readonly chosenPersonId = signal('');
  readonly creatingPerson = signal(false);
  readonly newPersonName = signal('');
  readonly references = signal<readonly ReferenceItem[]>([]);
  readonly referenceUrls = signal<ReadonlyMap<string, string>>(new Map());
  readonly referencePage = signal(0);
  readonly referenceTotal = signal(0);
  readonly avatarUrls = signal<ReadonlyMap<string, string>>(new Map());
  readonly selectedAvatarPersonId = signal('');
  readonly avatarMedia = signal<readonly PersonMediaItem[]>([]);
  readonly avatarMediaUrls = signal<ReadonlyMap<string, string>>(new Map());
  readonly avatarMediaPage = signal(0);
  readonly avatarMediaTotal = signal(0);
  readonly avatarLoading = signal(false);
  readonly summary = signal({ pending: 0, unknown: 0 });
  readonly loading = signal(false);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);
  readonly message = signal<string | null>(null);
  readonly drawing = signal(false);
  readonly draft = signal<Box | null>(null);

  private readonly http = inject(HttpClient);
  private mediaSequence = 0;
  private faceSequence = 0;
  private referenceSequence = 0;
  private destroyed = false;
  private dragStart: { x: number; y: number } | null = null;

  constructor() {
    effect(() => {
      const options = this.environments();
      const preferred = this.defaultEnvironmentId();
      if ((options.length || preferred) && !this.environmentId()) {
        this.changeEnvironment(
          options.find(option => option.id === preferred)?.id
            ?? preferred ?? options[0].id,
        );
      }
    });
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.mediaSequence++;
    this.faceSequence++;
    this.referenceSequence++;
    this.releaseImage();
    this.releaseReferences();
    this.releaseAvatarUrls();
    this.releaseAvatarMediaUrls();
  }

  selectTab(tab: CurationTab): void {
    this.activeTab.set(tab);
    sessionStorage.setItem('deja-fotos-curation-active-tab', tab);
    if (tab === 'people') void this.loadReferences();
    if (tab === 'avatars') void this.loadAvatarUrls();
  }

  changeEnvironment(id: string): void {
    this.environmentId.set(id);
    this.personFilter.set('');
    this.creatingPerson.set(false);
    this.newPersonName.set('');
    this.albumFilter.set('');
    this.referenceSequence++;
    this.releaseReferences();
    this.releaseAvatarUrls();
    this.releaseAvatarMediaUrls();
    this.selectedAvatarPersonId.set('');
    this.avatarMedia.set([]);
    this.avatarMediaPage.set(0);
    this.avatarMediaTotal.set(0);
    this.references.set([]);
    this.people.set([]);
    this.albums.set([]);
    void this.loadPeople();
    void this.loadAlbums();
    void this.applyFilters();
  }

  async loadPeople(more = false): Promise<void> {
    const environment = this.environmentId();
    const page = more ? this.peoplePage() + 1 : 1;
    try {
      const result = await firstValueFrom(this.http.get<Page<PersonItem>>(
        '/api/fotos/people', { params: new HttpParams()
          .set('environment_id', environment).set('page', page).set('page_size', 200) },
      ));
      if (this.destroyed || environment !== this.environmentId()) return;
      this.people.set(more ? [...this.people(), ...result.items] : result.items);
      this.peopleTotal.set(result.total);
      this.peoplePage.set(result.page);

      if (this.activeTab() === 'avatars') {
        void this.loadAvatarUrls();
      }
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  async loadAlbums(): Promise<void> {
    const environment = this.environmentId();
    try {
      const items = await firstValueFrom(this.http.get<readonly AlbumItem[]>(
        '/api/fotos/albums', { params: { environment_id: environment } },
      ));
      if (!this.destroyed && environment === this.environmentId()) this.albums.set(items);
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  async applyFilters(page = 1): Promise<void> {
    const request = ++this.mediaSequence;
    this.loading.set(true);
    this.error.set(null);
    this.selectMedia(null);
    let params = new HttpParams().set('page', page).set('page_size', 24)
      .set('situation', this.situationFilter());
    if (this.environmentId()) params = params.set('environment_id', this.environmentId());
    if (this.personFilter()) params = params.set('person_id', this.personFilter());
    if (this.albumFilter()) params = params.set('album_id', this.albumFilter());
    if (this.yearFilter()) params = params.set('year', this.yearFilter());
    if (this.monthFilter()) params = params.set('month', this.monthFilter());
    try {
      const result = await firstValueFrom(this.http.get<Page<MediaItem>>(
        '/api/fotos/curation/media', { params },
      ));
      if (request !== this.mediaSequence || this.destroyed) return;
      this.media.set(result.items);
      this.mediaTotal.set(result.total);
      this.mediaPage.set(result.page);
      if (result.items.length) void this.selectMedia(result.items[0]);
      void this.loadSummary();
    } catch (error) {
      if (request === this.mediaSequence) this.error.set(this.errorMessage(error));
    } finally {
      if (request === this.mediaSequence) this.loading.set(false);
    }
  }

  async loadSummary(): Promise<void> {
    const environment = this.environmentId();
    try {
      const params = environment
        ? new HttpParams().set('environment_id', environment)
        : new HttpParams();
      const result = await firstValueFrom(this.http.get<{ pending: number; unknown: number }>(
        '/api/fotos/curation/summary', { params },
      ));
      if (!this.destroyed && environment === this.environmentId()) this.summary.set(result);
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  async selectMedia(item: MediaItem | null): Promise<void> {
    const request = ++this.faceSequence;
    this.releaseImage();
    this.selectedMedia.set(item);
    this.mediaDescription.set('');
    this.faces.set([]);
    this.facePage.set(0);
    this.faceTotal.set(0);
    this.selectedFaceId.set(null);
    this.drawing.set(false);
    this.draft.set(null);
    if (!item) return;
    try {
      const path = item.media_type === 'video' ? 'poster' : 'preview';
      if (item.media_type === 'video') {
        const [blob, mediaDetail] = await Promise.all([
          firstValueFrom(this.http.get(`/api/fotos/media/${item.id}/poster`, {
            responseType: 'blob',
          })),
          firstValueFrom(this.http.get<{ description: string | null }>(
            `/api/fotos/media/${item.id}`,
          )),
        ]);
        if (request !== this.faceSequence || this.destroyed) return;
        this.imageUrl.set(URL.createObjectURL(blob));
        this.mediaDescription.set(mediaDetail.description ?? item.description ?? '');
        return;
      }

      const [blob, faces] = await Promise.all([
        firstValueFrom(this.http.get(`/api/fotos/media/${item.id}/${path}`, {
          responseType: 'blob',
        })),
        firstValueFrom(this.http.get<Page<FaceItem>>(
          `/api/fotos/curation/media/${item.id}/faces`,
          { params: { page: 1, page_size: 50 } },
        )),
      ]);
      if (request !== this.faceSequence || this.destroyed) return;
      this.imageUrl.set(URL.createObjectURL(blob));
      this.faces.set(faces.items);
      this.facePage.set(faces.page);
      this.faceTotal.set(faces.total);
    } catch (error) {
      if (request === this.faceSequence) this.error.set(this.errorMessage(error));
    }
  }

  async saveDescription(): Promise<void> {
    const item = this.selectedMedia();
    if (!item || item.media_type !== 'video' || !this.canManage()) return;

    const description = this.mediaDescription().trim();
    if (description.length > 5000) {
      this.error.set('A descrição deve ter no máximo 5.000 caracteres.');
      return;
    }

    await this.mutate(async () => {
      const updated = await firstValueFrom(this.http.patch<{ description: string | null }>(
        `/api/fotos/media/${item.id}/description`,
        { description: description || null },
      ));
      const savedDescription = updated.description ?? '';
      this.mediaDescription.set(savedDescription);
      const updatedItem = { ...item, description: updated.description };
      this.selectedMedia.set(updatedItem);
      this.media.update(items => items.map(media =>
        media.id === item.id ? updatedItem : media,
      ));
    }, 'Descrição da mídia salva.');
  }

  async loadMoreFaces(): Promise<void> {
    const item = this.selectedMedia();
    if (!item || item.media_type !== 'image' || this.facePage() * 50 >= this.faceTotal()) return;
    try {
      const result = await firstValueFrom(this.http.get<Page<FaceItem>>(
        `/api/fotos/curation/media/${item.id}/faces`,
        { params: { page: this.facePage() + 1, page_size: 50 } },
      ));
      if (this.selectedMedia()?.id !== item.id || this.destroyed) return;
      this.faces.update(items => [...items, ...result.items]);
      this.facePage.set(result.page);
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  selectFace(face: FaceItem): void {
    this.selectedFaceId.set(face.id);
    this.chosenPersonId.set(face.person_id ?? '');
  }

  selectedFace(): FaceItem | undefined {
    return this.faces().find(face => face.id === this.selectedFaceId());
  }

  personName(id: string | null): string {
    return this.people().find(person => person.id === id)?.name ?? 'Sem identificação';
  }

  private pointerPosition(event: PointerEvent): { x: number; y: number } {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
    };
  }

  pointerDown(event: PointerEvent): void {
    if (!this.drawing() || !this.canManage()) return;
    event.preventDefault();
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
    this.dragStart = this.pointerPosition(event);
    this.draft.set({ ...this.dragStart, width: 0, height: 0 });
  }

  pointerMove(event: PointerEvent): void {
    if (!this.dragStart) return;
    const point = this.pointerPosition(event);
    this.draft.set({
      x: Math.min(this.dragStart.x, point.x),
      y: Math.min(this.dragStart.y, point.y),
      width: Math.abs(this.dragStart.x - point.x),
      height: Math.abs(this.dragStart.y - point.y),
    });
  }

  pointerUp(event: PointerEvent): void {
    if (!this.dragStart) return;
    this.pointerMove(event);
    this.dragStart = null;
    if ((this.draft()?.width ?? 0) < 0.02 || (this.draft()?.height ?? 0) < 0.02) {
      this.draft.set(null);
      this.message.set('Desenhe um quadrado maior sobre o rosto.');
    }
  }

  async saveDrawing(): Promise<void> {
    const item = this.selectedMedia();
    const box = this.draft();
    if (!item || !box || !this.canManage()) return;
    await this.mutate(async () => {
      const face = await firstValueFrom(this.http.post<FaceItem>(
        `/api/fotos/curation/media/${item.id}/faces`,
        { ...box, person_id: this.chosenPersonId() || null },
      ));
      this.faces.update(items => [...items, face]);
      this.faceTotal.update(count => count + 1);
      this.draft.set(null);
      this.drawing.set(false);
      this.selectFace(face);
    }, 'Rosto marcado com sucesso.');
  }

  async detect(): Promise<void> {
    const item = this.selectedMedia();
    if (!item || !this.canManage()) return;
    await this.mutate(async () => {
      const faces = await firstValueFrom(this.http.post<readonly FaceItem[]>(
        `/api/fotos/curation/media/${item.id}/detect`, {},
      ));
      if (this.destroyed || this.selectedMedia()?.id !== item.id) return;
      const selectedId = this.selectedFaceId();
      await this.selectMedia(item);
      const selected = this.faces().find(face => face.id === selectedId);
      if (selected) this.selectFace(selected);
      this.message.set(faces.length
        ? `${faces.length} rosto(s) novo(s) ou atualizado(s) para revisão.`
        : 'Nenhum rosto novo ou sugestão. Você pode corrigir ou desenhar uma marcação.');
    });
  }

  async createPerson(): Promise<void> {
    const name = this.newPersonName().trim();
    const environment = this.environmentId();
    if (!name || !environment || !this.canManage()) return;
    await this.mutate(async () => {
      const person = await firstValueFrom(this.http.post<PersonItem>(
        '/api/fotos/people', { environment_id: environment, name },
      ));
      if (this.destroyed || environment !== this.environmentId()) return;
      this.people.update(items => [person, ...items]);
      this.peopleTotal.update(total => total + 1);
      this.chosenPersonId.set(person.id);
      this.newPersonName.set('');
      this.creatingPerson.set(false);
    }, 'Pessoa cadastrada. Confirme a identificação do rosto selecionado.');
  }

  async confirm(): Promise<void> {
    const face = this.selectedFace();
    if (!face || !this.chosenPersonId() || !this.canManage()) return;
    await this.mutate(async () => {
      const updated = await firstValueFrom(this.http.post<FaceItem>(
        `/api/fotos/curation/faces/${face.id}/confirm`,
        { person_id: this.chosenPersonId() },
      ));
      this.replaceFace(updated);
    }, 'Identificação confirmada.');
  }

  async reject(): Promise<void> {
    const face = this.selectedFace();
    if (!face || face.status !== 'suggested' || !this.canManage()) return;
    await this.mutate(async () => {
      const updated = await firstValueFrom(this.http.post<FaceItem>(
        `/api/fotos/curation/faces/${face.id}/reject`, {},
      ));
      this.replaceFace(updated);
      this.chosenPersonId.set('');
    }, 'Sugestão rejeitada.');
  }

  async removeFace(): Promise<void> {
    const face = this.selectedFace();
    if (!face || !this.canManage()) return;
    await this.mutate(async () => {
      await firstValueFrom(this.http.delete(`/api/fotos/curation/faces/${face.id}`));
      this.faces.update(items => items.filter(item => item.id !== face.id));
      this.faceTotal.update(count => count - 1);
      this.selectedFaceId.set(null);
    }, 'Marcação removida.');
  }

  async teach(): Promise<void> {
    const face = this.selectedFace();
    if (!face || face.status !== 'confirmed' || !this.canManage()) return;
    await this.mutate(async () => {
      await firstValueFrom(this.http.post(`/api/fotos/curation/faces/${face.id}/teach`, {}));
      await this.loadReferences();
    }, 'Referência facial salva para futuras sugestões.');
  }

  async loadReferences(page = 1): Promise<void> {
    const personId = this.personFilter() || this.selectedFace()?.person_id;
    const request = ++this.referenceSequence;
    if (!personId) {
      this.releaseReferences();
      this.references.set([]);
      this.referenceTotal.set(0);
      return;
    }
    try {
      const result = await firstValueFrom(this.http.get<Page<ReferenceItem>>(
        `/api/fotos/curation/people/${personId}/references`,
        { params: { page, page_size: 50 } },
      ));
      if (this.destroyed || request !== this.referenceSequence) return;
      if (page === 1) this.releaseReferences();
      this.references.set(page === 1 ? result.items : [...this.references(), ...result.items]);
      this.referencePage.set(result.page);
      this.referenceTotal.set(result.total);
      for (const reference of result.items) {
        try {
          const blob = await firstValueFrom(this.http.get(
            `/api/fotos/curation/references/${reference.id}/image`,
            { responseType: 'blob' },
          ));
          if (this.destroyed || request !== this.referenceSequence) return;
          const url = URL.createObjectURL(blob);
          this.referenceUrls.update(previous => new Map(previous).set(reference.id, url));
        } catch {
          // A referência continua listada mesmo que seu arquivo esteja indisponível.
        }
      }
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  async removeReference(id: string): Promise<void> {
    if (!this.canManage()) return;
    await this.mutate(async () => {
      await firstValueFrom(this.http.delete(`/api/fotos/curation/references/${id}`));
      await this.loadReferences();
    }, 'Referência removida.');
  }

  async selectAvatarPerson(personId: string): Promise<void> {
    if (
      !personId
      || personId === this.selectedAvatarPersonId()
    ) {
      return;
    }

    this.selectedAvatarPersonId.set(personId);
    this.avatarMedia.set([]);
    this.avatarMediaPage.set(0);
    this.avatarMediaTotal.set(0);
    this.releaseAvatarMediaUrls();

    await this.loadAvatarMedia();
  }

  async loadAvatarMedia(more = false): Promise<void> {
    const personId = this.selectedAvatarPersonId();

    if (
      !personId
      || this.avatarLoading()
    ) {
      return;
    }

    const page =
      more
        ? this.avatarMediaPage() + 1
        : 1;

    this.avatarLoading.set(true);
    this.error.set(null);

    try {
      const result = await firstValueFrom(
        this.http.get<PersonMediaPage>(
          `/api/fotos/people/${personId}/media`,
          {
            params: {
              page,
              page_size: 50,
            },
          },
        ),
      );

      if (
        this.destroyed
        || personId !== this.selectedAvatarPersonId()
      ) {
        return;
      }

      const images = result.items.filter(
        item => item.media_type === 'image',
      );

      this.avatarMedia.set(
        more
          ? [
              ...this.avatarMedia(),
              ...images,
            ]
          : images,
      );

      this.avatarMediaPage.set(result.page);
      this.avatarMediaTotal.set(result.total);

      for (const item of images) {
        try {
          const blob = await firstValueFrom(
            this.http.get(
              `/api/fotos/media/${item.id}/thumbnail`,
              {
                responseType: 'blob',
              },
            ),
          );

          if (
            this.destroyed
            || personId !== this.selectedAvatarPersonId()
          ) {
            return;
          }

          const url = URL.createObjectURL(blob);

          this.avatarMediaUrls.update(current => {
            const next = new Map(current);
            next.set(item.id, url);
            return next;
          });
        } catch {
          // A foto continua disponível mesmo sem miniatura.
        }
      }
    } catch (error) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.avatarLoading.set(false);
    }
  }

  async uploadAvatar(
    personId: string,
    file: File | null,
  ): Promise<void> {
    if (
      !file
      || !this.canManage()
      || this.busy()
    ) {
      return;
    }

    await this.mutate(
      async () => {
        const formData = new FormData();
        formData.append('file', file);

        const updated = await firstValueFrom(
          this.http.put<PersonItem>(
            `/api/fotos/people/${personId}/avatar`,
            formData,
          ),
        );

        this.replacePerson(updated);
        await this.refreshAvatar(updated);
      },
      'Avatar atualizado.',
    );
  }

  async removeAvatar(
    personId: string,
  ): Promise<void> {
    if (
      !this.canManage()
      || this.busy()
    ) {
      return;
    }

    await this.mutate(
      async () => {
        const updated = await firstValueFrom(
          this.http.delete<PersonItem>(
            `/api/fotos/people/${personId}/avatar`,
          ),
        );

        this.replacePerson(updated);
        this.replaceAvatarUrl(
          personId,
          null,
        );
      },
      'Avatar removido.',
    );
  }

  async useMediaAsAvatar(
    personId: string,
    mediaId: string,
  ): Promise<void> {
    if (
      !this.canManage()
      || this.busy()
    ) {
      return;
    }

    await this.mutate(
      async () => {
        const blob = await firstValueFrom(
          this.http.get(
            `/api/fotos/media/${mediaId}/preview`,
            {
              responseType: 'blob',
            },
          ),
        );

        const file = new File(
          [blob],
          'avatar.webp',
          {
            type:
              blob.type
              || 'image/webp',
          },
        );

        const formData = new FormData();
        formData.append('file', file);

        const updated = await firstValueFrom(
          this.http.put<PersonItem>(
            `/api/fotos/people/${personId}/avatar`,
            formData,
          ),
        );

        this.replacePerson(updated);
        await this.refreshAvatar(updated);
      },
      'Foto definida como avatar.',
    );
  }

  private replacePerson(
    person: PersonItem,
  ): void {
    this.people.update(items =>
      items.map(item =>
        item.id === person.id
          ? person
          : item,
      ),
    );
  }

  private async refreshAvatar(
    person: PersonItem,
  ): Promise<void> {
    if (!person.avatar_content_type) {
      this.replaceAvatarUrl(
        person.id,
        null,
      );

      return;
    }

    const blob = await firstValueFrom(
      this.http.get(
        `/api/fotos/people/${person.id}/avatar`,
        {
          responseType: 'blob',
        },
      ),
    );

    if (this.destroyed) {
      return;
    }

    this.replaceAvatarUrl(
      person.id,
      URL.createObjectURL(blob),
    );
  }

  private replaceAvatarUrl(
    personId: string,
    url: string | null,
  ): void {
    const current =
      this.avatarUrls().get(personId);

    if (current) {
      URL.revokeObjectURL(current);
    }

    this.avatarUrls.update(previous => {
      const next = new Map(previous);

      if (url) {
        next.set(personId, url);
      } else {
        next.delete(personId);
      }

      return next;
    });
  }

  private releaseAvatarMediaUrls(): void {
    for (
      const url
      of this.avatarMediaUrls().values()
    ) {
      URL.revokeObjectURL(url);
    }

    this.avatarMediaUrls.set(
      new Map(),
    );
  }

  private replaceFace(face: FaceItem): void {
    this.faces.update(items => items.map(item => item.id === face.id ? face : item));
  }

  private async mutate(action: () => Promise<void>, success?: string): Promise<void> {
    if (this.busy()) return;
    this.busy.set(true);
    this.error.set(null);
    this.message.set(null);
    try {
      await action();
      if (success) this.message.set(success);
      void this.loadSummary();
    } catch (error) {
      this.error.set(this.errorMessage(error));
    } finally {
      this.busy.set(false);
    }
  }

  private releaseImage(): void {
    const url = this.imageUrl();
    if (url) URL.revokeObjectURL(url);
    this.imageUrl.set(null);
  }

  private releaseReferences(): void {
    for (const url of this.referenceUrls().values()) URL.revokeObjectURL(url);
    this.referenceUrls.set(new Map());
  }

  private async loadAvatarUrls(): Promise<void> {
    this.releaseAvatarUrls();

    const people = this.people();

    for (const person of people) {
      if (!person.avatar_content_type) continue;

      try {
        const blob = await firstValueFrom(this.http.get(
          `/api/fotos/people/${person.id}/avatar`,
          { responseType: 'blob' },
        ));

        if (this.destroyed || this.activeTab() !== 'avatars') return;

        const url = URL.createObjectURL(blob);
        this.avatarUrls.update(current => {
          const next = new Map(current);
          next.set(person.id, url);
          return next;
        });
      } catch {
        // A pessoa continua disponível mesmo se o avatar estiver ausente.
      }
    }
  }

  private releaseAvatarUrls(): void {
    for (const url of this.avatarUrls().values()) URL.revokeObjectURL(url);
    this.avatarUrls.set(new Map());
  }

  private restoreActiveTab(): CurationTab {
    const tab = sessionStorage.getItem('deja-fotos-curation-active-tab');

    if (
      tab === 'recognition'
      || tab === 'people'
      || tab === 'avatars'
    ) {
      return tab;
    }

    return 'recognition';
  }

  private errorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      const detail = error.error?.message ?? error.error?.detail;
      if (typeof detail === 'string') return detail;
      if (error.status === 403) return 'Você não tem permissão para esta ação.';
      if (error.status === 503) return 'Motor facial indisponível. Instale a opção faces da API.';
    }
    return 'Não foi possível concluir a operação. Tente novamente.';
  }
}