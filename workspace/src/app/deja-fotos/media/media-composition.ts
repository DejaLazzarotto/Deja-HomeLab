/*
 * Deja Fotos
 *
 * Media Composition
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  MediaService,
} from './application';

import {
  HttpMediaRepository,
} from './infrastructure';

export class MediaComposition {
  readonly service: MediaService;

  constructor(
    http: HttpClient,
  ) {
    const repository = new HttpMediaRepository(http);

    this.service = new MediaService(repository);
  }
}