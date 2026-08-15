import {
  HttpClient,
  provideHttpClient,
} from '@angular/common/http';

import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import {
  TestBed,
} from '@angular/core/testing';

import {
  CompanyInput,
} from '../domain';

import {
  HttpCompanyRepository,
} from './http-company-repository';

describe('HttpCompanyRepository', () => {

  let repository: HttpCompanyRepository;
  let httpTesting: HttpTestingController;

  const environmentId =
    '11111111-1111-1111-1111-111111111111';

  const companyResponse = {
    id: '22222222-2222-2222-2222-222222222222',
    environment_id: environmentId,
    legal_name: 'Empresa Demonstração Ltda.',
    trade_name: 'Empresa Demonstração',
    document: '12345678000195',
    email: 'contato@example.com',
    phone: '(54) 99985-3226',
    status: 'active' as const,
    created_at: '2026-08-15T10:00:00',
    updated_at: '2026-08-15T10:00:00',
  };

  const input: CompanyInput = {
    environmentId,
    legalName: 'Empresa Teste Ltda.',
    tradeName: 'Empresa Teste',
    document: '12.345.678/0001-96',
    email: 'TESTE@EXAMPLE.COM',
    phone: ' (54) 99999-0000 ',
    status: 'active',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpCompanyRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should list and map companies from the API', async () => {
    const resultPromise = repository.list();

    const request =
      httpTesting.expectOne('/api/companies');

    expect(request.request.method).toBe('GET');

    request.flush([
      companyResponse,
    ]);

    await expect(resultPromise).resolves.toEqual([
      {
        id: companyResponse.id,
        environmentId,
        legalName: companyResponse.legal_name,
        tradeName: companyResponse.trade_name,
        document: companyResponse.document,
        email: companyResponse.email,
        phone: companyResponse.phone,
        status: companyResponse.status,
        createdAt: companyResponse.created_at,
        updatedAt: companyResponse.updated_at,
      },
    ]);
  });

  it('should normalize and create a company', async () => {
    const resultPromise = repository.create(input);

    const request =
      httpTesting.expectOne('/api/companies');

    expect(request.request.method).toBe('POST');

    expect(request.request.body).toEqual({
      environment_id: environmentId,
      legal_name: 'Empresa Teste Ltda.',
      trade_name: 'Empresa Teste',
      document: '12345678000196',
      email: 'teste@example.com',
      phone: '(54) 99999-0000',
      status: 'active',
    });

    request.flush({
      ...companyResponse,
      legal_name: 'Empresa Teste Ltda.',
      trade_name: 'Empresa Teste',
      document: '12345678000196',
      email: 'teste@example.com',
      phone: '(54) 99999-0000',
    });

    await expect(resultPromise).resolves.toMatchObject({
      environmentId,
      legalName: 'Empresa Teste Ltda.',
      tradeName: 'Empresa Teste',
      document: '12345678000196',
    });
  });

  it('should update and delete a company', async () => {
    const updatePromise = repository.update(
      companyResponse.id,
      input,
    );

    const updateRequest =
      httpTesting.expectOne(
        `/api/companies/${companyResponse.id}`,
      );

    expect(updateRequest.request.method).toBe('PUT');

    updateRequest.flush({
      ...companyResponse,
      legal_name: 'Empresa Teste Ltda.',
      trade_name: 'Empresa Teste',
      document: '12345678000196',
      email: 'teste@example.com',
      phone: '(54) 99999-0000',
    });

    await updatePromise;

    const deletePromise = repository.delete(
      companyResponse.id,
    );

    const deleteRequest =
      httpTesting.expectOne(
        `/api/companies/${companyResponse.id}`,
      );

    expect(deleteRequest.request.method).toBe('DELETE');

    deleteRequest.flush(null);

    await expect(deletePromise).resolves.toBeUndefined();
  });

});