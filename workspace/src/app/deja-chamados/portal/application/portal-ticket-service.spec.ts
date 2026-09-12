import {
  PortalTicket,
  PortalTicketAttachment,
  PortalTicketComment,
  PortalTicketCommentCreate,
  PortalTicketCreate,
  PortalTimelineEvent,
} from '../domain/portal-ticket';

import {
  HttpPortalTicketRepository,
} from '../infrastructure/http-portal-ticket-repository';

import {
  PortalTicketNotFoundError,
  PortalTicketService,
} from './portal-ticket-service';

describe('PortalTicketService', () => {

  const ticket: PortalTicket = {
    id: 'ticket-1',
    title: 'Erro de acesso',
    description: 'Não consigo acessar.',
    status: 'open',
    priority: 'medium',
    assignedToUserName: null,
    closedAt: null,
    createdAt: '2026-09-08T10:00:00',
    updatedAt: '2026-09-08T10:00:00',
  };

  const timeline: readonly PortalTimelineEvent[] = [
    {
      id: 'event-1',
      eventType: 'created',
      description: 'Chamado criado pelo Portal.',
      previousValue: null,
      newValue: 'created',
      createdAt: '2026-09-08T10:00:00',
    },
    {
      id: 'event-2',
      eventType: 'status_changed',
      description: 'Status do chamado alterado.',
      previousValue: 'open',
      newValue: 'in_progress',
      createdAt: '2026-09-08T11:00:00',
    },
  ];

  const attachments: readonly PortalTicketAttachment[] = [
    {
      id: 'attachment-1',
      originalName: 'evidencia.png',
      contentType: 'image/png',
      fileSize: 2048,
      createdBy: 'Analista Deja',
      createdAt: '2026-09-12T15:00:00',
    },
  ];

  const comments: readonly PortalTicketComment[] = [
    {
      id: 'comment-1',
      content: 'Comentário do cliente.',
      createdBy: 'Cliente Portal',
      createdAt: '2026-09-08T12:00:00',
    },
    {
      id: 'comment-2',
      content: 'Resposta pública da equipe.',
      createdBy: 'Analista',
      createdAt: '2026-09-08T13:00:00',
    },
  ];

  function createRepositoryMock(): HttpPortalTicketRepository {
    return {
      list: vi.fn(),
      findById: vi.fn(),
      listTimeline: vi.fn(),
      listComments: vi.fn(),
      createComment: vi.fn(),
      listAttachments: vi.fn(),
      downloadAttachment: vi.fn(),
      create: vi.fn(),
    } as unknown as HttpPortalTicketRepository;
  }

  it(
    'deve listar os chamados pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.list)
        .mockResolvedValue([
          ticket,
        ]);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.list(),
      ).resolves.toEqual([
        ticket,
      ]);

      expect(repository.list)
        .toHaveBeenCalledOnce();
    },
  );

  it(
    'deve consultar um chamado existente',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.findById)
        .mockResolvedValue(ticket);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.findById(
          'ticket-1',
        ),
      ).resolves.toEqual(ticket);

      expect(repository.findById)
        .toHaveBeenCalledWith(
          'ticket-1',
        );
    },
  );

  it(
    'deve lançar erro quando o chamado não existir',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.findById)
        .mockResolvedValue(undefined);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.findById(
          'ticket-inexistente',
        ),
      ).rejects.toBeInstanceOf(
        PortalTicketNotFoundError,
      );
    },
  );

  it(
    'deve listar a timeline pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.listTimeline)
        .mockResolvedValue(timeline);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.listTimeline(
          'ticket-1',
        ),
      ).resolves.toEqual(timeline);

      expect(repository.listTimeline)
        .toHaveBeenCalledWith(
          'ticket-1',
        );
    },
  );

  it(
    'deve listar os comentários pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.listComments)
        .mockResolvedValue(comments);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.listComments(
          'ticket-1',
        ),
      ).resolves.toEqual(comments);

      expect(repository.listComments)
        .toHaveBeenCalledWith(
          'ticket-1',
        );
    },
  );

  it(
    'deve criar comentário pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      const createdComment =
        comments[0];

      vi.mocked(repository.createComment)
        .mockResolvedValue(createdComment);

      const service =
        new PortalTicketService(
          repository,
        );

      const input: PortalTicketCommentCreate = {
        content: 'Comentário do cliente.',
      };

      await expect(
        service.createComment(
          'ticket-1',
          input,
        ),
      ).resolves.toEqual(createdComment);

      expect(repository.createComment)
        .toHaveBeenCalledWith(
          'ticket-1',
          input,
        );
    },
  );

  it(
    'deve abrir um chamado pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.create)
        .mockResolvedValue(ticket);

      const service =
        new PortalTicketService(
          repository,
        );

      const input: PortalTicketCreate = {
        title: 'Erro de acesso',
        description: 'Não consigo acessar.',
      };

      await expect(
        service.create(input),
      ).resolves.toEqual(ticket);

      expect(repository.create)
        .toHaveBeenCalledWith(input);
    },
  );


  it(
    'deve listar os anexos pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(repository.listAttachments)
        .mockResolvedValue(attachments);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.listAttachments(
          'ticket-1',
        ),
      ).resolves.toEqual(attachments);

      expect(repository.listAttachments)
        .toHaveBeenCalledWith(
          'ticket-1',
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

      vi.mocked(repository.downloadAttachment)
        .mockResolvedValue(blob);

      const service =
        new PortalTicketService(
          repository,
        );

      await expect(
        service.downloadAttachment(
          'attachment-1',
        ),
      ).resolves.toBe(blob);

      expect(repository.downloadAttachment)
        .toHaveBeenCalledWith(
          'attachment-1',
        );
    },
  );

});