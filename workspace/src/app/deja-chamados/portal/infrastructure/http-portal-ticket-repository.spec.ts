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
  HttpPortalTicketRepository,
} from './http-portal-ticket-repository';

describe('HttpPortalTicketRepository', () => {

  let repository: HttpPortalTicketRepository;

  let httpTesting:
    HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    repository =
      new HttpPortalTicketRepository(
        TestBed.inject(HttpClient),
      );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it(
    'deve listar os chamados do Portal',
    async () => {
      const promise =
        repository.list();

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush([
        {
          id: 'ticket-1',
          title: 'Erro de acesso',
          description: 'Não consigo acessar.',
          status: 'open',
          priority: 'medium',
          assigned_to_user_name: null,
          closed_at: null,
          created_at: '2026-09-08T10:00:00',
          updated_at: '2026-09-08T10:00:00',
        },
      ]);

      await expect(promise)
        .resolves
        .toEqual([
          {
            id: 'ticket-1',
            title: 'Erro de acesso',
            description: 'Não consigo acessar.',
            status: 'open',
            priority: 'medium',
            assignedToUserName: null,
            closedAt: null,
            createdAt: '2026-09-08T10:00:00',
            updatedAt: '2026-09-08T10:00:00',
          },
        ]);
    },
  );

  it(
    'deve consultar um chamado por id',
    async () => {
      const promise =
        repository.findById(
          'ticket-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets/ticket-1',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush({
        id: 'ticket-1',
        title: 'Falha no sistema',
        description: 'Sistema indisponível.',
        status: 'in_progress',
        priority: 'medium',
        assigned_to_user_name: 'Analista Deja',
        closed_at: null,
        created_at: '2026-09-08T10:00:00',
        updated_at: '2026-09-08T11:00:00',
      });

      await expect(promise)
        .resolves
        .toEqual({
          id: 'ticket-1',
          title: 'Falha no sistema',
          description: 'Sistema indisponível.',
          status: 'in_progress',
          priority: 'medium',
          assignedToUserName: 'Analista Deja',
          closedAt: null,
          createdAt: '2026-09-08T10:00:00',
          updatedAt: '2026-09-08T11:00:00',
        });
    },
  );

  it(
    'deve retornar undefined quando o chamado não existir',
    async () => {
      const promise =
        repository.findById(
          'ticket-inexistente',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets/ticket-inexistente',
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

      await expect(promise)
        .resolves
        .toBeUndefined();
    },
  );

  it(
    'deve listar a timeline de um chamado do Portal',
    async () => {
      const promise =
        repository.listTimeline(
          'ticket-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets/ticket-1/timeline',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush([
        {
          id: 'event-1',
          event_type: 'created',
          description: 'Chamado criado pelo Portal.',
          previous_value: null,
          new_value: 'created',
          created_at: '2026-09-10T10:30:00',
        },
        {
          id: 'event-2',
          event_type: 'status_changed',
          description: 'Status do chamado alterado.',
          previous_value: 'open',
          new_value: 'in_progress',
          created_at: '2026-09-10T11:00:00',
        },
      ]);

      await expect(promise)
        .resolves
        .toEqual([
          {
            id: 'event-1',
            eventType: 'created',
            description: 'Chamado criado pelo Portal.',
            previousValue: null,
            newValue: 'created',
            createdAt: '2026-09-10T10:30:00',
          },
          {
            id: 'event-2',
            eventType: 'status_changed',
            description: 'Status do chamado alterado.',
            previousValue: 'open',
            newValue: 'in_progress',
            createdAt: '2026-09-10T11:00:00',
          },
        ]);
    },
  );

  it(
    'deve listar os comentários de um chamado do Portal',
    async () => {
      const promise =
        repository.listComments(
          'ticket-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets/ticket-1/comments',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush([
        {
          id: 'comment-1',
          content: 'Comentário do cliente.',
          created_by: 'Cliente Portal',
          created_at: '2026-09-10T11:30:00',
        },
        {
          id: 'comment-2',
          content: 'Resposta pública da equipe.',
          created_by: 'Analista',
          created_at: '2026-09-10T12:00:00',
        },
      ]);

      await expect(promise)
        .resolves
        .toEqual([
          {
            id: 'comment-1',
            content: 'Comentário do cliente.',
            createdBy: 'Cliente Portal',
            createdAt: '2026-09-10T11:30:00',
          },
          {
            id: 'comment-2',
            content: 'Resposta pública da equipe.',
            createdBy: 'Analista',
            createdAt: '2026-09-10T12:00:00',
          },
        ]);
    },
  );

  it(
    'deve criar comentário público no chamado do Portal',
    async () => {
      const promise =
        repository.createComment(
          'ticket-1',
          {
            content: 'Novo comentário.',
          },
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets/ticket-1/comments',
        );

      expect(request.request.method)
        .toBe('POST');

      expect(request.request.body)
        .toEqual({
          content: 'Novo comentário.',
        });

      request.flush({
        id: 'comment-3',
        content: 'Novo comentário.',
        created_by: 'Cliente Portal',
        created_at: '2026-09-10T12:30:00',
      });

      await expect(promise)
        .resolves
        .toEqual({
          id: 'comment-3',
          content: 'Novo comentário.',
          createdBy: 'Cliente Portal',
          createdAt: '2026-09-10T12:30:00',
        });
    },
  );

  it(
    'deve abrir um chamado enviando apenas título e descrição',
    async () => {
      const promise =
        repository.create({
          title: 'Novo chamado',
          description: 'Descrição do problema.',
        });

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets',
        );

      expect(request.request.method)
        .toBe('POST');

      expect(request.request.body)
        .toEqual({
          title: 'Novo chamado',
          description: 'Descrição do problema.',
        });

      request.flush({
        id: 'ticket-2',
        title: 'Novo chamado',
        description: 'Descrição do problema.',
        status: 'open',
        priority: 'medium',
        assigned_to_user_name: null,
        closed_at: null,
        created_at: '2026-09-08T12:00:00',
        updated_at: '2026-09-08T12:00:00',
      });

      await expect(promise)
        .resolves
        .toEqual({
          id: 'ticket-2',
          title: 'Novo chamado',
          description: 'Descrição do problema.',
          status: 'open',
          priority: 'medium',
          assignedToUserName: null,
          closedAt: null,
          createdAt: '2026-09-08T12:00:00',
          updatedAt: '2026-09-08T12:00:00',
        });
    },
  );


  it(
    'deve listar os anexos de um chamado do Portal',
    async () => {
      const promise =
        repository.listAttachments(
          'ticket-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/tickets/ticket-1/attachments',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush([
        {
          id: 'attachment-1',
          original_name: 'evidencia.png',
          content_type: 'image/png',
          file_size: 2048,
          created_by: 'Analista Deja',
          created_at: '2026-09-12T15:00:00',
        },
      ]);

      await expect(promise)
        .resolves
        .toEqual([
          {
            id: 'attachment-1',
            originalName: 'evidencia.png',
            contentType: 'image/png',
            fileSize: 2048,
            createdBy: 'Analista Deja',
            createdAt: '2026-09-12T15:00:00',
          },
        ]);
    },
  );

  it(
    'deve baixar um anexo do Portal como Blob',
    async () => {
      const promise =
        repository.downloadAttachment(
          'attachment-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/portal/attachments/attachment-1/download',
        );

      expect(request.request.method)
        .toBe('GET');

      expect(request.request.responseType)
        .toBe('blob');

      const blob = new Blob(
        ['conteudo'],
        {
          type: 'application/pdf',
        },
      );

      request.flush(blob);

      await expect(promise)
        .resolves
        .toBeInstanceOf(Blob);
    },
  );

});