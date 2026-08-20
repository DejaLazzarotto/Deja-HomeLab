/*
 * Deja Indicadores
 *
 * Indicators Composition
 *
 * Composição das dependências da Gestão de Indicadores.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  IndicatorService,
} from './application';

import {
  HttpIndicatorRepository,
} from './infrastructure';

export class IndicatorsComposition {

  private readonly repository:
    HttpIndicatorRepository;

  readonly service: IndicatorService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpIndicatorRepository(http);

    this.service =
      new IndicatorService(this.repository);
  }

}