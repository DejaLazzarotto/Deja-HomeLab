/*
 * Deja Fotos
 *
 * Album Repository
 */

import {
  Album,
  AlbumFilters,
  AlbumInput,
} from './album';

export interface AlbumRepository {
  list(
    filters?: AlbumFilters,
  ): Promise<readonly Album[]>;

  findById(
    id: string,
  ): Promise<Album | undefined>;

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