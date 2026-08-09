/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Contrato institucional de persistência e consulta de empresas.
 */

import {
  Company,
} from './company';

import {
  CompanyInput,
} from './company-input';

export interface CompanyRepository {
  list(): readonly Company[];
  findById(id: string): Company | undefined;
  create(input: CompanyInput): Company;
  update(id: string, input: CompanyInput): Company;
  delete(id: string): void;
}