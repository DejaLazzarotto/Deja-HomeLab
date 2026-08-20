/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Modelo institucional de medição coletada manualmente.
 */

export interface Measurement {
  readonly id: string;
  readonly indicatorId: string;
  readonly referenceDate: string;
  readonly actualValue: number;
  readonly observation: string;
  readonly createdBy: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}