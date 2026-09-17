/*
 * Deja Fotos
 *
 * Album Application Service
 */

import {
  Album,
  AlbumFilters,
  AlbumInput,
  AlbumRepository,
  AlbumValidator,
} from '../domain';

export class AlbumService {
  private readonly validator = new AlbumValidator();

  constructor(
    private readonly repository: AlbumRepository,
  ) {}

  list(
    filters: AlbumFilters = {},
  ): Promise<readonly Album[]> {
    return this.repository.list(filters);
  }

  findById(
    id: string,
  ): Promise<Album | undefined> {
    return this.repository.findById(id);
  }

  create(
    input: AlbumInput,
  ): Promise<Album> {
    return this.repository.create(
      this.validator.validate(input),
    );
  }

  update(
    id: string,
    input: AlbumInput,
  ): Promise<Album> {
    return this.repository.update(
      id,
      this.validator.validate(input),
    );
  }

  delete(
    id: string,
  ): Promise<void> {
    return this.repository.delete(id);
  }
}