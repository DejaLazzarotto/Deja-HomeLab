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

import { FavoriteMediaViewerPageComponent } from './favorite-media-viewer-page';

describe('FavoriteMediaViewerPageComponent', () => {
  let fixture: ComponentFixture<FavoriteMediaViewerPageComponent>;
  let component: FavoriteMediaViewerPageComponent;
  let httpTestingController: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FavoriteMediaViewerPageComponent],
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

    fixture = TestBed.createComponent(FavoriteMediaViewerPageComponent);
    component = fixture.componentInstance;

    httpTestingController = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should add and remove favorites without duplicate requests', async () => {
    const mediaId = 'recent-media-1';
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
  it('should update favorite state when navigating between favorite media', async () => {
    const items = [
      {
        id: 'favorite-photo-1',
        media_type: 'image' as const,
        original_date: '2026-10-12T10:00:00',
        original_name: 'foto.jpg',
      },
      {
        id: 'favorite-video-2',
        media_type: 'video' as const,
        original_date: '2026-10-12T11:00:00',
        original_name: 'video.mp4',
      },
    ];

    component.mediaId.set(items[0].id);
    component.monthMedia.set(items);
    component.currentIndex.set(0);
    component.total.set(2);

    // A listagem já está completa neste cenário.
    Object.assign(component, {
      currentPage: 1,
      totalPages: 1,
    });

    const firstLoad = component['loadCurrentMedia']();

    httpTestingController.expectOne(
      '/api/fotos/media/favorite-photo-1',
    ).flush(items[0]);

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/favorites/favorite-photo-1',
    ).flush({
      media_id: 'favorite-photo-1',
      is_favorite: true,
    });

    httpTestingController.expectOne(
      '/api/fotos/media/favorite-photo-1/preview',
    ).flush(new Blob(['image'], { type: 'image/jpeg' }));

    await firstLoad;

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.isFavorite()).toBe(true);

    const nextPromise = component.showNext();

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/media/favorite-video-2',
    ).flush(items[1]);

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    httpTestingController.expectOne(
      '/api/fotos/favorites/favorite-video-2',
    ).flush({
      media_id: 'favorite-video-2',
      is_favorite: false,
    });

    httpTestingController.expectOne(
      '/api/fotos/media/favorite-video-2/preview',
    ).flush(new Blob(['video'], { type: 'video/mp4' }));

    await nextPromise;

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.currentIndex()).toBe(1);
    expect(component.mediaId()).toBe('favorite-video-2');
    expect(component.isFavorite()).toBe(false);
  });

});
