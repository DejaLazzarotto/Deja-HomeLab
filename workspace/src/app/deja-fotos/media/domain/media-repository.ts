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
  MediaType,
} from './media';

export interface MediaUploadRequest {
  readonly environmentId: string;
  readonly albumId: string | null;
  readonly file: File;
}

export interface MediaRepository {
  list(
    filters?: MediaFilters,
  ): Promise<MediaPage>;

  listByPerson(
    personId: string,
    page: number,
    pageSize: number,
  ): Promise<MediaPage>;

  findById(
    id: string,
  ): Promise<Media | undefined>;

  upload(
    request: MediaUploadRequest,
  ): Promise<Media>;

  delete(
    mediaId: string,
  ): Promise<void>;

  bulkUpdate(
    operation: MediaBulkOperation,
  ): Promise<MediaBulkResult>;

  loadThumbnail(
    mediaId: string,
    mediaType: MediaType,
  ): Promise<Blob>;
}
