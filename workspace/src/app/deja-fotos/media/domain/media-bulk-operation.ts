/*
 * Deja Fotos
 *
 * Media Bulk Operations
 */

import {
  Media,
} from './media';

export type MediaBulkOperationName =
  | 'set_original_date'
  | 'verify_original_date'
  | 'clear_original_date_conflict'
  | 'set_album';

interface MediaBulkOperationBase {
  readonly mediaIds: readonly string[];
}

export interface SetMediaOriginalDateBulkOperation
  extends MediaBulkOperationBase {
  readonly operation: 'set_original_date';
  readonly originalDate: string;
}

export interface VerifyMediaOriginalDateBulkOperation
  extends MediaBulkOperationBase {
  readonly operation: 'verify_original_date';
}

export interface ClearMediaOriginalDateConflictBulkOperation
  extends MediaBulkOperationBase {
  readonly operation: 'clear_original_date_conflict';
}

export interface SetMediaAlbumBulkOperation
  extends MediaBulkOperationBase {
  readonly operation: 'set_album';
  readonly albumId: string | null;
}

export type MediaBulkOperation =
  | SetMediaOriginalDateBulkOperation
  | VerifyMediaOriginalDateBulkOperation
  | ClearMediaOriginalDateConflictBulkOperation
  | SetMediaAlbumBulkOperation;

export interface MediaBulkItemResult {
  readonly mediaId: string;
  readonly success: boolean;
  readonly media: Media | null;
  readonly errorCode: string | null;
  readonly errorMessage: string | null;
}

export interface MediaBulkResult {
  readonly operation: MediaBulkOperationName;
  readonly requestedCount: number;
  readonly succeededCount: number;
  readonly failedCount: number;
  readonly results: readonly MediaBulkItemResult[];
}