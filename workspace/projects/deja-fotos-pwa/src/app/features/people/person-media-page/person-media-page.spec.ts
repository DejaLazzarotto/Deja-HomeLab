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

import { PersonMediaPageComponent } from './person-media-page';

describe('PersonMediaPageComponent', () => {
  let fixture: ComponentFixture<PersonMediaPageComponent>;
  let component: PersonMediaPageComponent;
  let httpTestingController: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        PersonMediaPageComponent,
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
      PersonMediaPageComponent,
    );

    component = fixture.componentInstance;

    httpTestingController = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should load the first 30 media items and append the next page', async () => {
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

    const personRequest =
      httpTestingController.expectOne(
        '/api/fotos/people/person-1',
      );

    personRequest.flush({
      id: 'person-1',
      name: 'Carol',
      description: null,
      active: true,
      avatar_content_type: null,
    });

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

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

    const firstPageThumbnailRequests =
      httpTestingController.match(
        (request) =>
          request.url.endsWith('/thumbnail'),
      );

    expect(
      firstPageThumbnailRequests.length,
    ).toBe(30);

    for (const request of firstPageThumbnailRequests) {
      request.flush(
        new Blob(['image']),
      );
    }

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.media().length).toBe(30);
    expect(component.total()).toBe(40);
    expect(component.hasMore()).toBe(true);

    const nextPagePromise =
      component.loadNextPage();

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

    const secondPageThumbnailRequests =
      httpTestingController.match(
        (request) =>
          request.url.endsWith('/thumbnail'),
      );

    expect(
      secondPageThumbnailRequests.length,
    ).toBe(10);

    for (const request of secondPageThumbnailRequests) {
      request.flush(
        new Blob(['image']),
      );
    }

    await nextPagePromise;

    expect(component.media().length).toBe(40);
    expect(component.total()).toBe(40);

    expect(
      component.media()[0]?.id,
    ).toBe('media-1');

    expect(
      component.media()[39]?.id,
    ).toBe('media-40');

    expect(component.hasMore()).toBe(false);
  });
});