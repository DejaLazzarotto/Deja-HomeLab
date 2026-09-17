/*
 * Deja Fotos
 *
 * Media Filters
 */

import {
  MediaProcessingStatus,
  MediaType,
} from './media';

export interface MediaFilters {
  readonly organizationId?: string;
  readonly tenantId?: string;
  readonly environmentId?: string;
  readonly albumId?: string;

  readonly mediaType?: MediaType;
  readonly processingStatus?: MediaProcessingStatus;

  readonly originalDateFrom?: string;
  readonly originalDateTo?: string;
  readonly originalYear?: number;
  readonly originalMonth?: number;

  readonly withoutOriginalDate?: boolean;
  readonly originalDateVerified?: boolean;
  readonly originalDateConflict?: boolean;
  readonly wasConverted?: boolean;

  readonly page?: number;
  readonly pageSize?: number;
}