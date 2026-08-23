/*
 * Deja Chamados
 *
 * Clients Composition
 *
 * Composição das dependências da Gestão de Clientes.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  ClientService,
} from './application';

import {
  HttpClientRepository,
} from './infrastructure';

export class ClientsComposition {

  private readonly repository: HttpClientRepository;

  readonly service: ClientService;

  constructor(
    http: HttpClient,
  ) {
    this.repository = new HttpClientRepository(
      http,
    );

    this.service = new ClientService(
      this.repository,
    );
  }

}