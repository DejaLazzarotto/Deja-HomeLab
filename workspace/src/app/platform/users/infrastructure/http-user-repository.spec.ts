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
  UserInput,
} from '../domain';

import {
  HttpUserRepository,
} from './http-user-repository';

describe('HttpUserRepository', () => {

  let repository: HttpUserRepository;
  let httpTesting: HttpTestingController;

  const organizationId =
    '11111111-1111-1111-1111-111111111111';

  const tenantId =
    '22222222-2222-2222-2222-222222222222';

  const environmentId =
    '33333333-3333-3333-3333-333333333333';

  const userResponse = {
    id: '44444444-4444-4444-4444-444444444444',
    organization_id: organizationId,
    tenant_id: tenantId,
    environment_id: environmentId,
    name: 'Usuário Demonstração',
    email: 'usuario@example.com',
    role: 'analyst' as const,
    status: 'active' as const,
    created_at: '2026-08-20T10:00:00',
    updated_at: '2026-08-20T10:00:00',
  };

  const input: UserInput = {
    organizationId,
    tenantId,
    environmentId,
    name: ' Usuário Teste ',
    email: 'TESTE@EXAMPLE.COM',
    role: 'analyst',
    status: 'active',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpUserRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should list and map users with filters', async () => {
    const resultPromise = repository.list({
      organizationId,
      tenantId,
      environmentId,
      status: 'active',
    });

    const request = httpTesting.expectOne(candidate => (
      candidate.url === '/api/v1/users'
      && candidate.params.get('organization_id') === organizationId
      && candidate.params.get('tenant_id') === tenantId
      && candidate.params.get('environment_id') === environmentId
      && candidate.params.get('user_status') === 'active'
    ));

    expect(request.request.method).toBe('GET');

    request.flush([
      userResponse,
    ]);

    await expect(resultPromise).resolves.toEqual([
      {
        id: userResponse.id,
        organizationId,
        tenantId,
        environmentId,
        name: userResponse.name,
        email: userResponse.email,
        role: userResponse.role,
        status: userResponse.status,
        createdAt: userResponse.created_at,
        updatedAt: userResponse.updated_at,
      },
    ]);
  });

  it('should normalize and create a user', async () => {
    const resultPromise = repository.create(input);

    const request =
      httpTesting.expectOne('/api/v1/users');

    expect(request.request.method).toBe('POST');

    expect(request.request.body).toEqual({
      organization_id: organizationId,
      tenant_id: tenantId,
      environment_id: environmentId,
      name: 'Usuário Teste',
      email: 'teste@example.com',
      role: 'analyst',
      status: 'active',
    });

    request.flush({
      ...userResponse,
      name: 'Usuário Teste',
      email: 'teste@example.com',
    });

    await expect(resultPromise).resolves.toMatchObject({
      organizationId,
      tenantId,
      environmentId,
      name: 'Usuário Teste',
      email: 'teste@example.com',
    });
  });

  it('should update a user', async () => {
    const resultPromise = repository.update(
      userResponse.id,
      input,
    );

    const request = httpTesting.expectOne(
      `/api/v1/users/${userResponse.id}`,
    );

    expect(request.request.method).toBe('PUT');

    request.flush({
      ...userResponse,
      name: 'Usuário Teste',
      email: 'teste@example.com',
    });

    await expect(resultPromise).resolves.toMatchObject({
      id: userResponse.id,
      name: 'Usuário Teste',
      email: 'teste@example.com',
    });
  });

  it('should set a user password', async () => {
    const resultPromise = repository.setPassword(
      userResponse.id,
      'Analyst21!',
    );

    const request = httpTesting.expectOne(
      `/api/v1/users/${userResponse.id}/password`,
    );

    expect(request.request.method).toBe('PUT');

    expect(request.request.body).toEqual({
      password: 'Analyst21!',
    });

    request.flush(userResponse);

    await expect(resultPromise).resolves.toMatchObject({
      id: userResponse.id,
      email: userResponse.email,
    });
  });

it('should load user module accesses', async () => {
  const resultPromise =
    repository.getModuleAccesses(
      userResponse.id,
    );

  const request = httpTesting.expectOne(
    `/api/v1/users/${userResponse.id}/modules`,
  );

  expect(request.request.method).toBe('GET');

  request.flush({
    user_id: userResponse.id,
    modules: [
      {
        key: 'fotos',
        name: 'Fotos',
        description: 'Gestão de fotos e vídeos.',
        display_order: 50,
        organization_enabled: true,
        has_access: true,
        role: 'manager',
      },
      {
        key: 'indicators',
        name: 'Indicadores',
        description: 'Gestão de indicadores.',
        display_order: 10,
        organization_enabled: true,
        has_access: false,
        role: null,
      },
    ],
  });

  await expect(resultPromise).resolves.toEqual({
    userId: userResponse.id,
    modules: [
      {
        key: 'fotos',
        name: 'Fotos',
        description: 'Gestão de fotos e vídeos.',
        displayOrder: 50,
        organizationEnabled: true,
        hasAccess: true,
        role: 'manager',
      },
      {
        key: 'indicators',
        name: 'Indicadores',
        description: 'Gestão de indicadores.',
        displayOrder: 10,
        organizationEnabled: true,
        hasAccess: false,
        role: null,
      },
    ],
  });
});

it('should save user module accesses', async () => {
  const resultPromise =
    repository.updateModuleAccesses(
      userResponse.id,
      [
        {
          moduleKey: 'fotos',
          role: 'manager',
        },
        {
          moduleKey: 'indicators',
          role: 'viewer',
        },
      ],
    );

  const request = httpTesting.expectOne(
    `/api/v1/users/${userResponse.id}/modules`,
  );

  expect(request.request.method).toBe('PUT');

  expect(request.request.body).toEqual({
    modules: [
      {
        module_key: 'fotos',
        role: 'manager',
      },
      {
        module_key: 'indicators',
        role: 'viewer',
      },
    ],
  });

  request.flush({
    user_id: userResponse.id,
    modules: [
      {
        key: 'fotos',
        name: 'Fotos',
        description: 'Gestão de fotos e vídeos.',
        display_order: 50,
        organization_enabled: true,
        has_access: true,
        role: 'manager',
      },
      {
        key: 'indicators',
        name: 'Indicadores',
        description: 'Gestão de indicadores.',
        display_order: 10,
        organization_enabled: true,
        has_access: true,
        role: 'viewer',
      },
    ],
  });

  await expect(resultPromise).resolves.toEqual({
    userId: userResponse.id,
    modules: [
      {
        key: 'fotos',
        name: 'Fotos',
        description: 'Gestão de fotos e vídeos.',
        displayOrder: 50,
        organizationEnabled: true,
        hasAccess: true,
        role: 'manager',
      },
      {
        key: 'indicators',
        name: 'Indicadores',
        description: 'Gestão de indicadores.',
        displayOrder: 10,
        organizationEnabled: true,
        hasAccess: true,
        role: 'viewer',
      },
    ],
  });
});

});