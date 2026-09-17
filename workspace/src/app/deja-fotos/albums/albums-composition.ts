/*
 * Deja Fotos
 *
 * Albums Composition
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  AlbumService,
} from './application';

import {
  HttpAlbumRepository,
} from './infrastructure';

export class AlbumsComposition {
  readonly service: AlbumService;

  constructor(
    http: HttpClient,
  ) {
    const repository = new HttpAlbumRepository(http);

    this.service = new AlbumService(repository);
  }
}