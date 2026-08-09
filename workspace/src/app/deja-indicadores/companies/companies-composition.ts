/*
 * Deja Indicadores
 *
 * Companies Composition
 *
 * Composição das dependências da Gestão de Empresas.
 */

import {
  CompanyService,
} from './application';

import {
  InMemoryCompanyRepository,
} from './infrastructure';

export class CompaniesComposition {

  private readonly repository = new InMemoryCompanyRepository();

  readonly service = new CompanyService(
    this.repository,
  );

}