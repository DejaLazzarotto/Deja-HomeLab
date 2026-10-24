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
  vi,
} from 'vitest';

import { MediaViewerPageComponent } from './media-viewer-page';

describe('MediaViewerPageComponent', () => {
  let fixture: ComponentFixture<MediaViewerPageComponent>;
  let component: MediaViewerPageComponent;
  let httpTestingController: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MediaViewerPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => {
                  if (key === 'year') {
                    return '2017';
                  }

                  if (key === 'month') {
                    return '4';
                  }

                  if (key === 'mediaId') {
                    return 'media-30';
                  }

                  return null;
                },
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
      MediaViewerPageComponent,
    );

    component = fixture.componentInstance;

    httpTestingController = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should load the next page before moving from media 30 to media 31', async () => {
    const firstPageItems = Array.from(
      { length: 30 },
      (_, index) => ({
        id: `media-${index + 1}`,
        media_type: 'image' as const,
        original_date: '2017-04-01T00:00:00',
        original_name: `foto-${index + 1}.jpg`,
      }),
    );

    const secondPageItems = Array.from(
      { length: 10 },
      (_, index) => ({
        id: `media-${index + 31}`,
        media_type: 'image' as const,
        original_date: '2017-04-01T00:00:00',
        original_name: `foto-${index + 31}.jpg`,
      }),
    );

    fixture.detectChanges();

    const firstPageRequest =
      httpTestingController.expectOne(
        (request) =>
          request.url === '/api/fotos/media' &&
          request.params.get('original_year') === '2017' &&
          request.params.get('original_month') === '4' &&
          request.params.get('page') === '1' &&
          request.params.get('page_size') === '30',
      );

    firstPageRequest.flush({
      items: firstPageItems,
      page: 1,
      page_size: 30,
      total: 40,
      total_pages: 2,
    });

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const mediaThirtyRequest =
      httpTestingController.expectOne(
        '/api/fotos/media/media-30',
      );

    mediaThirtyRequest.flush(
      firstPageItems[29],
    );

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const favoriteThirtyRequest =
      httpTestingController.expectOne(
        '/api/fotos/favorites/media-30',
      );

    favoriteThirtyRequest.flush({
      media_id: 'media-30',
      is_favorite: true,
    });
    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });
    const previewThirtyRequest =
      httpTestingController.expectOne(
        '/api/fotos/media/media-30/preview',
      );

    previewThirtyRequest.flush(
      new Blob(['image']),
    );

    await fixture.whenStable();

    expect(component.currentIndex()).toBe(29);
    expect(component.isFavorite()).toBe(true);
    expect(component.monthMedia().length).toBe(30);
    expect(component.total()).toBe(40);

    const nextPromise = component.showNext();

    const secondPageRequest =
      httpTestingController.expectOne(
        (request) =>
          request.url === '/api/fotos/media' &&
          request.params.get('original_year') === '2017' &&
          request.params.get('original_month') === '4' &&
          request.params.get('page') === '2' &&
          request.params.get('page_size') === '30',
      );

    secondPageRequest.flush({
      items: secondPageItems,
      page: 2,
      page_size: 30,
      total: 40,
      total_pages: 2,
    });

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const mediaThirtyOneRequest =
      httpTestingController.expectOne(
        '/api/fotos/media/media-31',
      );

    mediaThirtyOneRequest.flush(
      secondPageItems[0],
    );

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const favoriteThirtyOneRequest =
      httpTestingController.expectOne(
        '/api/fotos/favorites/media-31',
      );

    favoriteThirtyOneRequest.flush({
      media_id: 'media-31',
      is_favorite: false,
    });
    const previewThirtyOneRequest =
      httpTestingController.expectOne(
        '/api/fotos/media/media-31/preview',
      );

    previewThirtyOneRequest.flush(
      new Blob(['image']),
    );

    await nextPromise;

    expect(component.currentIndex()).toBe(30);
    expect(component.mediaId()).toBe('media-31');
    expect(component.isFavorite()).toBe(false);
    expect(component.monthMedia().length).toBe(40);
    expect(component.total()).toBe(40);
  });

  it('should request the original file for animated images', async () => {
    fixture.detectChanges();

    const listRequest = httpTestingController.expectOne(
      (request) =>
        request.url === '/api/fotos/media' &&
        request.params.get('original_year') === '2017' &&
        request.params.get('original_month') === '4',
    );

    const animatedMedia = {
      id: 'media-30',
      media_type: 'image' as const,
      is_animated: true,
      original_date: '2017-04-01T00:00:00',
      original_name: 'animacao.webp',
    };

    listRequest.flush({
      items: [animatedMedia],
      page: 1,
      page_size: 30,
      total: 1,
      total_pages: 1,
    });

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const mediaRequest = httpTestingController.expectOne(
      '/api/fotos/media/media-30',
    );

    mediaRequest.flush(animatedMedia);

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const favoriteRequest = httpTestingController.expectOne(
      '/api/fotos/favorites/media-30',
    );

    favoriteRequest.flush({
      media_id: 'media-30',
      is_favorite: false,
    });

    const originalRequest = httpTestingController.expectOne(
      '/api/fotos/media/media-30/original',
    );

    expect(originalRequest.request.responseType).toBe('blob');

    expect(
      httpTestingController.match(
        '/api/fotos/media/media-30/preview',
      ),
    ).toHaveLength(0);

    originalRequest.flush(
      new Blob(['animated-webp'], { type: 'image/webp' }),
    );

    await fixture.whenStable();

    expect(component.mediaUrl()).toBeTruthy();
    expect(component.media()?.is_animated).toBe(true);
  });
  it('should add and remove a favorite without duplicate requests', async () => {
    const mediaId = 'media-30';
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

  it('should navigate using a single-finger swipe', async () => {
    const next = vi.spyOn(component, 'showNext')
      .mockResolvedValue(undefined);

    component.onTouchStart({
      touches: [{ clientX: 200, clientY: 100 }],
      changedTouches: [{ clientX: 200, clientY: 100 }],
    } as unknown as TouchEvent);

    await component.onTouchEnd({
      changedTouches: [{ clientX: 100, clientY: 100 }],
    } as unknown as TouchEvent);

    expect(next).toHaveBeenCalledOnce();
  });

  it('should ignore a multi-touch gesture during swipe navigation', async () => {
    const next = vi.spyOn(component, 'showNext')
      .mockResolvedValue(undefined);

    const previous = vi.spyOn(component, 'showPrevious')
      .mockResolvedValue(undefined);

    component.onTouchStart({
      touches: [{ clientX: 200, clientY: 100 }],
      changedTouches: [{ clientX: 200, clientY: 100 }],
    } as unknown as TouchEvent);

    component.onTouchStart({
      touches: [
        { clientX: 180, clientY: 100 },
        { clientX: 220, clientY: 100 },
      ],
      changedTouches: [{ clientX: 180, clientY: 100 }],
    } as unknown as TouchEvent);

    await component.onTouchEnd({
      changedTouches: [{ clientX: 50, clientY: 100 }],
    } as unknown as TouchEvent);

    expect(next).not.toHaveBeenCalled();
    expect(previous).not.toHaveBeenCalled();
  });
});