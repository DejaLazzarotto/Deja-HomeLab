import {
  provideHttpClient,
} from '@angular/common/http';

import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import {
  TestBed,
} from '@angular/core/testing';

import {
  HttpClient,
} from '@angular/common/http';

import {
  HttpModuleManagementRepository,
} from './http-module-management-repository';

describe('HttpModuleManagementRepository', () => {
  let repository: HttpModuleManagementRepository;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpModuleManagementRepository(
      TestBed.inject(HttpClient),
    );
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('should list organizations', async () => {
    const promise = repository.listOrganizations();
    const request = http.expectOne('/api/v1/organizations');

    request.flush([
      {
        id: 'organization-id',
        code: 'ORG-TESTE',
        name: 'Organização Teste',
        status: 'active',
        created_at: '2026-08-24T10:00:00',
        updated_at: '2026-08-24T10:00:00',
      },
    ]);

    await expect(promise).resolves.toEqual([
      {
        id: 'organization-id',
        code: 'ORG-TESTE',
        name: 'Organização Teste',
        status: 'active',
        createdAt: '2026-08-24T10:00:00',
        updatedAt: '2026-08-24T10:00:00',
      },
    ]);
  });

  it('should load organization modules', async () => {
    const promise = repository.getOrganizationModules(
      'organization-id',
    );
    const request = http.expectOne(
      '/api/v1/organizations/organization-id/modules',
    );

    request.flush({
      organization_id: 'organization-id',
      modules: [
        {
          key: 'indicators',
          name: 'Indicadores',
          description: 'Gestão de indicadores.',
          display_order: 10,
          enabled: true,
        },
      ],
    });

    await expect(promise).resolves.toEqual({
      organizationId: 'organization-id',
      modules: [
        {
          key: 'indicators',
          name: 'Indicadores',
          description: 'Gestão de indicadores.',
          displayOrder: 10,
          enabled: true,
        },
      ],
    });
  });

  it('should save enabled modules atomically', async () => {
    const promise = repository.updateOrganizationModules(
      'organization-id',
      ['indicators', 'reports'],
    );
    const request = http.expectOne(
      '/api/v1/organizations/organization-id/modules',
    );

    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual({
      enabled_modules: ['indicators', 'reports'],
    });

    request.flush({
      organization_id: 'organization-id',
      modules: [],
    });

    await expect(promise).resolves.toEqual({
      organizationId: 'organization-id',
      modules: [],
    });
  });
});