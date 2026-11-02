import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { Router } from '@angular/router';

import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
} from 'vitest';

import { PeoplePageComponent } from './people-page';

describe('PeoplePageComponent', () => {
  let fixture: ComponentFixture<PeoplePageComponent>;
  let component: PeoplePageComponent;
  let httpTestingController: HttpTestingController;

  const person = (id: string, name: string) => ({
    id,
    name,
    description: null,
    active: true,
    avatar_content_type: null,
  });

  const flushPeople = (
    page: number,
    items: ReturnType<typeof person>[],
    totalPages: number,
  ) => {
    const request = httpTestingController.expectOne(
      (req) =>
        req.url === '/api/fotos/people' &&
        req.params.get('active') === 'true' &&
        req.params.get('page') === String(page) &&
        req.params.get('page_size') === '30',
    );

    request.flush({
      items,
      page,
      page_size: 30,
      total: totalPages === 1 ? items.length : 96,
      total_pages: totalPages,
    });
  };

  const flushMedia = async (
    people: ReturnType<typeof person>[],
    counts: number[],
  ) => {
    await new Promise<void>((resolve) =>
      setTimeout(resolve, 0),
    );

    people.forEach((item, index) => {
      const request = httpTestingController.expectOne(
        (req) =>
          req.url ===
            `/api/fotos/people/${item.id}/media` &&
          req.params.get('page') === '1' &&
          req.params.get('page_size') === '1',
      );

      request.flush({
        items: [],
        page: 1,
        page_size: 1,
        total: counts[index],
        total_pages: counts[index],
      });
    });

    await new Promise<void>((resolve) =>
      setTimeout(resolve, 0),
    );
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PeoplePageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
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
      PeoplePageComponent,
    );

    component = fixture.componentInstance;

    httpTestingController = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    fixture.destroy();
    httpTestingController.verify();
  });

  it('should load people with their media counts', async () => {
    fixture.detectChanges();

    const people = [
      person('person-1', 'Branco'),
      person('person-2', 'Carol'),
    ];

    flushPeople(1, people, 1);
    await flushMedia(people, [2, 11]);

    expect(component.loading()).toBe(false);
    expect(component.error()).toBeNull();
    expect(component.people().length).toBe(2);
    expect(component.people()[0]?.name).toBe('Branco');
    expect(component.people()[0]?.mediaCount).toBe(2);
    expect(component.people()[1]?.name).toBe('Carol');
    expect(component.people()[1]?.mediaCount).toBe(11);
    expect(component.hasMore()).toBe(false);
  });

  it('should append the next page without losing existing people', async () => {
    fixture.detectChanges();

    const first = [person('person-1', 'Ana')];

    flushPeople(1, first, 2);
    await flushMedia(first, [3]);

    expect(component.people().length).toBe(1);
    expect(component.hasMore()).toBe(true);

    const nextPage = component.loadNextPage();

    const second = [person('person-2', 'Beatriz')];

    flushPeople(2, second, 2);
    await flushMedia(second, [7]);
    await nextPage;

    expect(component.people().map((item) => item.name))
      .toEqual(['Ana', 'Beatriz']);

    expect(component.people()[1]?.mediaCount).toBe(7);
    expect(component.hasMore()).toBe(false);

    await component.loadNextPage();

    httpTestingController.expectNone(
      (req) => req.url === '/api/fotos/people',
    );
  });

  it('should allow retry after a failed additional page', async () => {
    fixture.detectChanges();

    const first = [person('person-1', 'Ana')];

    flushPeople(1, first, 2);
    await flushMedia(first, [3]);

    const failedPage = component.loadNextPage();

    const request = httpTestingController.expectOne(
      (req) =>
        req.url === '/api/fotos/people' &&
        req.params.get('page') === '2',
    );

    request.flush(
      { detail: 'Gateway Timeout' },
      {
        status: 504,
        statusText: 'Gateway Timeout',
      },
    );

    await failedPage;

    expect(component.people().length).toBe(1);
    expect(component.loadMoreError()).not.toBeNull();
    expect(component.hasMore()).toBe(true);

    const retry = component.loadNextPage();

    const second = [person('person-2', 'Beatriz')];

    flushPeople(2, second, 2);
    await flushMedia(second, [5]);
    await retry;

    expect(component.people().length).toBe(2);
    expect(component.loadMoreError()).toBeNull();
    expect(component.hasMore()).toBe(false);
  });

  it('should allow retry after initial loading failure', async () => {
    fixture.detectChanges();

    const request = httpTestingController.expectOne(
      (req) =>
        req.url === '/api/fotos/people' &&
        req.params.get('page') === '1',
    );

    request.flush(
      { detail: 'Gateway Timeout' },
      {
        status: 504,
        statusText: 'Gateway Timeout',
      },
    );

    await new Promise<void>((resolve) =>
      setTimeout(resolve, 0),
    );

    expect(component.error()).not.toBeNull();
    expect(component.loading()).toBe(false);

    const retry = component.loadNextPage();
    const people = [person('person-1', 'Ana')];

    flushPeople(1, people, 1);
    await flushMedia(people, [4]);
    await retry;

    expect(component.error()).toBeNull();
    expect(component.people().length).toBe(1);
    expect(component.people()[0]?.mediaCount).toBe(4);
  });
});
