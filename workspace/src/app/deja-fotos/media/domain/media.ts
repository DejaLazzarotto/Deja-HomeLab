/*
 * Deja Fotos
 *
 * Media Domain
 *
 * Tipos centrais das mídias e de sua curadoria administrativa.
 */

export type MediaType =
  | 'image'
  | 'video';

export type MediaProcessingStatus =
  | 'received'
  | 'validating'
  | 'processing'
  | 'ready'
  | 'failed'
  | 'quarantine';

export type MediaOriginalDateSource =
  | 'embedded_metadata'
  | 'source_folder'
  | 'filename'
  | 'filesystem'
  | 'manual'
  | 'ai_suggested';

export interface Media {
  readonly id: string;

  readonly organizationId: string;
  readonly tenantId: string;
  readonly environmentId: string;

  readonly albumId: string | null;

  readonly originalName: string;

  readonly sourceContentType: string;
  readonly sourceFileExtension: string | null;
  readonly sourceFileSize: number;
  readonly sourceChecksumSha256: string;

  readonly mediaType: MediaType;
  readonly contentType: string;
  readonly fileExtension: string | null;
  readonly fileSize: number;
  readonly checksumSha256: string;
  readonly wasConverted: boolean;

  readonly processingStatus: MediaProcessingStatus;
  readonly processingError: string | null;

  readonly originalDate: string | null;
  readonly originalDateSource: MediaOriginalDateSource | null;
  readonly originalDateVerified: boolean;
  readonly originalDateConflict: boolean;

  readonly width: number | null;
  readonly height: number | null;
  readonly durationSeconds: number | null;

  readonly viewCount: number;

  readonly createdByUserId: string | null;

  readonly createdAt: string;
  readonly updatedAt: string;
  readonly deletedAt: string | null;
}

export interface MediaPage {
  readonly items: readonly Media[];
  readonly page: number;
  readonly pageSize: number;
  readonly total: number;
  readonly totalPages: number;
}