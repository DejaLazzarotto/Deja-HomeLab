/*
 * Deja Indicadores
 *
 * Companies Composition
 *
 * Composição das dependências da Gestão de Empresas.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  CompanyService,
} from './application';

import {
  HttpCompanyRepository,
} from './infrastructure';

export class CompaniesComposition {

  private readonly repository: HttpCompanyRepository;

  readonly service: CompanyService;

  constructor(
    http: HttpClient,
  ) {
    this.repository = new HttpCompanyRepository(
      http,
    );

    this.service = new CompanyService(
      this.repository,
    );
  }

}