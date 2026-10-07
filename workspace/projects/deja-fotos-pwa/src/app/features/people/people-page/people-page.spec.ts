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

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        PeoplePageComponent,
      ],
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
    httpTestingController.verify();
  });

  it('should load people with their media counts', async () => {
    fixture.detectChanges();

    const peopleRequest =
      httpTestingController.expectOne(
        (request) =>
          request.url === '/api/fotos/people' &&
          request.params.get('active') === 'true' &&
          request.params.get('page') === '1' &&
          request.params.get('page_size') === '30',
      );

    peopleRequest.flush({
      items: [
        {
          id: 'person-1',
          name: 'Branco',
          description: null,
          active: true,
          avatar_content_type: null,
        },
        {
          id: 'person-2',
          name: 'Carol',
          description: null,
          active: true,
          avatar_content_type: null,
        },
      ],
      page: 1,
      page_size: 30,
      total: 2,
      total_pages: 1,
    });

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    const firstMediaRequest =
      httpTestingController.expectOne(
        (request) =>
          request.url ===
            '/api/fotos/people/person-1/media' &&
          request.params.get('page') === '1' &&
          request.params.get('page_size') === '1',
      );

    const secondMediaRequest =
      httpTestingController.expectOne(
        (request) =>
          request.url ===
            '/api/fotos/people/person-2/media' &&
          request.params.get('page') === '1' &&
          request.params.get('page_size') === '1',
      );

    firstMediaRequest.flush({
      items: [],
      page: 1,
      page_size: 1,
      total: 2,
      total_pages: 2,
    });

    secondMediaRequest.flush({
      items: [],
      page: 1,
      page_size: 1,
      total: 11,
      total_pages: 11,
    });

    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });

    expect(component.loading()).toBe(false);
    expect(component.error()).toBeNull();

    expect(component.people().length).toBe(2);

    expect(
      component.people()[0]?.name,
    ).toBe('Branco');

    expect(
      component.people()[0]?.mediaCount,
    ).toBe(2);

    expect(
      component.people()[1]?.name,
    ).toBe('Carol');

    expect(
      component.people()[1]?.mediaCount,
    ).toBe(11);
  });
});