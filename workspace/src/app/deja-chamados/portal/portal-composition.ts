import {
  HttpClient,
} from '@angular/common/http';

import {
  PortalTicketService,
} from './application/portal-ticket-service';

import {
  HttpPortalTicketRepository,
} from './infrastructure/http-portal-ticket-repository';

export class PortalComposition {

  private readonly repository:
    HttpPortalTicketRepository;

  readonly service:
    PortalTicketService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpPortalTicketRepository(
        http,
      );

    this.service =
      new PortalTicketService(
        this.repository,
      );
  }

}