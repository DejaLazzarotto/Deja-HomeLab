import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';

import { FavoritesPageComponent } from './favorites-page';

describe('FavoritesPageComponent', () => {
  let fixture: ComponentFixture<FavoritesPageComponent>;
  let component: FavoritesPageComponent;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FavoritesPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: Router,
          useValue: {
            navigate: vi.fn().mockResolvedValue(true),
            navigateByUrl: vi.fn().mockResolvedValue(true),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      FavoritesPageComponent,
    );
    component = fixture.componentInstance;

    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    vi.restoreAllMocks();
  });

  it('should load favorites in pages of 30', async () => {
    const createItem = (index: number) => ({
      id: `favorite-${index}`,
      media_type: index === 1 ? 'video' as const : 'image' as const,
      original_date: '2026-10-13T10:00:00',
      original_name: `media-${index}`,
    });

    const firstPage = Array.from(
      { length: 30 },
      (_, index) => createItem(index + 1),
    );

    const secondPage = [createItem(31)];

    fixture.detectChanges();

    const request1 = http.expectOne(
      (request) =>
        request.url === '/api/fotos/favorites' &&
        request.params.get('page') === '1' &&
        request.params.get('page_size') === '30',
    );

    request1.flush({
      items: firstPage,
      page: 1,
      page_size: 30,
      total: 31,
      total_pages: 2,
    });

    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    for (const item of firstPage) {
      const derivative = item.media_type === 'video'
        ? 'poster'
        : 'thumbnail';

      http.expectOne(
        `/api/fotos/media/${item.id}/${derivative}`,
      ).flush(new Blob(['preview']));
    }

    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    expect(component.loading()).toBe(false);

    expect(component.media().length).toBe(30);
    expect(component.hasMore()).toBe(true);

    const nextPromise = component.loadNextPage();

    const request2 = http.expectOne(
      (request) =>
        request.url === '/api/fotos/favorites' &&
        request.params.get('page') === '2' &&
        request.params.get('page_size') === '30',
    );

    request2.flush({
      items: secondPage,
      page: 2,
      page_size: 30,
      total: 31,
      total_pages: 2,
    });

    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    http.expectOne(
      '/api/fotos/media/favorite-31/thumbnail',
    ).flush(new Blob(['preview']));

    await nextPromise;

    expect(component.media().length).toBe(31);
    expect(component.hasMore()).toBe(false);
  });
  it('should refresh favorites when the gallery is reopened', async () => {
    const firstItem = {
      id: 'favorite-photo-1',
      media_type: 'image' as const,
      original_date: '2026-10-13T10:00:00',
      original_name: 'photo-1.jpg',
    };

    const secondItem = {
      id: 'favorite-photo-2',
      media_type: 'image' as const,
      original_date: '2026-10-13T11:00:00',
      original_name: 'photo-2.jpg',
    };

    const flushGallery = async (
      items: readonly typeof firstItem[],
    ) => {
      const pageRequest = http.expectOne(
        (request) =>
          request.url === '/api/fotos/favorites' &&
          request.params.get('page') === '1' &&
          request.params.get('page_size') === '30',
      );

      pageRequest.flush({
        items,
        page: 1,
        page_size: 30,
        total: items.length,
        total_pages: items.length > 0 ? 1 : 0,
      });

      await new Promise<void>((resolve) => setTimeout(resolve, 0));

      for (const item of items) {
        http.expectOne(
          `/api/fotos/media/${item.id}/thumbnail`,
        ).flush(new Blob(['preview']));
      }

      await new Promise<void>((resolve) => setTimeout(resolve, 0));
    };

    fixture.detectChanges();

    await flushGallery([firstItem, secondItem]);

    expect(component.loading()).toBe(false);
    expect(component.media().map((item) => item.id)).toEqual([
      'favorite-photo-1',
      'favorite-photo-2',
    ]);

    fixture.destroy();

    // Uma nova instância representa o retorno à galeria.
    const reopenedFixture = TestBed.createComponent(
      FavoritesPageComponent,
    );

    const reopenedComponent = reopenedFixture.componentInstance;

    reopenedFixture.detectChanges();

    await flushGallery([secondItem]);

    expect(reopenedComponent.loading()).toBe(false);
    expect(reopenedComponent.media().map((item) => item.id)).toEqual([
      'favorite-photo-2',
    ]);

    reopenedFixture.destroy();
  });

});
