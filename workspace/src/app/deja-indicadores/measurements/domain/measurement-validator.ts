/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Validação e normalização dos dados de medições.
 */

import {
  InvalidMeasurementError,
} from './invalid-measurement.error';

import {
  MeasurementInput,
} from './measurement-input';

export class MeasurementValidator {

  validate(
    input: MeasurementInput,
  ): MeasurementInput {
    const indicatorId = input.indicatorId.trim();
    const referenceDate = input.referenceDate.trim();
    const observation = input.observation.trim();

    if (indicatorId.length !== 36) {
      throw new InvalidMeasurementError(
        'Selecione um indicador válido.',
      );
    }

    if (!this.isValidDate(referenceDate)) {
      throw new InvalidMeasurementError(
        'Informe uma data de referência válida.',
      );
    }

    if (!Number.isFinite(input.actualValue)) {
      throw new InvalidMeasurementError(
        'Informe um valor realizado válido.',
      );
    }

    return {
      indicatorId,
      referenceDate,
      actualValue: input.actualValue,
      observation,
    };
  }

  private isValidDate(
    value: string,
  ): boolean {
    const match =
      /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);

    if (!match) {
      return false;
    }

    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const date = new Date(
      Date.UTC(year, month - 1, day),
    );

    return (
      date.getUTCFullYear() === year
      && date.getUTCMonth() === month - 1
      && date.getUTCDate() === day
    );
  }

}