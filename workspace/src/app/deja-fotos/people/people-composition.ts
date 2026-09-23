/*
 * Deja Fotos
 *
 * Composição do domínio Pessoas.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  PersonService,
} from './application/person-service';

import {
  HttpPersonRepository,
} from './infrastructure/http-person-repository';

export class PeopleComposition {
  readonly service: PersonService;

  constructor(http: HttpClient) {
    this.service = new PersonService(
      new HttpPersonRepository(http),
    );
  }
}