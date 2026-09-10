import {
  PortalTicket,
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

  function createRepositoryMock(): HttpPortalTicketRepository {
    return {
      list: vi.fn(),
      findById: vi.fn(),
      listTimeline: vi.fn(),
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

});