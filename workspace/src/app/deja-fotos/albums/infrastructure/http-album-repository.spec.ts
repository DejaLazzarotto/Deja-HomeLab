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
  AlbumInput,
} from '../domain';

import {
  HttpAlbumRepository,
} from './http-album-repository';

describe('HttpAlbumRepository', () => {
  let repository: HttpAlbumRepository;
  let httpTesting: HttpTestingController;

  const organizationId =
    '11111111-1111-1111-1111-111111111111';

  const tenantId =
    '22222222-2222-2222-2222-222222222222';

  const environmentId =
    '33333333-3333-3333-3333-333333333333';

  const albumId =
    '44444444-4444-4444-4444-444444444444';

  const albumResponse = {
    id: albumId,
    organization_id: organizationId,
    tenant_id: tenantId,
    environment_id: environmentId,
    name: 'Viagem 2024',
    description: 'Registros da viagem.',
    active: true,
    created_at: '2026-09-17T10:00:00',
    updated_at: '2026-09-17T11:00:00',
  };

  const input: AlbumInput = {
    environmentId,
    name: 'Viagem 2024',
    description: 'Registros da viagem.',
    active: true,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpAlbumRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should list and map albums using filters', async () => {
    const resultPromise = repository.list({
      organizationId,
      tenantId,
      environmentId,
      active: false,
    });

    const request = httpTesting.expectOne(candidate =>
      candidate.url === '/api/fotos/albums'
      && candidate.params.get('organization_id')
        === organizationId
      && candidate.params.get('tenant_id') === tenantId
      && candidate.params.get('environment_id')
        === environmentId
      && candidate.params.get('active') === 'false',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      {
        ...albumResponse,
        active: false,
      },
    ]);

    await expect(resultPromise).resolves.toEqual([
      {
        id: albumId,
        organizationId,
        tenantId,
        environmentId,
        name: 'Viagem 2024',
        description: 'Registros da viagem.',
        active: false,
        createdAt: '2026-09-17T10:00:00',
        updatedAt: '2026-09-17T11:00:00',
      },
    ]);
  });

  it('should return undefined when an album is not found', async () => {
    const resultPromise = repository.findById(albumId);

    const request = httpTesting.expectOne(
      `/api/fotos/albums/${albumId}`,
    );

    request.flush(
      {
        detail: 'Álbum não encontrado.',
      },
      {
        status: 404,
        statusText: 'Not Found',
      },
    );

    await expect(resultPromise).resolves.toBeUndefined();
  });

  it('should create an album using the API contract', async () => {
    const resultPromise = repository.create(input);

    const request = httpTesting.expectOne(
      '/api/fotos/albums',
    );

    expect(request.request.method).toBe('POST');

    expect(request.request.body).toEqual({
      environment_id: environmentId,
      name: 'Viagem 2024',
      description: 'Registros da viagem.',
      active: true,
    });

    request.flush(albumResponse);

    await expect(resultPromise).resolves.toMatchObject({
      id: albumId,
      environmentId,
      name: 'Viagem 2024',
      active: true,
    });
  });

  it('should update and delete an album', async () => {
    const updatePromise = repository.update(
      albumId,
      {
        ...input,
        name: 'Viagem 2024 atualizada',
        active: false,
      },
    );

    const updateRequest = httpTesting.expectOne(
      `/api/fotos/albums/${albumId}`,
    );

    expect(updateRequest.request.method).toBe('PUT');

    expect(updateRequest.request.body).toEqual({
      environment_id: environmentId,
      name: 'Viagem 2024 atualizada',
      description: 'Registros da viagem.',
      active: false,
    });

    updateRequest.flush({
      ...albumResponse,
      name: 'Viagem 2024 atualizada',
      active: false,
    });

    await expect(updatePromise).resolves.toMatchObject({
      name: 'Viagem 2024 atualizada',
      active: false,
    });

    const deletePromise = repository.delete(albumId);

    const deleteRequest = httpTesting.expectOne(
      `/api/fotos/albums/${albumId}`,
    );

    expect(deleteRequest.request.method).toBe('DELETE');

    deleteRequest.flush(null);

    await expect(deletePromise).resolves.toBeUndefined();
  });
});