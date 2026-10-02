import {
  HttpClient,
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
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
} from 'vitest';

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

    const request = http.expectOne(
      '/api/v1/organizations',
    );

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

  it('should list tenants by organization', async () => {
    const promise = repository.listTenants(
      'organization-id',
    );

    const request = http.expectOne(
      request =>
        request.url === '/api/v1/tenants'
        && request.params.get('organization_id')
          === 'organization-id',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      {
        id: 'tenant-id',
        organization_id: 'organization-id',
        name: 'Tenant Teste',
        status: 'active',
        created_at: '2026-08-24T10:00:00',
        updated_at: '2026-08-24T10:00:00',
      },
    ]);

    await expect(promise).resolves.toEqual([
      {
        id: 'tenant-id',
        organizationId: 'organization-id',
        name: 'Tenant Teste',
        status: 'active',
        createdAt: '2026-08-24T10:00:00',
        updatedAt: '2026-08-24T10:00:00',
      },
    ]);
  });

  it('should create a tenant', async () => {
    const promise = repository.createTenant({
      organizationId: 'organization-id',
      name: 'Tenant Teste',
      status: 'active',
    });

    const request = http.expectOne(
      '/api/v1/tenants',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      organization_id: 'organization-id',
      name: 'Tenant Teste',
      status: 'active',
    });

    request.flush({
      id: 'tenant-id',
      organization_id: 'organization-id',
      name: 'Tenant Teste',
      status: 'active',
      created_at: '2026-08-24T10:00:00',
      updated_at: '2026-08-24T10:00:00',
    });

    await expect(promise).resolves.toEqual({
      id: 'tenant-id',
      organizationId: 'organization-id',
      name: 'Tenant Teste',
      status: 'active',
      createdAt: '2026-08-24T10:00:00',
      updatedAt: '2026-08-24T10:00:00',
    });
  });

  it('should update a tenant', async () => {
    const promise = repository.updateTenant(
      'tenant-id',
      {
        organizationId: 'organization-id',
        name: 'Tenant Atualizado',
        status: 'inactive',
      },
    );

    const request = http.expectOne(
      '/api/v1/tenants/tenant-id',
    );

    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual({
      organization_id: 'organization-id',
      name: 'Tenant Atualizado',
      status: 'inactive',
    });

    request.flush({
      id: 'tenant-id',
      organization_id: 'organization-id',
      name: 'Tenant Atualizado',
      status: 'inactive',
      created_at: '2026-08-24T10:00:00',
      updated_at: '2026-08-25T10:00:00',
    });

    await expect(promise).resolves.toEqual({
      id: 'tenant-id',
      organizationId: 'organization-id',
      name: 'Tenant Atualizado',
      status: 'inactive',
      createdAt: '2026-08-24T10:00:00',
      updatedAt: '2026-08-25T10:00:00',
    });
  });

  it('should delete a tenant', async () => {
    const promise = repository.deleteTenant(
      'tenant-id',
    );

    const request = http.expectOne(
      '/api/v1/tenants/tenant-id',
    );

    expect(request.request.method).toBe('DELETE');

    request.flush(null);

    await expect(promise).resolves.toBeUndefined();
  });

  it('should list environments by tenant', async () => {
    const promise = repository.listEnvironments(
      'tenant-id',
    );

    const request = http.expectOne(
      request =>
        request.url === '/api/v1/environments'
        && request.params.get('tenant_id')
          === 'tenant-id',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      {
        id: 'environment-id',
        tenant_id: 'tenant-id',
        name: 'Produção',
        status: 'active',
        created_at: '2026-08-24T10:00:00',
        updated_at: '2026-08-24T10:00:00',
      },
    ]);

    await expect(promise).resolves.toEqual([
      {
        id: 'environment-id',
        tenantId: 'tenant-id',
        name: 'Produção',
        status: 'active',
        createdAt: '2026-08-24T10:00:00',
        updatedAt: '2026-08-24T10:00:00',
      },
    ]);
  });

  it('should create an environment', async () => {
    const promise = repository.createEnvironment({
      tenantId: 'tenant-id',
      name: 'Produção',
      status: 'active',
    });

    const request = http.expectOne(
      '/api/v1/environments',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      tenant_id: 'tenant-id',
      name: 'Produção',
      status: 'active',
    });

    request.flush({
      id: 'environment-id',
      tenant_id: 'tenant-id',
      name: 'Produção',
      status: 'active',
      created_at: '2026-08-24T10:00:00',
      updated_at: '2026-08-24T10:00:00',
    });

    await expect(promise).resolves.toEqual({
      id: 'environment-id',
      tenantId: 'tenant-id',
      name: 'Produção',
      status: 'active',
      createdAt: '2026-08-24T10:00:00',
      updatedAt: '2026-08-24T10:00:00',
    });
  });

  it('should update an environment', async () => {
    const promise = repository.updateEnvironment(
      'environment-id',
      {
        tenantId: 'tenant-id',
        name: 'Homologação',
        status: 'inactive',
      },
    );

    const request = http.expectOne(
      '/api/v1/environments/environment-id',
    );

    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual({
      tenant_id: 'tenant-id',
      name: 'Homologação',
      status: 'inactive',
    });

    request.flush({
      id: 'environment-id',
      tenant_id: 'tenant-id',
      name: 'Homologação',
      status: 'inactive',
      created_at: '2026-08-24T10:00:00',
      updated_at: '2026-08-25T10:00:00',
    });

    await expect(promise).resolves.toEqual({
      id: 'environment-id',
      tenantId: 'tenant-id',
      name: 'Homologação',
      status: 'inactive',
      createdAt: '2026-08-24T10:00:00',
      updatedAt: '2026-08-25T10:00:00',
    });
  });

  it('should delete an environment', async () => {
    const promise = repository.deleteEnvironment(
      'environment-id',
    );

    const request = http.expectOne(
      '/api/v1/environments/environment-id',
    );

    expect(request.request.method).toBe('DELETE');

    request.flush(null);

    await expect(promise).resolves.toBeUndefined();
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
      [
        'indicators',
        'reports',
      ],
    );

    const request = http.expectOne(
      '/api/v1/organizations/organization-id/modules',
    );

    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual({
      enabled_modules: [
        'indicators',
        'reports',
      ],
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