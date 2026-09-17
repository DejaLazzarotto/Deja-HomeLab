/*
 * Deja Fotos
 *
 * Media Repository
 *
 * Porta de acesso às mídias, independente da infraestrutura HTTP.
 */

import {
  MediaBulkOperation,
  MediaBulkResult,
} from './media-bulk-operation';

import {
  MediaFilters,
} from './media-filters';

import {
  Media,
  MediaPage,
} from './media';

export interface MediaRepository {
  list(
    filters?: MediaFilters,
  ): Promise<MediaPage>;

  findById(
    id: string,
  ): Promise<Media | undefined>;

  bulkUpdate(
    operation: MediaBulkOperation,
  ): Promise<MediaBulkResult>;

  loadThumbnail(
    mediaId: string,
  ): Promise<Blob>;
}