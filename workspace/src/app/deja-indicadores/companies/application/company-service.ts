/*
 * Deja Indicadores
 *
 * Companies Application
 *
 * Serviço de aplicação responsável por coordenar as operações
 * de consulta, criação, atualização e remoção de empresas.
 */

import {
  Company,
} from '../domain/company';

import {
  CompanyInput,
} from '../domain/company-input';

import {
  CompanyNotFoundError,
} from '../domain/company-not-found.error';

import {
  CompanyRepository,
} from '../domain/company-repository';

export class CompanyService {

  constructor(
    private readonly repository: CompanyRepository,
  ) {}

  list(): Promise<readonly Company[]> {
    return this.repository.list();
  }

  async findById(
    id: string,
  ): Promise<Company> {
    const company = await this.repository.findById(id);

    if (!company) {
      throw new CompanyNotFoundError(id);
    }

    return company;
  }

  create(
    input: CompanyInput,
  ): Promise<Company> {
    return this.repository.create(input);
  }

  update(
    id: string,
    input: CompanyInput,
  ): Promise<Company> {
    return this.repository.update(id, input);
  }

  delete(
    id: string,
  ): Promise<void> {
    return this.repository.delete(id);
  }

}