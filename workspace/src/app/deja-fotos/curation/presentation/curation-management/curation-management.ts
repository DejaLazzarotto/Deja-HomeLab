import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, HostListener, OnDestroy, computed, effect, inject, input, signal } from '@angular/core';
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
interface AvatarFaceItem {
  readonly id: string;
  readonly media_id: string;
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}
interface AvatarFacePage extends Page<AvatarFaceItem> {}
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
  readonly canSelectEnvironment = input(false);
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
  readonly completionFilter = signal<"pending" | "completed">("pending");
  readonly mediaTotal = signal(0);
  readonly mediaPage = signal(0);
  readonly selectedMedia = signal<MediaItem | null>(null);
  readonly selectedMediaSupportsFaces = computed(() => this.selectedMedia()?.media_type === 'image');
  readonly mediaDescription = signal('');
  readonly mediaOriginalDate = signal('');
  readonly imageUrl = signal<string | null>(null);
  readonly videoUrl = signal<string | null>(null);
  readonly expandedImage = signal(false);
  readonly rotationDegrees = signal(0);
  readonly imageAspectRatio = signal(1);
  readonly rotationPreviewScale = computed(() => {
    const delta = (this.rotationDegrees() - this.savedRotationDegrees() + 360) % 360;
    if (delta % 180 === 0) return 1;
    const ratio = this.imageAspectRatio();
    return Math.min(ratio, 1 / ratio);
  });

  onReviewImageLoad(event: Event): void {
    const image = event.target as HTMLImageElement;
    if (image.naturalWidth > 0 && image.naturalHeight > 0) {
      this.imageAspectRatio.set(image.naturalWidth / image.naturalHeight);
    }
  }
  readonly savedRotationDegrees = signal(0);
  readonly rotationChanged = computed(
    () => this.rotationDegrees() !== this.savedRotationDegrees()
  );
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
  readonly avatarFaces = signal<readonly AvatarFaceItem[]>([]);
  readonly avatarFaceUrls = signal<ReadonlyMap<string, string>>(new Map());
  readonly avatarFacePage = signal(0);
  readonly avatarFaceTotal = signal(0);
  readonly avatarFaceLoading = signal(false);
  readonly summary = signal({ pending: 0, unknown: 0 });
  readonly loading = signal(false);
  readonly busy = signal(false);
  readonly error = signal<string | null>(null);
  readonly message = signal<string | null>(null);
  readonly drawing = signal(false);
  readonly draft = signal<Box | null>(null);

  private readonly http = inject(HttpClient);
  private mediaSequence = 0;
  private avatarFaceSequence = 0;
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

  @HostListener("document:keydown.escape")
  closeExpandedImage(): void {
    this.expandedImage.set(false);
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.mediaSequence++;
    this.faceSequence++;
    this.referenceSequence++;
    this.releaseImage();
    this.releaseReferences();
    this.releaseAvatarUrls();
    this.releaseAvatarFaceUrls();
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
    this.releaseAvatarFaceUrls();
    this.selectedAvatarPersonId.set('');
    this.avatarFaceSequence++;
    this.avatarFaceLoading.set(false);
    this.avatarFaces.set([]);
    this.avatarFacePage.set(0);
    this.avatarFaceTotal.set(0);
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
      this.people.set(
        (more ? [...this.people(), ...result.items] : [...result.items])
          .sort((a, b) => a.name.localeCompare(b.name, 'pt-BR', { sensitivity: 'base' }))
      );
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

  async setCurationCompleted(completed: boolean): Promise<void> {
    const item = this.selectedMedia();
    if (!item || !this.canManage() || this.busy()) return;

    this.busy.set(true);
    this.error.set(null);
    try {
      await firstValueFrom(this.http.post(
        `/api/fotos/curation/media/${item.id}/completion`,
        null,
        { params: new HttpParams().set("completed", completed) },
      ));
      await this.applyFilters(this.mediaPage() || 1);
    } catch (error: unknown) {
      this.error.set(error instanceof HttpErrorResponse && typeof error.error?.detail === 'string' ? error.error.detail : 'Não foi possível atualizar a situação da curadoria.');
    } finally {
      this.busy.set(false);
    }
  }

  async applyFilters(page = 1): Promise<void> {
    const request = ++this.mediaSequence;
    this.loading.set(true);
    this.error.set(null);
    this.selectMedia(null);
    let params = new HttpParams().set('page', page).set('page_size', 24)
      .set('situation', this.situationFilter())
      .set('completion_status', this.completionFilter());
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
    this.releaseVideo();
    this.expandedImage.set(false);
    this.selectedMedia.set(item);
    this.rotationDegrees.set(0);
    this.savedRotationDegrees.set(0);
    this.mediaDescription.set('');
    this.mediaOriginalDate.set(item?.original_date?.slice(0, 10) ?? '');
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
        try {
          const videoBlob = await firstValueFrom(this.http.get(`/api/fotos/media/${item.id}/preview`, { responseType: 'blob' }));
          if (request !== this.faceSequence || this.destroyed) return;
          this.videoUrl.set(URL.createObjectURL(videoBlob));
        } catch {
          if (request === this.faceSequence && !this.destroyed) this.error.set('Não foi possível carregar o vídeo para reprodução.');
        }
        return;
      }

      const [blob, faces, mediaDetail] = await Promise.all([
        firstValueFrom(this.http.get(`/api/fotos/media/${item.id}/${path}`, {
          responseType: 'blob',
        })),
        firstValueFrom(this.http.get<Page<FaceItem>>(
          `/api/fotos/curation/media/${item.id}/faces`,
          { params: { page: 1, page_size: 50 } },
        )),
        firstValueFrom(this.http.get<{ rotation_degrees: number }>(
          `/api/fotos/media/${item.id}`,
        )),
      ]);
      if (request !== this.faceSequence || this.destroyed) return;
      this.imageUrl.set(URL.createObjectURL(blob));
      this.savedRotationDegrees.set(mediaDetail.rotation_degrees ?? 0);
      this.rotationDegrees.set(mediaDetail.rotation_degrees ?? 0);
      this.faces.set(faces.items);
      this.facePage.set(faces.page);
      this.faceTotal.set(faces.total);
    } catch (error) {
      if (request === this.faceSequence) this.error.set(this.errorMessage(error));
    }
  }

  async saveOriginalDate(): Promise<void> {
    const item = this.selectedMedia();
    if (!item || !this.canManage()) return;

    const date = this.mediaOriginalDate();
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)
      || Number.isNaN(Date.parse(`${date}T12:00:00Z`))
      || new Date(`${date}T12:00:00Z`).toISOString().slice(0, 10) !== date) {
      this.error.set('Informe uma data válida (dia, mês e ano).');
      return;
    }

    await this.mutate(async () => {
      const updated = await firstValueFrom(this.http.patch<MediaItem>(
        `/api/fotos/media/${item.id}/original-date`,
        { original_date: `${date}T12:00:00Z` },
      ));
      const updatedItem = { ...item, original_date: updated.original_date };
      this.selectedMedia.set(updatedItem);
      this.media.update(items => items.map(media =>
        media.id === item.id ? updatedItem : media,
      ));
      this.mediaOriginalDate.set(updated.original_date?.slice(0, 10) ?? '');
    }, 'Data original da mídia salva.');
  }

  rotateImage(delta: number): void {
    if (!this.selectedMediaSupportsFaces() || !this.canManage() || this.busy()) return;
    this.rotationDegrees.update(angle => (angle + delta + 360) % 360);
  }

  async saveRotation(): Promise<void> {
    const item = this.selectedMedia();
    if (!item || item.media_type !== 'image' || !this.canManage()
      || this.busy() || !this.rotationChanged()) return;

    const requestedRotation = this.rotationDegrees();

    await this.mutate(async () => {
      await firstValueFrom(this.http.patch(
        `/api/fotos/media/${item.id}/rotation`,
        { rotation_degrees: requestedRotation },
      ));

      if (this.destroyed || this.selectedMedia()?.id !== item.id) return;

      await this.selectMedia(item);

      if (!this.imageUrl()) {
        throw new Error('Não foi possível recarregar a fotografia após salvar a orientação.');
      }

      this.savedRotationDegrees.set(requestedRotation);
      this.rotationDegrees.set(requestedRotation);
    }, 'Orientação da fotografia salva.');
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
    if (!this.drawing() || !this.canManage() || this.rotationChanged() || this.busy()) return;
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
      this.people.update(items => [...items, person].sort((a, b) => a.name.localeCompare(b.name, 'pt-BR', { sensitivity: 'base' })));
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

    this.releaseAvatarFaceUrls();
    this.avatarFaces.set([]);
    this.avatarFacePage.set(0);
    this.avatarFaceTotal.set(0);
    this.avatarFaceSequence++;
    this.avatarFaceLoading.set(false);

    await this.loadAvatarFaces();
  }

  async loadAvatarFaces(more = false): Promise<void> {
    const personId = this.selectedAvatarPersonId();

    if (!personId || this.avatarFaceLoading()) {
      return;
    }

    const page = more ? this.avatarFacePage() + 1 : 1;

    if (more && this.avatarFacePage() === 0) {
      return;
    }

    if (more && this.avatarFaces().length >= this.avatarFaceTotal()) {
      return;
    }

    const sequence = ++this.avatarFaceSequence;
    this.avatarFaceLoading.set(true);
    this.error.set(null);

    try {
      const result = await firstValueFrom(
        this.http.get<AvatarFacePage>(
          `/api/fotos/people/${personId}/avatar/faces`,
          {
            params: {
              page,
              page_size: 50,
            },
          },
        ),
      );

      if (this.destroyed || personId !== this.selectedAvatarPersonId() || sequence !== this.avatarFaceSequence) {
        return;
      }

      this.avatarFaces.set(
        more
          ? [...this.avatarFaces(), ...result.items]
          : result.items,
      );
      this.avatarFacePage.set(result.page);
      this.avatarFaceTotal.set(result.total);

      for (const face of result.items) {
        try {
          const blob = await firstValueFrom(
            this.http.get(
              `/api/fotos/people/${personId}/avatar/faces/${face.id}/preview`,
              { responseType: 'blob' },
            ),
          );

          if (this.destroyed || personId !== this.selectedAvatarPersonId() || sequence !== this.avatarFaceSequence) {
            return;
          }

          const url = URL.createObjectURL(blob);

          this.avatarFaceUrls.update(current => {
            const next = new Map(current);
            const previous = next.get(face.id);

            if (previous) {
              URL.revokeObjectURL(previous);
            }

            next.set(face.id, url);
            return next;
          });
        } catch {
          // O candidato permanece listado caso a miniatura falhe.
        }
      }
    } catch (error) {
      if (!this.destroyed && personId === this.selectedAvatarPersonId() && sequence === this.avatarFaceSequence) {
        this.error.set(this.errorMessage(error));
      }
    } finally {
      if (sequence === this.avatarFaceSequence) {
        this.avatarFaceLoading.set(false);
      }
    }
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

  async useFaceAsAvatar(
    personId: string,
    faceId: string,
  ): Promise<void> {
    if (
      !personId
      || !faceId
      || personId !== this.selectedAvatarPersonId()
      || !this.canManage()
      || this.busy()
    ) {
      return;
    }

    await this.mutate(
      async () => {
        const updated = await firstValueFrom(
          this.http.put<PersonItem>(
            `/api/fotos/people/${personId}/avatar/faces/${faceId}`,
            {},
          ),
        );

        this.replacePerson(updated);
        await this.refreshAvatar(updated);
      },
      'Rosto definido como avatar.',
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

  private releaseAvatarFaceUrls(): void {
    for (const url of this.avatarFaceUrls().values()) {
      URL.revokeObjectURL(url);
    }

    this.avatarFaceUrls.set(new Map());
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

  private releaseVideo(): void {
    const url = this.videoUrl();
    if (url) URL.revokeObjectURL(url);
    this.videoUrl.set(null);
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