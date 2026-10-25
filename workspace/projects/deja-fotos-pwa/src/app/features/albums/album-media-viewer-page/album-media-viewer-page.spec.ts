import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { ActivatedRoute, Router } from '@angular/router';

import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
} from 'vitest';

import { MusicPlayerService } from '../../../core/music/music-player.service';
import { vi } from 'vitest';
import { AlbumMediaViewerPageComponent } from './album-media-viewer-page';

describe('AlbumMediaViewerPageComponent', () => {
  let fixture: ComponentFixture<AlbumMediaViewerPageComponent>;
  let component: AlbumMediaViewerPageComponent;
  let httpTestingController: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlbumMediaViewerPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: () => null,
              },
            },
          },
        },
        {
          provide: Router,
          useValue: {
            navigate: () => Promise.resolve(true),
            navigateByUrl: () => Promise.resolve(true),
            getCurrentNavigation: () => null,
            parseUrl: (url: string) => ({ toString: () => url }),
            url: '/albums',
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      AlbumMediaViewerPageComponent,
    );

    component = fixture.componentInstance;

    httpTestingController = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('pausa a música quando o vídeo inicia e solicita retomada ao parar', () => {
    const music = TestBed.inject(MusicPlayerService);

    const pauseForVideo = vi.spyOn(music, 'pauseForVideo')
      .mockImplementation(() => undefined);

    const resumeFromVideo = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);
    component.loading.set(false);

    component.onVideoPlay();
    expect(pauseForVideo).toHaveBeenCalledOnce();

    component.onVideoStop();
    expect(resumeFromVideo).toHaveBeenCalledOnce();
  });
  it('não retoma a música durante a transição entre vídeos', async () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    const videos = [
      {
        id: 'video-1',
        media_type: 'video' as const,
        is_animated: false,
        original_date: '2026-10-01T00:00:00',
        original_name: 'video-1.mp4',
      },
      {
        id: 'video-2',
        media_type: 'video' as const,
        is_animated: false,
        original_date: '2026-10-02T00:00:00',
        original_name: 'video-2.mp4',
      },
    ];

    component.monthMedia.set(videos);
    component.currentIndex.set(0);
    component.mediaId.set(videos[0].id);
    component.loading.set(false);

    const change = component['changeMedia'](1);

    expect(resume).not.toHaveBeenCalled();

    httpTestingController.expectOne(
      '/api/fotos/media/video-2',
    ).flush(videos[1]);

    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    httpTestingController.expectOne(
      '/api/fotos/favorites/video-2',
    ).flush({ media_id: 'video-2', is_favorite: false });

    httpTestingController.expectOne(
      '/api/fotos/media/video-2/preview',
    ).flush(new Blob(['video'], { type: 'video/mp4' }));

    await change;

    expect(resume).not.toHaveBeenCalled();
  });
  it('ignora a pausa do vídeo anterior durante o carregamento', () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    component.loading.set(true);
    component.onVideoStop();

    expect(resume).not.toHaveBeenCalled();

    component.loading.set(false);
    component.onVideoStop();

    expect(resume).toHaveBeenCalledOnce();
  });
  it('solicita retomada musical ao trocar vídeo por fotografia', async () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    const photo = {
      id: 'foto-apos-video',
      media_type: 'image' as const,
      is_animated: false,
      original_date: '2026-10-02T00:00:00',
      original_name: 'foto.jpg',
    };

    component.monthMedia.set([photo]);
    component.loading.set(false);

    const change = component['changeMedia'](0);

    expect(resume).toHaveBeenCalledOnce();

    httpTestingController.expectOne(
      '/api/fotos/media/foto-apos-video',
    ).flush(photo);

    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    httpTestingController.expectOne(
      '/api/fotos/favorites/foto-apos-video',
    ).flush({ media_id: photo.id, is_favorite: false });

    httpTestingController.expectOne(
      '/api/fotos/media/foto-apos-video/preview',
    ).flush(new Blob(['foto'], { type: 'image/jpeg' }));

    await change;
  });
  it('ignora eventos de pausa de vídeos removidos da página', () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    component.loading.set(false);

    const video = document.createElement('video');
    const event = new Event('pause');

    Object.defineProperty(event, 'target', {
      value: video,
    });

    component.onVideoStop(event);

    expect(resume).not.toHaveBeenCalled();
  });
  it('ignora eventos de vídeos conectados que não são a mídia ativa', () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    component.loading.set(false);

    const antigo = document.createElement('video');
    antigo.className = 'viewer-video';

    document.body.appendChild(antigo);

    try {
      antigo.dispatchEvent(new Event('pause'));

      expect(antigo.isConnected).toBe(true);
      expect(resume).not.toHaveBeenCalled();
    } finally {
      antigo.remove();
    }
  });
  it('ignora Play de vídeos antigos que não são a mídia ativa', () => {
    const music = TestBed.inject(MusicPlayerService);
    const pause = vi.spyOn(music, 'pauseForVideo')
      .mockImplementation(() => undefined);

    component.loading.set(false);

    const antigo = document.createElement('video');
    antigo.className = 'viewer-video';
    document.body.appendChild(antigo);

    try {
      antigo.addEventListener('play', (event) => {
        component.onVideoPlay(event);
      });

      antigo.dispatchEvent(new Event('play'));

      expect(antigo.isConnected).toBe(true);
      expect(pause).not.toHaveBeenCalled();
    } finally {
      antigo.remove();
    }
  });
  it('solicita retomada musical ao encerrar o visualizador', () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    component.albumId.set('album-1');
    vi.spyOn(TestBed.inject(Router), 'getCurrentNavigation').mockReturnValue({ finalUrl: { toString: () => '/albums/album-1/2026/10' } } as ReturnType<Router['getCurrentNavigation']>);

    component.ngOnDestroy();

    expect(resume).toHaveBeenCalledOnce();
  });
  it('não retoma música ao sair completamente do álbum', () => {
    const music = TestBed.inject(MusicPlayerService);
    const resume = vi.spyOn(music, 'resumeFromVideo')
      .mockImplementation(() => undefined);

    component.albumId.set('album-1');

    vi.spyOn(TestBed.inject(Router), 'getCurrentNavigation')
      .mockReturnValue({
        finalUrl: { toString: () => '/explore' },
      } as ReturnType<Router['getCurrentNavigation']>);

    component.ngOnDestroy();

    expect(resume).not.toHaveBeenCalled();
  });
  it('should load the original animated image in albums', async () => {
    const animatedMedia = {
      id: 'album-animation-1',
      media_type: 'image' as const,
      is_animated: true,
      original_date: '2017-04-01T00:00:00',
      original_name: 'animacao.webp',
    };

    component.albumId.set('album-1');
    component.year.set(2017);
    component.month.set(4);
    component.mediaId.set(animatedMedia.id);
    component.monthMedia.set([animatedMedia]);
    component.currentIndex.set(0);
    component.total.set(1);

    const loadPromise = component['loadCurrentMedia']();

    httpTestingController.expectOne(
      '/api/fotos/media/album-animation-1',
    ).flush(animatedMedia);

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/favorites/album-animation-1',
    ).flush({
      media_id: animatedMedia.id,
      is_favorite: false,
    });

    const originalRequest = httpTestingController.expectOne(
      '/api/fotos/media/album-animation-1/original',
    );

    expect(originalRequest.request.responseType).toBe('blob');

    expect(
      httpTestingController.match(
        '/api/fotos/media/album-animation-1/preview',
      ),
    ).toHaveLength(0);

    originalRequest.flush(
      new Blob(['animated-webp'], { type: 'image/webp' }),
    );

    await loadPromise;

    expect(component.mediaUrl()).toBeTruthy();
    expect(component.media()?.is_animated).toBe(true);
    expect(component.isFavorite()).toBe(false);
  });
  it('should add and remove favorites without duplicate requests', async () => {
    const mediaId = 'media-album-1';
    const favoriteUrl = `/api/fotos/favorites/${mediaId}`;

    component.mediaId.set(mediaId);

    const addPromise = component.toggleFavorite();

    expect(component.favoriteSaving()).toBe(true);

    const duplicateClick = component.toggleFavorite();

    const putRequests = httpTestingController.match(
      (request) =>
        request.method === 'PUT' &&
        request.url === favoriteUrl,
    );

    expect(putRequests.length).toBe(1);

    putRequests[0].flush({
      media_id: mediaId,
      is_favorite: true,
    });

    await Promise.all([addPromise, duplicateClick]);

    expect(component.isFavorite()).toBe(true);
    expect(component.favoriteSaving()).toBe(false);

    const removePromise = component.toggleFavorite();

    const deleteRequest = httpTestingController.expectOne(
      (request) =>
        request.method === 'DELETE' &&
        request.url === favoriteUrl,
    );

    deleteRequest.flush(null);

    await removePromise;

    expect(component.isFavorite()).toBe(false);
    expect(component.favoriteSaving()).toBe(false);
  });

  it('should update favorite state when navigating between album media', async () => {
    const items = [
      {
        id: 'album-media-1',
        media_type: 'image' as const,
        is_animated: false,
        original_date: '2017-04-01T00:00:00',
        original_name: 'foto-1.jpg',
      },
      {
        id: 'album-media-2',
        media_type: 'image' as const,
        is_animated: false,
        original_date: '2017-04-02T00:00:00',
        original_name: 'foto-2.jpg',
      },
    ];

    component.albumId.set('album-1');
    component.year.set(2017);
    component.month.set(4);
    component.mediaId.set(items[0].id);
    component.monthMedia.set(items);
    component.currentIndex.set(0);
    component.total.set(2);

    const firstLoad = component['loadCurrentMedia']();

    httpTestingController.expectOne(
      '/api/fotos/media/album-media-1',
    ).flush(items[0]);

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/favorites/album-media-1',
    ).flush({
      media_id: 'album-media-1',
      is_favorite: true,
    });

    httpTestingController.expectOne(
      '/api/fotos/media/album-media-1/preview',
    ).flush(new Blob(['image']));

    await firstLoad;

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.isFavorite()).toBe(true);

    // Todas as mídias do álbum já estão carregadas neste cenário.
    // Evita uma busca adicional por páginas antes da navegação.
    Object.assign(component, {
      currentPage: 1,
      totalPages: 1,
    });

    const nextPromise = component.showNext();

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/media/album-media-2',
    ).flush(items[1]);

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/favorites/album-media-2',
    ).flush({
      media_id: 'album-media-2',
      is_favorite: false,
    });

    httpTestingController.expectOne(
      '/api/fotos/media/album-media-2/preview',
    ).flush(new Blob(['image']));

    await nextPromise;

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.currentIndex()).toBe(1);
    expect(component.mediaId()).toBe('album-media-2');
    expect(component.isFavorite()).toBe(false);
  });
});
