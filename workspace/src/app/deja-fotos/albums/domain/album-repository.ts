/*
 * Deja Fotos
 *
 * Album Repository
 */

import {
  Album,
  AlbumFilters,
  AlbumInput,
  AlbumPeriod,
  AlbumPeriodDescriptionInput,
} from './album';

export interface AlbumRepository {
  list(
    filters?: AlbumFilters,
  ): Promise<readonly Album[]>;

  findById(
    id: string,
  ): Promise<Album | undefined>;

  listPeriods(
    albumId: string,
  ): Promise<readonly AlbumPeriod[]>;

  updatePeriodDescription(
    albumId: string,
    year: number,
    month: number,
    input: AlbumPeriodDescriptionInput,
  ): Promise<AlbumPeriod>;

  create(
    input: AlbumInput,
  ): Promise<Album>;

  update(
    id: string,
    input: AlbumInput,
  ): Promise<Album>;

  delete(
    id: string,
  ): Promise<void>;
}