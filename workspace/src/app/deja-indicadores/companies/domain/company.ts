/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Modelo institucional de empresa cliente gerenciada pelo produto.
 */

export type CompanyStatus =
  | 'active'
  | 'inactive';

export interface Company {
  readonly id: string;
  readonly legalName: string;
  readonly tradeName: string;
  readonly document: string;
  readonly email: string;
  readonly phone: string;
  readonly status: CompanyStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}