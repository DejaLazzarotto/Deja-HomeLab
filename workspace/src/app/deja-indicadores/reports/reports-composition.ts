/*
 * Deja Indicadores
 *
 * Reports Composition
 *
 * Composição das dependências dos relatórios gerenciais.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  ReportService,
} from './application';

import {
  HttpReportRepository,
} from './infrastructure';

export class ReportsComposition {

  private readonly repository:
    HttpReportRepository;

  readonly service: ReportService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpReportRepository(http);

    this.service =
      new ReportService(this.repository);
  }

}