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
  HttpTicketAttachmentRepository,
} from './http-ticket-attachment-repository';

describe('HttpTicketAttachmentRepository', () => {

  let repository: HttpTicketAttachmentRepository;

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
      new HttpTicketAttachmentRepository(
        TestBed.inject(HttpClient),
      );

    httpTesting =
      TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it(
    'deve listar os anexos de um chamado',
    async () => {
      const promise =
        repository.listByTicketId(
          'ticket-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/tickets/ticket-1/attachments',
        );

      expect(request.request.method)
        .toBe('GET');

      request.flush([
        {
          id: 'attachment-1',
          ticket_id: 'ticket-1',
          original_name: 'evidencia.png',
          content_type: 'image/png',
          file_size: 2048,
          created_by_user_id: 'user-1',
          created_by: 'Analista Deja',
          created_at: '2026-09-12T15:00:00',
        },
      ]);

      await expect(promise)
        .resolves
        .toEqual([
          {
            id: 'attachment-1',
            ticketId: 'ticket-1',
            originalName: 'evidencia.png',
            contentType: 'image/png',
            fileSize: 2048,
            createdByUserId: 'user-1',
            createdBy: 'Analista Deja',
            createdAt: '2026-09-12T15:00:00',
          },
        ]);
    },
  );

  it(
    'deve enviar um anexo usando multipart form data',
    async () => {
      const file = new File(
        ['conteudo'],
        'evidencia.png',
        {
          type: 'image/png',
        },
      );

      const promise =
        repository.upload(
          'ticket-1',
          file,
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/tickets/ticket-1/attachments',
        );

      expect(request.request.method)
        .toBe('POST');

      expect(request.request.body)
        .toBeInstanceOf(FormData);

      expect(
        (
          request.request.body as FormData
        ).get('file'),
      ).toBe(file);

      request.flush({
        id: 'attachment-1',
        ticket_id: 'ticket-1',
        original_name: 'evidencia.png',
        content_type: 'image/png',
        file_size: 8,
        created_by_user_id: 'user-1',
        created_by: 'Analista Deja',
        created_at: '2026-09-12T15:00:00',
      });

      await expect(promise)
        .resolves
        .toMatchObject({
          id: 'attachment-1',
          ticketId: 'ticket-1',
          originalName: 'evidencia.png',
        });
    },
  );

  it(
    'deve excluir um anexo',
    async () => {
      const promise =
        repository.delete(
          'attachment-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/tickets/attachments/attachment-1',
        );

      expect(request.request.method)
        .toBe('DELETE');

      request.flush(null);

      await expect(promise)
        .resolves
        .toBeUndefined();
    },
  );

  it(
    'deve baixar um anexo como Blob',
    async () => {
      const promise =
        repository.download(
          'attachment-1',
        );

      const request =
        httpTesting.expectOne(
          '/api/chamados/tickets/attachments/attachment-1/download',
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