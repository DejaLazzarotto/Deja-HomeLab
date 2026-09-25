import type {
  MediaType,
} from '../domain/media';

/*
 * Deja Fotos
 *
 * Media Application Service
 */

import {
  Media,
  MediaBulkOperation,
  MediaBulkResult,
  MediaFilters,
  MediaPage,
  MediaRepository,
  MediaUploadRequest,
} from '../domain';

const MAX_UPLOAD_SIZE_BYTES =
  500 * 1024 * 1024;

const ALLOWED_UPLOAD_CONTENT_TYPES =
  new Set([
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/gif',
    'image/bmp',
    'image/x-ms-bmp',
    'video/mp4',
    'video/quicktime',
    'video/mpeg',
  ]);

export class MediaService {
  constructor(
    private readonly repository: MediaRepository,
  ) {}

  list(
    filters: MediaFilters = {},
  ): Promise<MediaPage> {
    return this.repository.list(filters);
  }

  listByPerson(
    personId: string,
    page: number,
    pageSize: number,
  ): Promise<MediaPage> {
    return this.repository.listByPerson(
      personId,
      page,
      pageSize,
    );
  }

  findById(
    id: string,
  ): Promise<Media | undefined> {
    return this.repository.findById(id);
  }

  upload(
    request: MediaUploadRequest,
  ): Promise<Media> {
    const environmentId =
      request.environmentId.trim();

    if (!environmentId) {
      throw new Error(
        'Selecione o ambiente de destino.',
      );
    }

    if (!request.file.name.trim()) {
      throw new Error(
        'O arquivo selecionado não possui nome.',
      );
    }

    if (request.file.size === 0) {
      throw new Error(
        `O arquivo ${request.file.name} está vazio.`,
      );
    }

    if (
      request.file.size > MAX_UPLOAD_SIZE_BYTES
    ) {
      throw new Error(
        `O arquivo ${request.file.name} excede o limite de 500 MB.`,
      );
    }

    if (
      !ALLOWED_UPLOAD_CONTENT_TYPES.has(
        request.file.type,
      )
    ) {
      throw new Error(
        `O formato do arquivo ${request.file.name} não é aceito.`,
      );
    }

    return this.repository.upload({
      environmentId,
      albumId:
        request.albumId?.trim() || null,
      file: request.file,
    });
  }

  bulkUpdate(
    operation: MediaBulkOperation,
  ): Promise<MediaBulkResult> {
    this.validateMediaIds(operation.mediaIds);

    return this.repository.bulkUpdate(operation);
  }

  delete(mediaId: string): Promise<void> {
    if (!mediaId.trim()) {
      throw new Error('O identificador da mídia é obrigatório.');
    }

    return this.repository.delete(mediaId);
  }

  loadThumbnail(
    mediaId: string,
    mediaType: MediaType,
  ): Promise<Blob> {
    if (!mediaId.trim()) {
      throw new Error('O identificador da mídia é obrigatório.');
    }

    return this.repository.loadThumbnail(
      mediaId,
      mediaType,
    );
  }

  private validateMediaIds(
    mediaIds: readonly string[],
  ): void {
    if (mediaIds.length === 0) {
      throw new Error('Selecione ao menos uma mídia.');
    }

    if (mediaIds.length > 100) {
      throw new Error('Selecione no máximo 100 mídias por operação.');
    }

    if (new Set(mediaIds).size !== mediaIds.length) {
      throw new Error('A seleção contém mídias repetidas.');
    }
  }
}
