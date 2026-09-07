import { HttpClient, provideHttpClient } from '@angular/common/http';

import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { TestBed } from '@angular/core/testing';

import { HttpTicketTimelineRepository } from './http-ticket-timeline-repository';

describe('HttpTicketTimelineRepository', () => {
  let repository: HttpTicketTimelineRepository;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    repository = new HttpTicketTimelineRepository(TestBed.inject(HttpClient));

    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('lista e converte o histórico de um chamado', async () => {
    const promise = repository.listByTicketId('c844b26e-0680-43ef-8178-d609903384ba');

    const request = http.expectOne(
      '/api/chamados/tickets/c844b26e-0680-43ef-8178-d609903384ba/timeline',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      {
        id: '01a07da2-aee4-761a-b105-6a3ba1433db7',
        ticket_id: 'c844b26e-0680-43ef-8178-d609903384ba',
        event_type: 'status_changed',
        description: 'Status do chamado alterado.',
        previous_value: 'pending',
        new_value: 'in_progress',
        created_by_user_id: '307b6395-5e91-466f-b686-919b94cb5f82',
        created_at: '2026-09-07T17:50:08',
      },
    ]);

    await expect(promise).resolves.toEqual([
      {
        id: '01a07da2-aee4-761a-b105-6a3ba1433db7',
        ticketId: 'c844b26e-0680-43ef-8178-d609903384ba',
        eventType: 'status_changed',
        description: 'Status do chamado alterado.',
        previousValue: 'pending',
        newValue: 'in_progress',
        createdByUserId: '307b6395-5e91-466f-b686-919b94cb5f82',
        createdAt: '2026-09-07T17:50:08',
      },
    ]);
  });
});
