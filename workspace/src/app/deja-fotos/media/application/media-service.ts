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
} from '../domain';

export class MediaService {
  constructor(
    private readonly repository: MediaRepository,
  ) {}

  list(
    filters: MediaFilters = {},
  ): Promise<MediaPage> {
    return this.repository.list(filters);
  }

  findById(
    id: string,
  ): Promise<Media | undefined> {
    return this.repository.findById(id);
  }

  bulkUpdate(
    operation: MediaBulkOperation,
  ): Promise<MediaBulkResult> {
    this.validateMediaIds(operation.mediaIds);

    return this.repository.bulkUpdate(operation);
  }

  loadThumbnail(
    mediaId: string,
  ): Promise<Blob> {
    if (!mediaId.trim()) {
      throw new Error('O identificador da mídia é obrigatório.');
    }

    return this.repository.loadThumbnail(mediaId);
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