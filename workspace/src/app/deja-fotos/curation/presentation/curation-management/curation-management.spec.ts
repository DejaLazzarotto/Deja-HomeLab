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
      'não são usados como referência automática',
    );
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
    await analysing;
    expect(component.faces()).toHaveLength(1);
    expect(component.faces()[0].status).toBe('suggested');
    expect(component.faceTotal()).toBe(1);
    expect(component.message()).toContain('atualizado');
    http.expectOne('/api/fotos/curation/summary').flush({ pending: 1, unknown: 0 });
    createUrl.mockRestore();
  });
});
