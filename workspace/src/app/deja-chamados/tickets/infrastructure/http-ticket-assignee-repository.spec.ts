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
  HttpTicketAssigneeRepository,
} from './http-ticket-assignee-repository';

describe('HttpTicketAssigneeRepository', () => {

  let repository: HttpTicketAssigneeRepository;
  let httpTesting: HttpTestingController;

  const clientId =
    '44444444-4444-4444-8444-444444444444';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpTicketAssigneeRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('lista responsáveis elegíveis pelo Cliente', async () => {
    const promise = repository.list(clientId);

    const request = httpTesting.expectOne(
      requestCandidate =>
        requestCandidate.url
          === '/api/chamados/tickets/assignees',
    );

    expect(request.request.method).toBe('GET');

    expect(
      request.request.params.get('client_id'),
    ).toBe(clientId);

    request.flush([
      {
        id: '55555555-5555-4555-8555-555555555555',
        name: 'Analista Responsável',
        email: 'analista@deja.com',
        role: 'analyst',
      },
    ]);

    await expect(promise).resolves.toEqual([
      {
        id: '55555555-5555-4555-8555-555555555555',
        name: 'Analista Responsável',
        email: 'analista@deja.com',
        role: 'analyst',
      },
    ]);
  });

});