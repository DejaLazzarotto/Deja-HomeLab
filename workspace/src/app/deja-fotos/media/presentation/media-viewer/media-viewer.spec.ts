import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { Media } from '../../domain';
import { MediaViewerComponent } from './media-viewer';

describe('MediaViewerComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MediaViewerComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('loads an authenticated MP4 preview and releases it on close', async () => {
    const http = TestBed.inject(HttpTestingController);
    const createUrl = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:video');
    const revokeUrl = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    const fixture = TestBed.createComponent(MediaViewerComponent);
    fixture.componentRef.setInput('media', {
      id: 'video-1', originalName: 'festa.mov', mediaType: 'video',
    } as Media);
    fixture.detectChanges();

    const request = http.expectOne('/api/fotos/media/video-1/preview');
    expect(request.request.method).toBe('GET');
    request.flush(new Blob(['mp4'], { type: 'video/mp4' }));
    await Promise.resolve();
    await fixture.whenStable();
    fixture.detectChanges();
    expect(fixture.componentInstance.error()).toBeNull();
    expect(fixture.componentInstance.url()).toBe('blob:video');
    const video = (fixture.nativeElement as HTMLElement).querySelector('video');
    expect(video?.getAttribute('src')).toBe('blob:video');
    expect(video?.controls).toBe(true);

    fixture.destroy();
    expect(revokeUrl).toHaveBeenCalledWith('blob:video');
    http.verify();
    createUrl.mockRestore();
    revokeUrl.mockRestore();
  });

  it('loads a photo preview and shows a useful error if it is missing', async () => {
    const http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(MediaViewerComponent);
    fixture.componentRef.setInput('media', {
      id: 'photo-1', originalName: 'foto.jpg', mediaType: 'image',
    } as Media);
    fixture.detectChanges();
    http.expectOne('/api/fotos/media/photo-1/preview').flush(new Blob(['missing']), {
      status: 404, statusText: 'Not Found',
    });
    await fixture.whenStable();
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('[role="alert"]')?.textContent)
      .toContain('Não foi possível abrir');
    fixture.destroy();
    http.verify();
  });
});
