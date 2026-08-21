/*
 * Deja Indicadores
 *
 * Dashboards Composition
 *
 * Composição das dependências da visão gerencial.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  DashboardService,
} from './application';

import {
  HttpDashboardRepository,
} from './infrastructure';

export class DashboardsComposition {

  private readonly repository:
    HttpDashboardRepository;

  readonly service: DashboardService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpDashboardRepository(http);

    this.service =
      new DashboardService(this.repository);
  }

}