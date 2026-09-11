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
  TicketCommentCreateInput,
} from '../domain';

import {
  HttpTicketCommentRepository,
} from './http-ticket-comment-repository';

describe('HttpTicketCommentRepository', () => {
  let repository: HttpTicketCommentRepository;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository = new HttpTicketCommentRepository(
      TestBed.inject(HttpClient),
    );

    httpTesting = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('deve listar comentários administrativos do chamado', async () => {
    const promise = repository.listByTicketId(
      'ticket-1',
    );

    const request = httpTesting.expectOne(
      '/api/chamados/tickets/ticket-1/comments',
    );

    expect(request.request.method).toBe('GET');

    request.flush([
      {
        id: 'comment-1',
        ticket_id: 'ticket-1',
        content: 'Comentário público.',
        visibility: 'public',
        created_by_user_id: 'user-1',
        created_by: 'Administrador',
        created_at: '2026-09-11T10:00:00',
      },
      {
        id: 'comment-2',
        ticket_id: 'ticket-1',
        content: 'Comentário interno.',
        visibility: 'internal',
        created_by_user_id: 'user-2',
        created_by: 'Analista',
        created_at: '2026-09-11T10:05:00',
      },
    ]);

    const comments = await promise;

    expect(comments).toEqual([
      {
        id: 'comment-1',
        ticketId: 'ticket-1',
        content: 'Comentário público.',
        visibility: 'public',
        createdByUserId: 'user-1',
        createdBy: 'Administrador',
        createdAt: '2026-09-11T10:00:00',
      },
      {
        id: 'comment-2',
        ticketId: 'ticket-1',
        content: 'Comentário interno.',
        visibility: 'internal',
        createdByUserId: 'user-2',
        createdBy: 'Analista',
        createdAt: '2026-09-11T10:05:00',
      },
    ]);
  });

  it('deve criar comentário administrativo com visibilidade', async () => {
    const input: TicketCommentCreateInput = {
      content: 'Observação da equipe.',
      visibility: 'internal',
    };

    const promise = repository.create(
      'ticket-1',
      input,
    );

    const request = httpTesting.expectOne(
      '/api/chamados/tickets/ticket-1/comments',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      content: 'Observação da equipe.',
      visibility: 'internal',
    });

    request.flush({
      id: 'comment-3',
      ticket_id: 'ticket-1',
      content: 'Observação da equipe.',
      visibility: 'internal',
      created_by_user_id: 'user-1',
      created_by: 'Administrador',
      created_at: '2026-09-11T10:10:00',
    });

    const comment = await promise;

    expect(comment).toEqual({
      id: 'comment-3',
      ticketId: 'ticket-1',
      content: 'Observação da equipe.',
      visibility: 'internal',
      createdByUserId: 'user-1',
      createdBy: 'Administrador',
      createdAt: '2026-09-11T10:10:00',
    });
  });
});