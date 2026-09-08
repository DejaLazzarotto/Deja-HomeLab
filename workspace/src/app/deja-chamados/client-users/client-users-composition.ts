import {
  HttpClient,
} from '@angular/common/http';

import {
  ClientUserLinkService,
} from './application/client-user-link-service';

import {
  HttpClientUserLinkRepository,
} from './infrastructure/http-client-user-link-repository';

export class ClientUsersComposition {

  private readonly repository:
    HttpClientUserLinkRepository;

  readonly service:
    ClientUserLinkService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpClientUserLinkRepository(
        http,
      );

    this.service =
      new ClientUserLinkService(
        this.repository,
      );
  }

}