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

import {
  PersonMediaViewerPageComponent,
} from './person-media-viewer-page';

describe('PersonMediaViewerPageComponent', () => {
  let fixture: ComponentFixture<PersonMediaViewerPageComponent>;
  let component: PersonMediaViewerPageComponent;
  let httpTestingController: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        PersonMediaViewerPageComponent,
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => {
                  if (key === 'personId') {
                    return 'person-1';
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
      PersonMediaViewerPageComponent,
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
          request.url ===
            '/api/fotos/people/person-1/media' &&
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

    httpTestingController.expectOne(
      '/api/fotos/favorites/media-30',
    ).flush({
      media_id: 'media-30',
      is_favorite: true,
    });

    const previewThirtyRequest =
      httpTestingController.expectOne(
        '/api/fotos/media/media-30/preview',
      );

    previewThirtyRequest.flush(
      new Blob(['image']),
    );

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.currentIndex()).toBe(29);
    expect(component.personMedia().length).toBe(30);
    expect(component.total()).toBe(40);

    const nextPromise =
      component.showNext();

    const secondPageRequest =
      httpTestingController.expectOne(
        (request) =>
          request.url ===
            '/api/fotos/people/person-1/media' &&
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

    httpTestingController.expectOne(
      '/api/fotos/favorites/media-31',
    ).flush({
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
    expect(component.personMedia().length).toBe(40);
    expect(component.total()).toBe(40);
  });

  it('should add and remove favorites without duplicate requests', async () => {
    const mediaId = 'person-media-1';
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
});