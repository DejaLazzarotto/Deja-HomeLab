import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { CurationManagementComponent } from './curation-management';

describe('CurationManagementComponent', () => {
  let fixture: ComponentFixture<CurationManagementComponent>;
  let component: CurationManagementComponent;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CurationManagementComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    fixture = TestBed.createComponent(CurationManagementComponent);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  it('clears previous avatar faces when selecting another person', async () => {
    component.selectedAvatarPersonId.set('person-a');
    component.avatarFaces.set([
      {
        id: 'face-a',
        media_id: 'media-a',
        x: 0.1,
        y: 0.1,
        width: 0.3,
        height: 0.3,
      },
    ]);
    component.avatarFacePage.set(1);
    component.avatarFaceTotal.set(1);

    const selecting = component.selectAvatarPerson('person-b');

    expect(component.selectedAvatarPersonId()).toBe('person-b');
    expect(component.avatarFaces()).toEqual([]);
    expect(component.avatarFacePage()).toBe(0);
    expect(component.avatarFaceTotal()).toBe(0);


    let facesRequest: ReturnType<HttpTestingController['expectOne']> | undefined;

    await vi.waitFor(() => {
      const pending = http.match(
        '/api/fotos/people/person-b/avatar/faces?page=1&page_size=50',
      );
      expect(pending.length).toBe(1);
      facesRequest = pending[0];
    });

    if (!facesRequest) {
      throw new Error('Requisição de rostos não encontrada.');
    }

    facesRequest.flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await selecting;
  });
  it('ignores avatar faces returned for a previously selected person', async () => {
    const selectingA = component.selectAvatarPerson('person-a');


    let facesA: ReturnType<HttpTestingController['expectOne']> | undefined;

    await vi.waitFor(() => {
      const requests = http.match(
        '/api/fotos/people/person-a/avatar/faces?page=1&page_size=50',
      );
      expect(requests.length).toBe(1);
      facesA = requests[0];
    });

    const selectingB = component.selectAvatarPerson('person-b');


    if (!facesA) {
      throw new Error('Requisição da pessoa A não encontrada.');
    }

    facesA.flush({
      items: [
        { id: 'face-a', media_id: 'media-a',
          x: 0.1, y: 0.1, width: 0.3, height: 0.3 },
      ],
      page: 1,
      total: 1,
      total_pages: 1,
    });

    await selectingA;

    let facesB: ReturnType<HttpTestingController['expectOne']> | undefined;

    await vi.waitFor(() => {
      const requests = http.match(
        '/api/fotos/people/person-b/avatar/faces?page=1&page_size=50',
      );
      expect(requests.length).toBe(1);
      facesB = requests[0];
    });

    if (!facesB) {
      throw new Error('Requisição da pessoa B não encontrada.');
    }

    facesB.flush({
      items: [
        { id: 'face-b', media_id: 'media-b',
          x: 0.2, y: 0.2, width: 0.4, height: 0.4 },
      ],
      page: 1,
      total: 1,
      total_pages: 1,
    });

    let previewB: ReturnType<HttpTestingController['expectOne']> | undefined;

    await vi.waitFor(() => {
      const requests = http.match(
        '/api/fotos/people/person-b/avatar/faces/face-b/preview',
      );
      expect(requests.length).toBe(1);
      previewB = requests[0];
    });

    if (!previewB) {
      throw new Error('Miniatura da pessoa B não encontrada.');
    }

    previewB.flush(new Blob(['imagem-b'], { type: 'image/webp' }));

    await selectingB;

    expect(component.selectedAvatarPersonId()).toBe('person-b');
    expect(component.avatarFaces().map(face => face.id)).toEqual(['face-b']);
    expect(component.avatarFaces().some(face => face.id === 'face-a')).toBe(false);
  });
  it('keeps the current avatar loading state when an old request finishes', async () => {
    const loadingA = component.selectAvatarPerson('person-a');


    let facesA: ReturnType<HttpTestingController['expectOne']> | undefined;

    await vi.waitFor(() => {
      const requests = http.match(
        '/api/fotos/people/person-a/avatar/faces?page=1&page_size=50',
      );
      expect(requests.length).toBe(1);
      facesA = requests[0];
    });

    const loadingB = component.selectAvatarPerson('person-b');


    let facesB: ReturnType<HttpTestingController['expectOne']> | undefined;

    await vi.waitFor(() => {
      const requests = http.match(
        '/api/fotos/people/person-b/avatar/faces?page=1&page_size=50',
      );
      expect(requests.length).toBe(1);
      facesB = requests[0];
    });

    expect(component.avatarFaceLoading()).toBe(true);

    if (!facesA || !facesB) {
      throw new Error('Requisições esperadas não encontradas.');
    }

    facesA.flush({ items: [], page: 1, total: 0, total_pages: 0 });
    await loadingA;

    expect(component.avatarFaceLoading()).toBe(true);
    expect(component.selectedAvatarPersonId()).toBe('person-b');

    facesB.flush({ items: [], page: 1, total: 0, total_pages: 0 });
    await loadingB;

    expect(component.avatarFaceLoading()).toBe(false);
  });
  it('shows live counters and the existing tabs without false empty claims', () => {
    expect(component.activeTab()).toBe('recognition');
    component.summary.set({ pending: 3, unknown: 2 });
    component.peopleTotal.set(1);
    fixture.detectChanges();
    const content = (fixture.nativeElement as HTMLElement).textContent ?? '';
    expect(content).toContain('3');
    expect(content).toContain('Pessoas cadastradas');
    component.selectTab('avatars');
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain(
      'não são usados automaticamente como referência para reconhecimento facial',
    );
  });

  it('saves a missing original date for an image', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    const media = {
      id: 'image-date-1',
      original_name: 'foto.jpg',
      media_type: 'image' as const,
      original_date: null,
    };
    component.selectedMedia.set(media);
    component.media.set([media]);
    component.mediaOriginalDate.set('2008-04-15');

    const saving = component.saveOriginalDate();
    const request = http.expectOne('/api/fotos/media/image-date-1/original-date');

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual({
      original_date: '2008-04-15T12:00:00Z',
    });

    request.flush({ ...media, original_date: '2008-04-15T12:00:00' });
    await saving;

    expect(component.selectedMedia()?.original_date).toBe('2008-04-15T12:00:00');
    expect(component.media()[0].original_date).toBe('2008-04-15T12:00:00');
    expect(component.mediaOriginalDate()).toBe('2008-04-15');
    expect(component.message()).toContain('salva');

    http.expectOne('/api/fotos/curation/summary')
      .flush({ pending: 0, unknown: 0 });
  });

  it('corrects an existing original date for a video', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    const media = {
      id: 'video-date-1',
      original_name: 'video.mp4',
      media_type: 'video' as const,
      original_date: '2007-01-01T12:00:00',
    };
    component.selectedMedia.set(media);
    component.media.set([media]);
    component.mediaOriginalDate.set('2008-04-15');

    const saving = component.saveOriginalDate();
    const request = http.expectOne('/api/fotos/media/video-date-1/original-date');

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual({
      original_date: '2008-04-15T12:00:00Z',
    });

    request.flush({ ...media, original_date: '2008-04-15T12:00:00' });
    await saving;

    expect(component.selectedMedia()?.original_date).toBe('2008-04-15T12:00:00');
    expect(component.media()[0].original_date).toBe('2008-04-15T12:00:00');
    expect(component.mediaOriginalDate()).toBe('2008-04-15');

    http.expectOne('/api/fotos/curation/summary')
      .flush({ pending: 0, unknown: 0 });
  });
  it('saves a manual box with normalized coordinates and a person ID', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();
    component.selectedMedia.set({ id: 'media-1', original_name: 'foto.jpg',
      media_type: 'image', original_date: null });
    component.draft.set({ x: 0.1, y: 0.2, width: 0.3, height: 0.4 });
    component.chosenPersonId.set('person-1');
    const saving = component.saveDrawing();
    const request = http.expectOne('/api/fotos/curation/media/media-1/faces');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      x: 0.1, y: 0.2, width: 0.3, height: 0.4, person_id: 'person-1',
    });
    request.flush({ id: 'face-1', x: 0.1, y: 0.2, width: 0.3, height: 0.4,
      status: 'confirmed', origin: 'manual', person_id: 'person-1', confidence: null });
    await saving;
    expect(component.faceTotal()).toBe(1);
    expect(component.selectedFaceId()).toBe('face-1');
    http.expectOne('/api/fotos/curation/summary').flush({ pending: 0, unknown: 0 });
  });

  it('creates a person beside the selected face and selects it for confirmation', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();
    component.environmentId.set('environment-1');
    component.newPersonName.set('  Maria Cardoso  ');
    const saving = component.createPerson();
    const request = http.expectOne('/api/fotos/people');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ environment_id: 'environment-1', name: 'Maria Cardoso' });
    request.flush({ id: 'person-2', name: 'Maria Cardoso', avatar_content_type: null });
    await saving;
    expect(component.chosenPersonId()).toBe('person-2');
    expect(component.peopleTotal()).toBe(1);
    expect(component.people()[0].name).toBe('Maria Cardoso');
    http.expectOne(request => request.url === '/api/fotos/curation/summary').flush({ pending: 0, unknown: 0 });
  });

  it('draws a box in image coordinates even when dragged backwards', () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();
    component.drawing.set(true);
    const element = {
      getBoundingClientRect: () => ({ left: 10, top: 20, width: 200, height: 100 }),
      setPointerCapture: () => undefined,
    } as unknown as HTMLElement;
    const event = (x: number, y: number) => ({
      currentTarget: element, clientX: x, clientY: y,
      pointerId: 1, preventDefault: () => undefined,
    }) as unknown as PointerEvent;
    component.pointerDown(event(170, 100));
    component.pointerMove(event(50, 40));
    component.pointerUp(event(50, 40));
    expect(component.draft()?.x).toBeCloseTo(0.2);
    expect(component.draft()?.y).toBeCloseTo(0.2);
    expect(component.draft()?.width).toBeCloseTo(0.6);
    expect(component.draft()?.height).toBeCloseTo(0.6);
  });

  it('does not load facial curation for video media', async () => {
    const media = {
      id: 'video-1',
      original_name: 'video.mp4',
      media_type: 'video' as const,
      original_date: null,
    };
    const createUrl = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:poster');

    const selecting = component.selectMedia(media);
    const request = http.expectOne('/api/fotos/media/video-1/poster');
    expect(request.request.method).toBe('GET');
    request.flush(new Blob(['poster'], { type: 'image/webp' }));

    const descriptionRequest = http.expectOne('/api/fotos/media/video-1');
    expect(descriptionRequest.request.method).toBe('GET');
    descriptionRequest.flush({ ...media, description: 'Vídeo de teste' });

    let previewRequest;
    for (let attempt = 0; attempt < 20; attempt++) {
      const requests = http.match('/api/fotos/media/video-1/preview');
      if (requests.length) {
        previewRequest = requests[0];
        break;
      }
      await Promise.resolve();
    }
    if (!previewRequest) {
      throw new Error('Requisição de pré-visualização do vídeo não foi iniciada.');
    }
    expect(previewRequest.request.method).toBe('GET');
    previewRequest.flush(new Blob(['video'], { type: 'video/mp4' }));

    await selecting;

    expect(component.faces()).toEqual([]);
    expect(component.faceTotal()).toBe(0);
    expect(component.imageUrl()).toBe('blob:poster');
    expect(component.mediaDescription()).toBe('Vídeo de teste');
    http.expectNone('/api/fotos/curation/media/video-1/faces');
    createUrl.mockRestore();
  });

  it('saves photo rotation and reloads its preview', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    const media = {
      id: 'media-1',
      original_name: 'foto.jpg',
      media_type: 'image' as const,
      original_date: null,
    };

    component.selectedMedia.set(media);
    component.rotationDegrees.set(90);
    component.savedRotationDegrees.set(0);

    const createUrl = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:rotated');

    try {
      const saving = component.saveRotation();

      const request = http.expectOne('/api/fotos/media/media-1/rotation');
      expect(request.request.method).toBe('PATCH');
      expect(request.request.body).toEqual({ rotation_degrees: 90 });
      request.flush({ rotation_degrees: 90 });

      await Promise.resolve();

      http.expectOne('/api/fotos/media/media-1/preview')
        .flush(new Blob(['image'], { type: 'image/webp' }));

      http.expectOne(request =>
        request.url === '/api/fotos/curation/media/media-1/faces',
      ).flush({ items: [], page: 1, total: 0, total_pages: 0 });

      http.expectOne('/api/fotos/media/media-1')
        .flush({ rotation_degrees: 90 });

      await saving;

      expect(component.savedRotationDegrees()).toBe(90);
      expect(component.rotationDegrees()).toBe(90);
      expect(component.rotationChanged()).toBe(false);

      http.expectOne('/api/fotos/curation/summary')
        .flush({ pending: 0, unknown: 0 });
    } finally {
      createUrl.mockRestore();
    }
  });
  it('refreshes an existing unidentified face after analysing again', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();
    const media = { id: 'media-1', original_name: 'maximo.jpg',
      media_type: 'image' as const, original_date: null };
    const unknown = { id: 'face-1', x: 0.1, y: 0.1, width: 0.4, height: 0.4,
      origin: 'detected' as const, status: 'unknown' as const,
      person_id: null, confidence: null };
    component.selectedMedia.set(media);
    component.faces.set([unknown]);
    component.faceTotal.set(1);
    const createUrl = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:preview');

    const analysing = component.detect();
    http.expectOne('/api/fotos/curation/media/media-1/detect').flush([
      { ...unknown, status: 'suggested', person_id: 'person-1', confidence: 0.82 },
    ]);
    await Promise.resolve();
    http.expectOne('/api/fotos/media/media-1/preview').flush(
      new Blob(['image'], { type: 'image/webp' }),
    );
    http.expectOne(request => request.url === '/api/fotos/curation/media/media-1/faces')
      .flush({ items: [{ ...unknown, status: 'suggested', person_id: 'person-1',
        confidence: 0.82 }], page: 1, total: 1, total_pages: 1 });
    http.expectOne('/api/fotos/media/media-1')
      .flush({ rotation_degrees: 0 });
    await analysing;
    expect(component.faces()).toHaveLength(1);
    expect(component.faces()[0].status).toBe('suggested');
    expect(component.faceTotal()).toBe(1);
    expect(component.message()).toContain('atualizado');
    http.expectOne('/api/fotos/curation/summary').flush({ pending: 1, unknown: 0 });
    createUrl.mockRestore();
  });
  it('confirms suggested faces before completing curation', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-test',
      original_name: 'foto.jpg',
      media_type: 'image',
      original_date: null,
    });

    const completing = component.setCurationCompleted(true);

    const facesRequest = http.expectOne(
      '/api/fotos/curation/media/photo-test/faces?page=1&page_size=50',
    );

    facesRequest.flush({
      items: [{
        id: 'face-test',
        status: 'suggested',
        person_id: 'person-test',
      }],
      page: 1,
      total: 1,
      total_pages: 1,
    });

    await Promise.resolve();

    const confirmation = http.expectOne(
      '/api/fotos/curation/faces/face-test/confirm',
    );

    expect(confirmation.request.method).toBe('POST');
    expect(confirmation.request.body).toEqual({
      person_id: 'person-test',
    });

    expect(http.match(
      request => request.url.includes('/completion'),
    )).toHaveLength(0);

    confirmation.flush({
      id: 'face-test',
      status: 'confirmed',
      person_id: 'person-test',
    });

    await Promise.resolve();

    const completion = http.expectOne(
      request => request.url ===
        '/api/fotos/curation/media/photo-test/completion',
    );

    expect(completion.request.method).toBe('POST');
    expect(completion.request.params.get('completed')).toBe('true');

    completion.flush({ curation_completed: true });

    await Promise.resolve();

    http.expectOne(request =>
      request.url === '/api/fotos/curation/media',
    ).flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await completing;

    http.expectOne('/api/fotos/curation/summary')
      .flush({ pending: 0, unknown: 0 });
  });

  it('moves a photograph to the selected album before completing curation', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-album',
      original_name: 'familia.jpg',
      media_type: 'image',
      original_date: null,
    });

    component.originalAlbumId.set('album-old');
    component.destinationAlbumId.set('album-new');

    const completing = component.setCurationCompleted(true);

    http.expectOne(
      '/api/fotos/curation/media/photo-album/faces?page=1&page_size=50',
    ).flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await Promise.resolve();

    const transfer = http.expectOne('/api/fotos/media/bulk');

    expect(transfer.request.method).toBe('PATCH');
    expect(transfer.request.body).toEqual({
      operation: 'set_album',
      media_ids: ['photo-album'],
      album_id: 'album-new',
    });

    expect(http.match(request =>
      request.url.includes('/completion'),
    )).toHaveLength(0);

    transfer.flush({
      operation: 'set_album',
      requested_count: 1,
      succeeded_count: 1,
      failed_count: 0,
      results: [],
    });

    await Promise.resolve();

    expect(component.originalAlbumId()).toBe('album-new');

    const completion = http.expectOne(
      request => request.url ===
        '/api/fotos/curation/media/photo-album/completion',
    );

    expect(completion.request.method).toBe('POST');
    expect(completion.request.params.get('completed')).toBe('true');

    completion.flush({ curation_completed: true });

    await Promise.resolve();

    http.expectOne(request =>
      request.url === '/api/fotos/curation/media',
    ).flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await completing;

    http.expectOne('/api/fotos/curation/summary')
      .flush({ pending: 0, unknown: 0 });
  });
  it('keeps the current album without an unnecessary transfer', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-same-album',
      original_name: 'familia.jpg',
      media_type: 'image',
      original_date: null,
    });

    component.originalAlbumId.set('album-family');
    component.destinationAlbumId.set('album-family');

    const completing = component.setCurationCompleted(true);

    http.expectOne(
      '/api/fotos/curation/media/photo-same-album/faces?page=1&page_size=50',
    ).flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await Promise.resolve();

    expect(http.match('/api/fotos/media/bulk')).toHaveLength(0);

    const completion = http.expectOne(
      request => request.url ===
        '/api/fotos/curation/media/photo-same-album/completion',
    );

    expect(completion.request.method).toBe('POST');
    expect(completion.request.params.get('completed')).toBe('true');

    completion.flush({ curation_completed: true });

    await Promise.resolve();

    http.expectOne(request =>
      request.url === '/api/fotos/curation/media',
    ).flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await completing;

    http.expectOne('/api/fotos/curation/summary')
      .flush({ pending: 0, unknown: 0 });

    expect(http.match('/api/fotos/media/bulk')).toHaveLength(0);
    expect(component.error()).toBeNull();
    expect(component.busy()).toBe(false);
  });
  it('does not complete curation when album transfer fails', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-transfer-failure',
      original_name: 'familia.jpg',
      media_type: 'image',
      original_date: null,
    });

    component.originalAlbumId.set('album-old');
    component.destinationAlbumId.set('album-new');

    const completing = component.setCurationCompleted(true);

    http.expectOne(
      '/api/fotos/curation/media/photo-transfer-failure/faces?page=1&page_size=50',
    ).flush({
      items: [],
      page: 1,
      total: 0,
      total_pages: 0,
    });

    await Promise.resolve();

    const transfer = http.expectOne('/api/fotos/media/bulk');

    expect(transfer.request.method).toBe('PATCH');

    transfer.flush({
      operation: 'set_album',
      requested_count: 1,
      succeeded_count: 0,
      failed_count: 1,
      results: [],
    });

    await completing;

    expect(http.match(request =>
      request.url.includes('/completion'),
    )).toHaveLength(0);

    expect(component.originalAlbumId()).toBe('album-old');
    expect(component.destinationAlbumId()).toBe('album-new');
    expect(component.error()).toContain(
      'Não foi possível atualizar o álbum de destino.',
    );
    expect(component.busy()).toBe(false);
  });
  it('does not complete curation when a face confirmation fails', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-failure',
      original_name: 'foto.jpg',
      media_type: 'image',
      original_date: null,
    });

    const completing = component.setCurationCompleted(true);

    http.expectOne(
      '/api/fotos/curation/media/photo-failure/faces?page=1&page_size=50',
    ).flush({
      items: [{
        id: 'face-failure',
        status: 'suggested',
        person_id: 'person-1',
      }],
      page: 1,
      total: 1,
      total_pages: 1,
    });

    await Promise.resolve();

    http.expectOne(
      '/api/fotos/curation/faces/face-failure/confirm',
    ).flush(
      { detail: 'Falha na confirmação do rosto.' },
      { status: 500, statusText: 'Internal Server Error' },
    );

    await completing;

    expect(http.match(request =>
      request.url.includes('/completion'),
    )).toHaveLength(0);

    expect(component.error()).toBeTruthy();
    expect(component.busy()).toBe(false);
  });

  it('does not delete a photograph when confirmation is cancelled', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-delete',
      original_name: 'familia.jpg',
      media_type: 'image',
      original_date: null,
    });

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);

    try {
      await component.deleteSelectedMedia();

      expect(confirmSpy).toHaveBeenCalledOnce();
      expect(http.match(request =>
        request.method === 'DELETE',
      )).toHaveLength(0);

      expect(component.busy()).toBe(false);
    } finally {
      confirmSpy.mockRestore();
    }
  });

  it('deletes a photograph after confirmation and refreshes curation', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-approved',
      original_name: 'familia.jpg',
      media_type: 'image',
      original_date: null,
    });

    component.media.set([component.selectedMedia()!]);
    component.mediaPage.set(1);

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    try {
      const deleting = component.deleteSelectedMedia();

      const deleteRequest = http.expectOne(
        '/api/fotos/media/photo-approved',
      );

      expect(deleteRequest.request.method).toBe('DELETE');
      expect(confirmSpy).toHaveBeenCalledOnce();

      deleteRequest.flush(null, {
        status: 204,
        statusText: 'No Content',
      });

      await Promise.resolve();

      http.expectOne(request =>
        request.url === '/api/fotos/curation/media',
      ).flush({
        items: [],
        page: 1,
        total: 0,
        total_pages: 0,
      });

      await deleting;

      expect(component.selectedMedia()).toBeNull();
      expect(component.media()).toHaveLength(0);
      expect(component.message()).toContain('excluída');
      expect(component.busy()).toBe(false);

      http.expectOne('/api/fotos/curation/summary')
        .flush({ pending: 0, unknown: 0 });
    } finally {
      confirmSpy.mockRestore();
    }
  });

  it('does not remove facial markings when confirmation is cancelled', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-faces',
      original_name: 'grupo.jpg',
      media_type: 'image',
      original_date: null,
    });

    component.faceTotal.set(2);

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);

    try {
      await component.removeAllFaces();

      expect(confirmSpy).toHaveBeenCalledOnce();
      expect(http.match(request =>
        request.url.includes('/faces'),
      )).toHaveLength(0);

      expect(component.faceTotal()).toBe(2);
      expect(component.busy()).toBe(false);
    } finally {
      confirmSpy.mockRestore();
    }
  });

  it('removes all facial markings after confirmation', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-group',
      original_name: 'grupo.jpg',
      media_type: 'image',
      original_date: null,
    });
    component.faceTotal.set(2);

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    try {
      const removing = component.removeAllFaces();

      http.expectOne(
        '/api/fotos/curation/media/photo-group/faces?page=1&page_size=50',
      ).flush({
        items: [
          { id: 'face-a' },
          { id: 'face-b' },
        ],
        page: 1,
        total: 2,
        total_pages: 1,
      });

      await Promise.resolve();

      const firstDelete = http.expectOne(
        '/api/fotos/curation/faces/face-a',
      );
      expect(firstDelete.request.method).toBe('DELETE');
      firstDelete.flush(null, { status: 204, statusText: 'No Content' });

      await Promise.resolve();

      const secondDelete = http.expectOne(
        '/api/fotos/curation/faces/face-b',
      );
      expect(secondDelete.request.method).toBe('DELETE');
      secondDelete.flush(null, { status: 204, statusText: 'No Content' });

      await removing;

      expect(component.faces()).toHaveLength(0);
      expect(component.faceTotal()).toBe(0);
      expect(component.selectedFaceId()).toBeNull();
      expect(component.message()).toContain('removidas');

      http.expectOne('/api/fotos/curation/summary')
        .flush({ pending: 0, unknown: 0 });
    } finally {
      confirmSpy.mockRestore();
    }
  });

  it('reports partial failure when removing facial markings', async () => {
    fixture.componentRef.setInput('canManage', true);
    fixture.detectChanges();

    component.selectedMedia.set({
      id: 'photo-partial',
      original_name: 'grupo.jpg',
      media_type: 'image',
      original_date: null,
    });

    const faces = [
      { id: 'face-a', x: 0.1, y: 0.1, width: 0.2, height: 0.2,
        origin: 'detected' as const, status: 'unknown' as const,
        person_id: null, confidence: null },
      { id: 'face-b', x: 0.4, y: 0.4, width: 0.2, height: 0.2,
        origin: 'detected' as const, status: 'unknown' as const,
        person_id: null, confidence: null },
    ];

    component.faces.set(faces);
    component.faceTotal.set(2);

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    try {
      const removing = component.removeAllFaces();

      http.expectOne(
        '/api/fotos/curation/media/photo-partial/faces?page=1&page_size=50',
      ).flush({
        items: faces,
        page: 1,
        total: 2,
        total_pages: 1,
      });

      await Promise.resolve();

      http.expectOne('/api/fotos/curation/faces/face-a')
        .flush(null, { status: 204, statusText: 'No Content' });

      await Promise.resolve();

      http.expectOne('/api/fotos/curation/faces/face-b')
        .flush(
          { detail: 'Falha ao excluir marcação.' },
          { status: 500, statusText: 'Internal Server Error' },
        );

      await removing;

      expect(component.message()).toBeNull();
      expect(component.error()).toBeTruthy();
      expect(component.busy()).toBe(false);

      // A primeira marcação foi excluída com sucesso.
      // A segunda deve permanecer disponível na interface.
      expect(component.faces().map(face => face.id)).toEqual(['face-b']);
      expect(component.faceTotal()).toBe(1);

      http.expectOne('/api/fotos/curation/summary')
        .flush({ pending: 0, unknown: 1 });
    } finally {
      confirmSpy.mockRestore();
    }
  });

});

