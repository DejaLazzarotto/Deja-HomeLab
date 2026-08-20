/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Dados utilizados na criação e atualização de medições.
 */

export interface MeasurementInput {
  readonly indicatorId: string;
  readonly referenceDate: string;
  readonly actualValue: number;
  readonly observation: string;
}