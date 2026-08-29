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
  InvalidTicketError,
  TicketCreateInput,
} from '../domain';

import {
  HttpTicketRepository,
} from './http-ticket-repository';

describe('HttpTicketRepository', () => {

  let repository: HttpTicketRepository;
  let httpTesting: HttpTestingController;

  const organizationId =
    '11111111-1111-4111-8111-111111111111';

  const tenantId =
    '22222222-2222-4222-8222-222222222222';

  const environmentId =
    '33333333-3333-4333-8333-333333333333';

  const clientId =
    '44444444-4444-4444-8444-444444444444';

  const ticketId =
    '55555555-5555-4555-8555-555555555555';

  const openedByUserId =
    '66666666-6666-4666-8666-666666666666';

  const assignedToUserId =
    '77777777-7777-4777-8777-777777777777';

  const assignedToUserName = 'Analista de Chamados';

  const closedByUserId =
    '88888888-8888-4888-8888-888888888888';

  const ticketResponse = {
    id: ticketId,
    organization_id: organizationId,
    tenant_id: tenantId,
    environment_id: environmentId,
    client_id: clientId,
    title: 'Falha no acesso ao sistema',
    description: 'Usuário não consegue acessar o sistema.',
    status: 'open' as const,
    priority: 'high' as const,
    opened_by_user_id: openedByUserId,
    assigned_to_user_id: assignedToUserId,
    assigned_to_user_name: assignedToUserName,
    closed_by_user_id: null,
    closed_at: null,
    created_at: '2026-08-28T10:00:00',
    updated_at: '2026-08-28T10:00:00',
  };

  const input: TicketCreateInput = {
    environmentId,
    clientId,
    title: ' Falha no acesso ao sistema ',
    description: ' Usuário não consegue acessar o sistema. ',
    priority: 'high',
    assignedToUserId,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    const http = TestBed.inject(HttpClient);

    httpTesting = TestBed.inject(
      HttpTestingController,
    );

    repository = new HttpTicketRepository(http);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('lista e converte chamados da API', async () => {
    const promise = repository.list();

    const request = httpTesting.expectOne(
      '/api/chamados/tickets',
    );

    expect(request.request.method).toBe('GET');

    request.flush([ticketResponse]);

    await expect(promise).resolves.toEqual([
      {
        id: ticketId,
        organizationId,
        tenantId,
        environmentId,
        clientId,
        title: 'Falha no acesso ao sistema',
        description:
          'Usuário não consegue acessar o sistema.',
        status: 'open',
        priority: 'high',
        openedByUserId,
        assignedToUserId,
        assignedToUserName,
        closedByUserId: null,
        closedAt: null,
        createdAt: '2026-08-28T10:00:00',
        updatedAt: '2026-08-28T10:00:00',
      },
    ]);
  });

  it('envia todos os filtros da listagem', async () => {
    const promise = repository.list({
      organizationId,
      tenantId,
      environmentId,
      clientId,
      status: 'in_progress',
      priority: 'critical',
      assignedToUserId,
      search: ' falha crítica ',
    });

    const request = httpTesting.expectOne(
      requestCandidate =>
        requestCandidate.url === '/api/chamados/tickets',
    );

    expect(
      request.request.params.get('organization_id'),
    ).toBe(organizationId);

    expect(
      request.request.params.get('tenant_id'),
    ).toBe(tenantId);

    expect(
      request.request.params.get('environment_id'),
    ).toBe(environmentId);

    expect(
      request.request.params.get('client_id'),
    ).toBe(clientId);

    expect(
      request.request.params.get('status'),
    ).toBe('in_progress');

    expect(
      request.request.params.get('priority'),
    ).toBe('critical');

    expect(
      request.request.params.get('assigned_to_user_id'),
    ).toBe(assignedToUserId);

    expect(
      request.request.params.get('search'),
    ).toBe('falha crítica');

    request.flush([]);

    await expect(promise).resolves.toEqual([]);
  });

  it('consulta um chamado pelo identificador', async () => {
    const promise = repository.findById(ticketId);

    const request = httpTesting.expectOne(
      `/api/chamados/tickets/${ticketId}`,
    );

    expect(request.request.method).toBe('GET');

    request.flush(ticketResponse);

    const ticket = await promise;

    expect(ticket?.id).toBe(ticketId);
    expect(ticket?.clientId).toBe(clientId);
  });

  it('retorna undefined quando o chamado não existe', async () => {
    const promise = repository.findById(ticketId);

    const request = httpTesting.expectOne(
      `/api/chamados/tickets/${ticketId}`,
    );

    request.flush(
      {
        detail: 'Chamado não encontrado.',
      },
      {
        status: 404,
        statusText: 'Not Found',
      },
    );

    await expect(promise).resolves.toBeUndefined();
  });

  it('propaga erros diferentes de recurso inexistente', async () => {
    const promise = repository.findById(ticketId);

    const request = httpTesting.expectOne(
      `/api/chamados/tickets/${ticketId}`,
    );

    request.flush(
      {
        detail: 'Erro interno.',
      },
      {
        status: 500,
        statusText: 'Internal Server Error',
      },
    );

    await expect(promise).rejects.toBeDefined();
  });

  it('abre um chamado com dados normalizados', async () => {
    const promise = repository.create(input);

    const request = httpTesting.expectOne(
      '/api/chamados/tickets',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      environment_id: environmentId,
      client_id: clientId,
      title: 'Falha no acesso ao sistema',
      description:
        'Usuário não consegue acessar o sistema.',
      priority: 'high',
      assigned_to_user_id: assignedToUserId,
    });

    request.flush(ticketResponse);

    await expect(promise).resolves.toBeDefined();
  });

  it('abre um chamado sem responsável', async () => {
    const promise = repository.create({
      ...input,
      assignedToUserId: null,
    });

    const request = httpTesting.expectOne(
      '/api/chamados/tickets',
    );

    expect(
      request.request.body.assigned_to_user_id,
    ).toBeNull();

    request.flush({
      ...ticketResponse,
      assigned_to_user_id: null,
      assigned_to_user_name: null,
    });

    await expect(promise).resolves.toBeDefined();
  });

  it('atualiza os dados operacionais do chamado', async () => {
    const promise = repository.update(
      ticketId,
      {
        title: ' Falha crítica ',
        description: ' Serviço indisponível. ',
        priority: 'critical',
        assignedToUserId: null,
      },
    );

    const request = httpTesting.expectOne(
      `/api/chamados/tickets/${ticketId}`,
    );

    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual({
      title: 'Falha crítica',
      description: 'Serviço indisponível.',
      priority: 'critical',
      assigned_to_user_id: null,
    });

    request.flush({
      ...ticketResponse,
      title: 'Falha crítica',
      description: 'Serviço indisponível.',
      priority: 'critical',
      assigned_to_user_id: null,
      assigned_to_user_name: null,
    });

    await expect(promise).resolves.toBeDefined();
  });

  it('altera o status pelo endpoint próprio', async () => {
    const promise = repository.updateStatus(
      ticketId,
      {
        status: 'closed',
      },
    );

    const request = httpTesting.expectOne(
      `/api/chamados/tickets/${ticketId}/status`,
    );

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual({
      status: 'closed',
    });

    request.flush({
      ...ticketResponse,
      status: 'closed',
      closed_by_user_id: closedByUserId,
      closed_at: '2026-08-28T11:00:00',
    });

    const ticket = await promise;

    expect(ticket.status).toBe('closed');
    expect(ticket.closedByUserId).toBe(closedByUserId);
    expect(ticket.closedAt).toBe(
      '2026-08-28T11:00:00',
    );
  });

  it('rejeita a abertura antes da chamada HTTP', async () => {
    await expect(
      repository.create({
        ...input,
        title: '   ',
      }),
    ).rejects.toBeInstanceOf(InvalidTicketError);

    httpTesting.expectNone('/api/chamados/tickets');
  });

  it('rejeita status inválido antes da chamada HTTP', async () => {
    await expect(
      repository.updateStatus(
        ticketId,
        {
          status: 'cancelled' as never,
        },
      ),
    ).rejects.toBeInstanceOf(InvalidTicketError);

    httpTesting.expectNone(
      `/api/chamados/tickets/${ticketId}/status`,
    );
  });

});