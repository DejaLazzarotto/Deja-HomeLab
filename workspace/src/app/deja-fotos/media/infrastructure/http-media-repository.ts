import type {
  MediaType,
} from '../domain/media';

/*
 * Deja Fotos
 *
 * Media HTTP Repository
 *
 * Integra o domínio de mídias com a API FastAPI.
 */

import {
  HttpClient,
  HttpErrorResponse,
  HttpParams,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Media,
  MediaBulkItemResult,
  MediaBulkOperation,
  MediaBulkOperationName,
  MediaBulkResult,
  MediaFilters,
  MediaPage,
  MediaRepository,
  MediaUploadRequest,
} from '../domain';

interface MediaResponse {
  readonly id: string;

  readonly organization_id: string;
  readonly tenant_id: string;
  readonly environment_id: string;

  readonly album_id: string | null;

  readonly original_name: string;
  readonly description: string | null;

  readonly source_content_type: string;
  readonly source_file_extension: string | null;
  readonly source_file_size: number;
  readonly source_checksum_sha256: string;

  readonly media_type: Media['mediaType'];
  readonly content_type: string;
  readonly file_extension: string | null;
  readonly file_size: number;
  readonly checksum_sha256: string;
  readonly was_converted: boolean;

  readonly processing_status: Media['processingStatus'];
  readonly processing_error: string | null;

  readonly original_date: string | null;
  readonly original_date_source: Media['originalDateSource'];
  readonly original_date_precision: Media['originalDatePrecision'];
  readonly original_date_verified: boolean;
  readonly original_date_conflict: boolean;

  readonly width: number | null;
  readonly height: number | null;
  readonly duration_seconds: number | null;

  readonly view_count: number;

  readonly created_by_user_id: string | null;

  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string | null;
}

interface MediaPageResponse {
  readonly items: readonly MediaResponse[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
  readonly total_pages: number;
}

interface MediaBulkItemResponse {
  readonly media_id: string;
  readonly success: boolean;
  readonly media: MediaResponse | null;
  readonly error_code: string | null;
  readonly error_message: string | null;
}

interface MediaBulkResponse {
  readonly operation: MediaBulkOperationName;
  readonly requested_count: number;
  readonly succeeded_count: number;
  readonly failed_count: number;
  readonly results: readonly MediaBulkItemResponse[];
}

type MediaBulkRequest =
  | {
      readonly operation: 'set_original_date';
      readonly media_ids: readonly string[];
      readonly original_date: string;
    }
  | {
      readonly operation: 'verify_original_date';
      readonly media_ids: readonly string[];
    }
  | {
      readonly operation: 'clear_original_date_conflict';
      readonly media_ids: readonly string[];
    }
  | {
      readonly operation: 'set_album';
      readonly media_ids: readonly string[];
      readonly album_id: string | null;
    };

export class HttpMediaRepository implements MediaRepository {
  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    filters: MediaFilters = {},
  ): Promise<MediaPage> {
    const response = await firstValueFrom(
      this.http.get<MediaPageResponse>(
        '/api/fotos/media',
        {
          params: this.mapFilters(filters),
        },
      ),
    );

    return {
      items: response.items.map(item => this.mapMedia(item)),
      page: response.page,
      pageSize: response.page_size,
      total: response.total,
      totalPages: response.total_pages,
    };
  }

  async listByPerson(
    personId: string,
    page: number,
    pageSize: number,
  ): Promise<MediaPage> {
    const response = await firstValueFrom(
      this.http.get<MediaPageResponse>(
        `/api/fotos/people/${personId}/media`,
        {
          params: new HttpParams()
            .set("page", String(page))
            .set("page_size", String(pageSize)),
        },
      ),
    );

    return {
      items: response.items.map(item => this.mapMedia(item)),
      page: response.page,
      pageSize: response.page_size,
      total: response.total,
      totalPages: response.total_pages,
    };
  }

