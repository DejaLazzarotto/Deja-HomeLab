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
  list(): Promise<readonly Company[]>;
  findById(id: string): Promise<Company | undefined>;
  create(input: CompanyInput): Promise<Company>;
  update(id: string, input: CompanyInput): Promise<Company>;
  delete(id: string): Promise<void>;
}