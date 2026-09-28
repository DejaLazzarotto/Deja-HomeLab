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
  HttpMediaRepository,
} from './http-media-repository';

describe('HttpMediaRepository', () => {
  let repository: HttpMediaRepository;
  let httpTesting: HttpTestingController;

  const organizationId =
    '11111111-1111-1111-1111-111111111111';

  const tenantId =
    '22222222-2222-2222-2222-222222222222';

  const environmentId =
    '33333333-3333-3333-3333-333333333333';

  const albumId =
    '44444444-4444-4444-4444-444444444444';

  const mediaId =
    '55555555-5555-5555-5555-555555555555';

  const mediaResponse = {
    id: mediaId,
    organization_id: organizationId,
    tenant_id: tenantId,
    environment_id: environmentId,
    album_id: albumId,
    original_name: 'foto-teste.jpg',
    description: 'Descrição de teste',
    source_content_type: 'image/jpeg',
    source_file_extension: '.jpg',
    source_file_size: 2048,
    source_checksum_sha256: 'source-checksum',
    media_type: 'image' as const,
    content_type: 'image/jpeg',
    file_extension: '.jpg',
    file_size: 2048,
    checksum_sha256: 'managed-checksum',
    was_converted: false,
    processing_status: 'ready' as const,
    processing_error: null,
    original_date: '2024-03-10T15:00:00',
    original_date_source: 'manual' as const,
    original_date_precision: 'datetime' as const,
    original_date_verified: true,
    original_date_conflict: false,
    width: 1920,
    height: 1080,
    duration_seconds: null,
    view_count: 7,
    created_by_user_id: null,
    created_at: '2026-09-17T10:00:00',
    updated_at: '2026-09-17T11:00:00',
    deleted_at: null,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpMediaRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('deletes only the requested media', async () => {
    const result = repository.delete(mediaId);
    const request = httpTesting.expectOne(`/api/fotos/media/${mediaId}`);
    expect(request.request.method).toBe('DELETE');
    request.flush(null);
    await expect(result).resolves.toBeUndefined();
  });

  it('should list and map a paginated media response with filters', async () => {
    const resultPromise = repository.list({
      organizationId,
      tenantId,
      environmentId,
      albumId,
      mediaType: 'image',
      processingStatus: 'ready',
      originalDateFrom: '2024-03-01T00:00:00.000Z',
      originalDateTo: '2024-03-31T23:59:59.999Z',
      originalYear: 2024,
      originalMonth: 3,
      withoutOriginalDate: false,
      originalDateVerified: true,
      originalDateConflict: false,
      wasConverted: false,
      page: 2,
      pageSize: 24,
    });

    const request = httpTesting.expectOne(candidate =>
      candidate.url === '/api/fotos/media'
      && candidate.params.get('organization_id')
        === organizationId
      && candidate.params.get('tenant_id') === tenantId
      && candidate.params.get('environment_id')
        === environmentId
      && candidate.params.get('album_id') === albumId
      && candidate.params.get('media_type') === 'image'
      && candidate.params.get('processing_status') === 'ready'
      && candidate.params.get('original_year') === '2024'
      && candidate.params.get('original_month') === '3'
      && candidate.params.get('without_original_date') === 'false'
      && candidate.params.get('original_date_verified') === 'true'
      && candidate.params.get('original_date_conflict') === 'false'
      && candidate.params.get('was_converted') === 'false'
      && candidate.params.get('page') === '2'
      && candidate.params.get('page_size') === '24',
    );

    expect(request.request.method).toBe('GET');

    request.flush({
      items: [
        mediaResponse,
      ],
      page: 2,
      page_size: 24,
      total: 25,
      total_pages: 2,
    });

    await expect(resultPromise).resolves.toEqual({
      items: [
        {
          id: mediaId,
          organizationId,
          tenantId,
          environmentId,
          albumId,
          originalName: 'foto-teste.jpg',
          description: 'Descrição de teste',
          sourceContentType: 'image/jpeg',
          sourceFileExtension: '.jpg',
          sourceFileSize: 2048,
          sourceChecksumSha256: 'source-checksum',
          mediaType: 'image',
          contentType: 'image/jpeg',
          fileExtension: '.jpg',
          fileSize: 2048,
          checksumSha256: 'managed-checksum',
          wasConverted: false,
          processingStatus: 'ready',
          processingError: null,
          originalDate: '2024-03-10T15:00:00',
          originalDateSource: 'manual',
          originalDatePrecision: 'datetime',
          originalDateVerified: true,
          originalDateConflict: false,
          width: 1920,
          height: 1080,
          durationSeconds: null,
          viewCount: 7,
          createdByUserId: null,
          createdAt: '2026-09-17T10:00:00',
          updatedAt: '2026-09-17T11:00:00',
          deletedAt: null,
        },
      ],
      page: 2,
      pageSize: 24,
      total: 25,
      totalPages: 2,
    });
  });

  it('should return undefined when media is not found', async () => {
    const resultPromise = repository.findById(mediaId);

    const request = httpTesting.expectOne(
      `/api/fotos/media/${mediaId}`,
    );

    request.flush(
      {
        detail: 'Mídia não encontrada.',
      },
      {
        status: 404,
        statusText: 'Not Found',
      },
    );

    await expect(resultPromise).resolves.toBeUndefined();
  });

  it('should upload media as multipart form data', async () => {
    const file = new File(
      [
        'photo',
      ],
      'photo.jpg',
      {
        type: 'image/jpeg',
      },
    );

    const resultPromise = repository.upload({
      environmentId,
      albumId,
      file,
    });

    const request = httpTesting.expectOne(
      '/api/fotos/media',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toBeInstanceOf(FormData);

    const formData =
      request.request.body as FormData;

    expect(
      formData.get('environment_id'),
    ).toBe(environmentId);

    expect(
      formData.get('album_id'),
    ).toBe(albumId);

    const uploadedFile =
      formData.get('file');

    expect(uploadedFile).toBeInstanceOf(File);

    expect(
      (uploadedFile as File).name,
    ).toBe('photo.jpg');

    expect(
      (uploadedFile as File).type,
    ).toBe('image/jpeg');

    request.flush(mediaResponse);

    await expect(resultPromise).resolves.toMatchObject({
      id: mediaId,
      environmentId,
      albumId,
      originalName: 'foto-teste.jpg',
      mediaType: 'image',
    });
  });

  it('should update and map a media description', async () => {
    const resultPromise = repository.updateDescription(
      mediaId,
      'Vídeo do casamento',
    );

    const request = httpTesting.expectOne(
      `/api/fotos/media/${mediaId}/description`,
    );

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual({
      description: 'Vídeo do casamento',
    });

    request.flush({
      ...mediaResponse,
      media_type: 'video',
      description: 'Vídeo do casamento',
    });

    await expect(resultPromise).resolves.toMatchObject({
      id: mediaId,
      mediaType: 'video',
      description: 'Vídeo do casamento',
    });
  });

  it('should map a bulk operation and preserve partial failures', async () => {
    const failedMediaId =
      '66666666-6666-6666-6666-666666666666';

    const resultPromise = repository.bulkUpdate({
      operation: 'set_album',
      mediaIds: [
        mediaId,
        failedMediaId,
      ],
      albumId,
    });

    const request = httpTesting.expectOne(
      '/api/fotos/media/bulk',
    );

    expect(request.request.method).toBe('PATCH');

    expect(request.request.body).toEqual({
      operation: 'set_album',
      media_ids: [
        mediaId,
        failedMediaId,
      ],
      album_id: albumId,
    });

    request.flush({
      operation: 'set_album',
      requested_count: 2,
      succeeded_count: 1,
      failed_count: 1,
      results: [
        {
          media_id: mediaId,
          success: true,
          media: mediaResponse,
          error_code: null,
          error_message: null,
        },
        {
          media_id: failedMediaId,
          success: false,
          media: null,
          error_code: 'fotos_media_album_scope_mismatch',
          error_message: 'O álbum pertence a outro escopo.',
        },
      ],
    });

    await expect(resultPromise).resolves.toMatchObject({
      operation: 'set_album',
      requestedCount: 2,
      succeededCount: 1,
      failedCount: 1,
      results: [
        {
          mediaId,
          success: true,
          media: {
            id: mediaId,
            albumId,
          },
          errorCode: null,
          errorMessage: null,
        },
        {
          mediaId: failedMediaId,
          success: false,
          media: null,
          errorCode: 'fotos_media_album_scope_mismatch',
          errorMessage: 'O álbum pertence a outro escopo.',
        },
      ],
    });
  });

  it('should load an authenticated thumbnail as blob', async () => {
    const resultPromise = repository.loadThumbnail(
      mediaId,
      'image',
    );

    const request = httpTesting.expectOne(
      `/api/fotos/media/${mediaId}/thumbnail`,
    );

    expect(request.request.method).toBe('GET');
    expect(request.request.responseType).toBe('blob');

    const thumbnail = new Blob(
      [
        'thumbnail',
      ],
      {
        type: 'image/jpeg',
      },
    );

    request.flush(thumbnail);

    const result = await resultPromise;

    expect(result).toBeInstanceOf(Blob);
    expect(result.type).toBe('image/jpeg');
  });

  it('should load a video poster as its thumbnail', async () => {
    const resultPromise = repository.loadThumbnail(
      mediaId,
      'video',
    );

    const request = httpTesting.expectOne(
      `/api/fotos/media/${mediaId}/poster`,
    );

    expect(request.request.method).toBe('GET');
    expect(request.request.responseType).toBe('blob');

    const poster = new Blob(
      [
        'poster',
      ],
      {
        type: 'image/webp',
      },
    );

    request.flush(poster);

    const result = await resultPromise;

    expect(result).toBeInstanceOf(Blob);
    expect(result.type).toBe('image/webp');
  });

});