  async findById(
    id: string,
  ): Promise<Media | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<MediaResponse>(
          `/api/fotos/media/${id}`,
        ),
      );

      return this.mapMedia(response);
    } catch (error: unknown) {
      if (
        error instanceof HttpErrorResponse
        && error.status === 404
      ) {
        return undefined;
      }

      throw error;
    }
  }

  async upload(
    request: MediaUploadRequest,
  ): Promise<Media> {
    const formData = new FormData();

    formData.append(
      'environment_id',
      request.environmentId,
    );

    if (request.albumId) {
      formData.append(
        'album_id',
        request.albumId,
      );
    }

    formData.append(
      'file',
      request.file,
      request.file.name,
    );

    const response = await firstValueFrom(
      this.http.post<MediaResponse>(
        '/api/fotos/media',
        formData,
      ),
    );

    return this.mapMedia(response);
  }

  async delete(mediaId: string): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(`/api/fotos/media/${mediaId}`),
    );
  }

  async updateDescription(
    mediaId: string,
    description: string | null,
  ): Promise<Media> {
    const response = await firstValueFrom(
      this.http.patch<MediaResponse>(
        `/api/fotos/media/${mediaId}/description`,
        {
          description,
        },
      ),
    );

    return this.mapMedia(response);
  }

  async bulkUpdate(
    operation: MediaBulkOperation,
  ): Promise<MediaBulkResult> {
    const response = await firstValueFrom(
      this.http.patch<MediaBulkResponse>(
        '/api/fotos/media/bulk',
        this.mapBulkRequest(operation),
      ),
    );

    return {
      operation: response.operation,
      requestedCount: response.requested_count,
      succeededCount: response.succeeded_count,
      failedCount: response.failed_count,
      results: response.results.map(
        result => this.mapBulkItemResult(result),
      ),
    };
  }

  loadThumbnail(
    mediaId: string,
    mediaType: MediaType,
  ): Promise<Blob> {
    const derivativeType = (
      mediaType === 'video'
        ? 'poster'
        : 'thumbnail'
    );

    return firstValueFrom(
      this.http.get(
        `/api/fotos/media/${mediaId}/${derivativeType}`,
        {
          responseType: 'blob',
        },
      ),
    );
  }

  private mapFilters(
    filters: MediaFilters,
  ): HttpParams {
    let params = new HttpParams();

    if (filters.organizationId) {
      params = params.set(
        'organization_id',
        filters.organizationId,
      );
    }

    if (filters.tenantId) {
      params = params.set(
        'tenant_id',
        filters.tenantId,
      );
    }

    if (filters.environmentId) {
      params = params.set(
        'environment_id',
        filters.environmentId,
      );
    }

    if (filters.albumId) {
      params = params.set(
        'album_id',
        filters.albumId,
      );
    }

    if (filters.mediaType) {
      params = params.set(
        'media_type',
        filters.mediaType,
      );
    }

    if (filters.processingStatus) {
      params = params.set(
        'processing_status',
        filters.processingStatus,
      );
    }

    if (filters.originalDateFrom) {
      params = params.set(
        'original_date_from',
        filters.originalDateFrom,
      );
    }

    if (filters.originalDateTo) {
      params = params.set(
        'original_date_to',
        filters.originalDateTo,
      );
    }

    if (filters.originalYear !== undefined) {
      params = params.set(
        'original_year',
        String(filters.originalYear),
      );
    }

    if (filters.originalMonth !== undefined) {
      params = params.set(
        'original_month',
        String(filters.originalMonth),
      );
    }

    if (filters.withoutOriginalDate !== undefined) {
      params = params.set(
        'without_original_date',
        String(filters.withoutOriginalDate),
      );
    }

    if (filters.originalDateVerified !== undefined) {
      params = params.set(
        'original_date_verified',
        String(filters.originalDateVerified),
      );
    }

    if (filters.originalDateConflict !== undefined) {
      params = params.set(
        'original_date_conflict',
        String(filters.originalDateConflict),
      );
    }

    if (filters.wasConverted !== undefined) {
      params = params.set(
        'was_converted',
        String(filters.wasConverted),
      );
    }

    if (filters.page !== undefined) {
      params = params.set(
        'page',
        String(filters.page),
      );
    }

    if (filters.pageSize !== undefined) {
      params = params.set(
        'page_size',
        String(filters.pageSize),
      );
    }

    return params;
  }

  private mapBulkRequest(
    operation: MediaBulkOperation,
  ): MediaBulkRequest {
    switch (operation.operation) {
      case 'set_original_date':
        return {
          operation: operation.operation,
          media_ids: operation.mediaIds,
          original_date: operation.originalDate,
        };

      case 'verify_original_date':
      case 'clear_original_date_conflict':
        return {
          operation: operation.operation,
          media_ids: operation.mediaIds,
        };

      case 'set_album':
        return {
          operation: operation.operation,
          media_ids: operation.mediaIds,
          album_id: operation.albumId,
        };
    }
  }

  private mapBulkItemResult(
    response: MediaBulkItemResponse,
  ): MediaBulkItemResult {
    return {
      mediaId: response.media_id,
      success: response.success,
      media: response.media
        ? this.mapMedia(response.media)
        : null,
      errorCode: response.error_code,
      errorMessage: response.error_message,
    };
  }

  private mapMedia(
    response: MediaResponse,
  ): Media {
    return {
      id: response.id,
      organizationId: response.organization_id,
      tenantId: response.tenant_id,
      environmentId: response.environment_id,
      albumId: response.album_id,
      originalName: response.original_name,
      description: response.description,
      sourceContentType: response.source_content_type,
      sourceFileExtension: response.source_file_extension,
      sourceFileSize: response.source_file_size,
      sourceChecksumSha256: response.source_checksum_sha256,
      mediaType: response.media_type,
      contentType: response.content_type,
      fileExtension: response.file_extension,
      fileSize: response.file_size,
      checksumSha256: response.checksum_sha256,
      wasConverted: response.was_converted,
      processingStatus: response.processing_status,
      processingError: response.processing_error,
      originalDate: response.original_date,
      originalDateSource: response.original_date_source,
      originalDatePrecision: response.original_date_precision,
      originalDateVerified: response.original_date_verified,
      originalDateConflict: response.original_date_conflict,
      width: response.width,
      height: response.height,
      durationSeconds: response.duration_seconds,
      viewCount: response.view_count,
      createdByUserId: response.created_by_user_id,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
      deletedAt: response.deleted_at,
    };
  }
}
