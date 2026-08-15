/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Dados institucionais utilizados na criação e atualização de empresas.
 */

import {
  CompanyStatus,
} from './company';

export interface CompanyInput {
  readonly environmentId: string;
  readonly legalName: string;
  readonly tradeName: string;
  readonly document: string;
  readonly email: string;
  readonly phone: string;
  readonly status: CompanyStatus;
}