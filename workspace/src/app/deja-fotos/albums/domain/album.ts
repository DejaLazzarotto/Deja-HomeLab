/*
 * Deja Fotos
 *
 * Album Domain
 */

export interface Album {
  readonly id: string;

  readonly organizationId: string;
  readonly tenantId: string;
  readonly environmentId: string;

  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;

  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface AlbumInput {
  readonly environmentId: string;
  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;
}

export interface AlbumFilters {
  readonly organizationId?: string;
  readonly tenantId?: string;
  readonly environmentId?: string;
  readonly active?: boolean;
}

export interface AlbumPeriod {
  readonly year: number | null;
  readonly month: number | null;
  readonly mediaCount: number;
  readonly description: string | null;
}

export interface AlbumPeriodDescriptionInput {
  readonly description: string | null;
}