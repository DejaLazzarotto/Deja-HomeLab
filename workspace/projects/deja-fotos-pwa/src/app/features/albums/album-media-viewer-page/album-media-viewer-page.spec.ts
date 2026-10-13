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
        original_date: '2017-04-01T00:00:00',
        original_name: 'foto-1.jpg',
      },
      {
        id: 'album-media-2',
        media_type: 'image' as const,
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