/*
 * Deja Indicadores
 *
 * Users Composition
 *
 * Composição das dependências da Gestão de Usuários.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  UserService,
} from './application';

import {
  HttpUserRepository,
} from './infrastructure';

export class UsersComposition {

  private readonly repository: HttpUserRepository;

  readonly service: UserService;

  constructor(
    http: HttpClient,
  ) {
    this.repository = new HttpUserRepository(
      http,
    );

    this.service = new UserService(
      this.repository,
    );
  }

}