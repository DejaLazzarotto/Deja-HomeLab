/*
 * Deja Indicadores
 *
 * Indicators Domain
 *
 * Validação e normalização dos dados de indicadores.
 */

import {
  IndicatorInput,
} from './indicator-input';

import {
  InvalidIndicatorError,
} from './invalid-indicator.error';

export class IndicatorValidator {

  validate(
    input: IndicatorInput,
  ): IndicatorInput {
    const companyId = input.companyId.trim();
    const name = input.name.trim();
    const description = input.description.trim();
    const unit = input.unit.trim();

    if (companyId.length !== 36) {
      throw new InvalidIndicatorError(
        'Selecione uma empresa válida.',
      );
    }

    if (!name || name.length > 255) {
      throw new InvalidIndicatorError(
        'Informe um nome válido com até 255 caracteres.',
      );
    }

    if (!unit || unit.length > 50) {
      throw new InvalidIndicatorError(
        'Informe uma unidade válida com até 50 caracteres.',
      );
    }

    if (!Number.isFinite(input.targetValue)) {
      throw new InvalidIndicatorError(
        'Informe uma meta válida.',
      );
    }

    if (
      input.direction !== 'higher_is_better'
      && input.direction !== 'lower_is_better'
    ) {
      throw new InvalidIndicatorError(
        'Informe uma direção válida.',
      );
    }

    if (
      input.status !== 'active'
      && input.status !== 'inactive'
    ) {
      throw new InvalidIndicatorError(
        'Informe um status válido.',
      );
    }

    return {
      companyId,
      name,
      description,
      unit,
      direction: input.direction,
      targetValue: input.targetValue,
      status: input.status,
    };
  }

}