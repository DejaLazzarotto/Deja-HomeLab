import {
  TicketAttachment,
  TicketAttachmentRepository,
} from '../domain';

import {
  TicketAttachmentService,
} from './ticket-attachment-service';

describe('TicketAttachmentService', () => {

  const attachment: TicketAttachment = {
    id: 'attachment-1',
    ticketId: 'ticket-1',
    originalName: 'evidencia.png',
    contentType: 'image/png',
    fileSize: 2048,
    createdByUserId: 'user-1',
    createdBy: 'Analista Deja',
    createdAt: '2026-09-12T15:00:00',
  };

  function createRepositoryMock(): TicketAttachmentRepository {
    return {
      listByTicketId: vi.fn(),
      upload: vi.fn(),
      delete: vi.fn(),
      download: vi.fn(),
    };
  }

  it(
    'deve listar os anexos pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.listByTicketId)
        .mockResolvedValue([
          attachment,
        ]);

      const service =
        new TicketAttachmentService(
          repository,
        );

      await expect(
        service.listByTicketId(
          'ticket-1',
        ),
      ).resolves.toEqual([
        attachment,
      ]);

      expect(repository.listByTicketId)
        .toHaveBeenCalledWith(
          'ticket-1',
        );
    },
  );

  it(
    'deve enviar um anexo pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.upload)
        .mockResolvedValue(
          attachment,
        );

      const service =
        new TicketAttachmentService(
          repository,
        );

      const file = new File(
        ['conteudo'],
        'evidencia.png',
        {
          type: 'image/png',
        },
      );

      await expect(
        service.upload(
          'ticket-1',
          file,
        ),
      ).resolves.toEqual(
        attachment,
      );

      expect(repository.upload)
        .toHaveBeenCalledWith(
          'ticket-1',
          file,
        );
    },
  );

  it(
    'deve excluir um anexo pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.delete)
        .mockResolvedValue();

      const service =
        new TicketAttachmentService(
          repository,
        );

      await expect(
        service.delete(
          'attachment-1',
        ),
      ).resolves.toBeUndefined();

      expect(repository.delete)
        .toHaveBeenCalledWith(
          'attachment-1',
        );
    },
  );

  it(
    'deve baixar um anexo pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      const blob = new Blob(
        ['conteudo'],
        {
          type: 'application/pdf',
        },
      );

      vi.mocked(repository.download)
        .mockResolvedValue(blob);

      const service =
        new TicketAttachmentService(
          repository,
        );

      await expect(
        service.download(
          'attachment-1',
        ),
      ).resolves.toBe(blob);

      expect(repository.download)
        .toHaveBeenCalledWith(
          'attachment-1',
        );
    },
  );

});