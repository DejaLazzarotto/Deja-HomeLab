/*
 * Deja Indicadores
 *
 * Measurements Composition
 *
 * Composição das dependências da Coleta Manual.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  MeasurementService,
} from './application';

import {
  HttpMeasurementRepository,
} from './infrastructure';

export class MeasurementsComposition {

  private readonly repository:
    HttpMeasurementRepository;

  readonly service: MeasurementService;

  constructor(
    http: HttpClient,
  ) {
    this.repository =
      new HttpMeasurementRepository(http);

    this.service =
      new MeasurementService(this.repository);
  }

}