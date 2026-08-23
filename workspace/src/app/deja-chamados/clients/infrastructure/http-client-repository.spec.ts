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
  ClientInput,
} from '../domain';

import {
  HttpClientRepository,
} from './http-client-repository';

describe('HttpClientRepository', () => {

  let repository: HttpClientRepository;
  let httpTesting: HttpTestingController;

  const organizationId =
    '11111111-1111-1111-1111-111111111111';

  const tenantId =
    '22222222-2222-2222-2222-222222222222';

  const environmentId =
    '33333333-3333-3333-3333-333333333333';

  const clientResponse = {
    id: '44444444-4444-4444-4444-444444444444',
    organization_id: organizationId,
    tenant_id: tenantId,
    environment_id: environmentId,
    company_name: 'Cliente Demonstração Ltda.',
    fantasy_name: 'Cliente Demonstração',
    document: '12345678000195',
    contact_name: 'Maria da Silva',
    phone: '5432223344',
    whatsapp: '54999887766',
    email: 'contato@example.com',
    city: 'Caxias do Sul',
    state: 'RS',
    notes: 'Cliente prioritário.',
    active: true,
    created_at: '2026-08-23T10:00:00',
    updated_at: '2026-08-23T10:00:00',
    total_tickets: 3,
  };

  const input: ClientInput = {
    environmentId,
    companyName: ' Cliente Teste Ltda. ',
    fantasyName: ' Cliente Teste ',
    document: '12.345.678/0001-96',
    contactName: ' João da Silva ',
    phone: ' (54) 3222-4455 ',
    whatsapp: ' (54) 99988-7766 ',
    email: ' TESTE@EXAMPLE.COM ',
    city: ' Caxias do Sul ',
    state: ' rs ',
    notes: ' Observação de teste. ',
    active: true,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpClientRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should list and map clients using filters', async () => {
    const resultPromise = repository.list({
      organizationId,
      tenantId,
      environmentId,
      search: 'Demonstração',
      active: false,
    });

    const request = httpTesting.expectOne(candidate =>
      candidate.url === '/api/chamados/clients'
      && candidate.params.get('organization_id')
        === organizationId
      && candidate.params.get('tenant_id') === tenantId
      && candidate.params.get('environment_id')
        === environmentId
      && candidate.params.get('search') === 'Demonstração'
      && candidate.params.get('active') === 'false',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      clientResponse,
    ]);

    await expect(resultPromise).resolves.toEqual([
      {
        id: clientResponse.id,
        organizationId,
        tenantId,
        environmentId,
        companyName: clientResponse.company_name,
        fantasyName: clientResponse.fantasy_name,
        document: clientResponse.document,
        contactName: clientResponse.contact_name,
        phone: clientResponse.phone,
        whatsapp: clientResponse.whatsapp,
        email: clientResponse.email,
        city: clientResponse.city,
        state: clientResponse.state,
        notes: clientResponse.notes,
        active: clientResponse.active,
        createdAt: clientResponse.created_at,
        updatedAt: clientResponse.updated_at,
        totalTickets: clientResponse.total_tickets,
      },
    ]);
  });

  it('should find a client by id', async () => {
    const resultPromise = repository.findById(
      clientResponse.id,
    );

    const request = httpTesting.expectOne(
      `/api/chamados/clients/${clientResponse.id}`,
    );

    expect(request.request.method).toBe('GET');

    request.flush(clientResponse);

    await expect(resultPromise).resolves.toMatchObject({
      id: clientResponse.id,
      organizationId,
      tenantId,
      environmentId,
      companyName: clientResponse.company_name,
      totalTickets: clientResponse.total_tickets,
    });
  });

  it('should return undefined when a client is not found', async () => {
    const resultPromise = repository.findById(
      clientResponse.id,
    );

    const request = httpTesting.expectOne(
      `/api/chamados/clients/${clientResponse.id}`,
    );

    request.flush(
      {
        detail: 'Cliente não encontrado.',
      },
      {
        status: 404,
        statusText: 'Not Found',
      },
    );

    await expect(resultPromise).resolves.toBeUndefined();
  });

  it('should normalize and create a client', async () => {
    const resultPromise = repository.create(input);

    const request = httpTesting.expectOne(
      '/api/chamados/clients',
    );

    expect(request.request.method).toBe('POST');

    expect(request.request.body).toEqual({
      environment_id: environmentId,
      company_name: 'Cliente Teste Ltda.',
      fantasy_name: 'Cliente Teste',
      document: '12345678000196',
      contact_name: 'João da Silva',
      phone: '5432224455',
      whatsapp: '54999887766',
      email: 'teste@example.com',
      city: 'Caxias do Sul',
      state: 'RS',
      notes: 'Observação de teste.',
      active: true,
    });

    request.flush({
      ...clientResponse,
      company_name: 'Cliente Teste Ltda.',
      fantasy_name: 'Cliente Teste',
      document: '12345678000196',
      contact_name: 'João da Silva',
      phone: '5432224455',
      whatsapp: '54999887766',
      email: 'teste@example.com',
      notes: 'Observação de teste.',
    });

    await expect(resultPromise).resolves.toMatchObject({
      environmentId,
      companyName: 'Cliente Teste Ltda.',
      fantasyName: 'Cliente Teste',
      document: '12345678000196',
      contactName: 'João da Silva',
      email: 'teste@example.com',
    });
  });

  it('should update and delete a client', async () => {
    const updatePromise = repository.update(
      clientResponse.id,
      input,
    );

    const updateRequest = httpTesting.expectOne(
      `/api/chamados/clients/${clientResponse.id}`,
    );

    expect(updateRequest.request.method).toBe('PUT');

    updateRequest.flush({
      ...clientResponse,
      company_name: 'Cliente Teste Ltda.',
      fantasy_name: 'Cliente Teste',
      document: '12345678000196',
      contact_name: 'João da Silva',
      phone: '5432224455',
      whatsapp: '54999887766',
      email: 'teste@example.com',
      notes: 'Observação de teste.',
    });

    await updatePromise;

    const deletePromise = repository.delete(
      clientResponse.id,
    );

    const deleteRequest = httpTesting.expectOne(
      `/api/chamados/clients/${clientResponse.id}`,
    );

    expect(deleteRequest.request.method).toBe('DELETE');

    deleteRequest.flush(null);

    await expect(deletePromise).resolves.toBeUndefined();
  });

});