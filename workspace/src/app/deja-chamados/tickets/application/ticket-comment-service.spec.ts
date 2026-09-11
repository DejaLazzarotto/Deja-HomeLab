import {
  TicketComment,
  TicketCommentCreateInput,
  TicketCommentRepository,
} from '../domain';

import {
  TicketCommentService,
} from './ticket-comment-service';

describe('TicketCommentService', () => {

  const comment: TicketComment = {
    id: 'comment-1',
    ticketId: 'ticket-1',
    content: 'Comentário administrativo.',
    visibility: 'internal',
    createdByUserId: 'user-1',
    createdBy: 'Administrador',
    createdAt: '2026-09-11T10:00:00',
  };

  function createRepositoryMock(): TicketCommentRepository {
    return {
      listByTicketId: vi.fn(),
      create: vi.fn(),
    };
  }

  it(
    'deve listar os comentários pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      vi.mocked(
        repository.listByTicketId,
      ).mockResolvedValue([
        comment,
      ]);

      const service =
        new TicketCommentService(
          repository,
        );

      await expect(
        service.listByTicketId(
          'ticket-1',
        ),
      ).resolves.toEqual([
        comment,
      ]);

      expect(
        repository.listByTicketId,
      ).toHaveBeenCalledWith(
        'ticket-1',
      );
    },
  );

  it(
    'deve criar comentário pelo repositório',
    async () => {
      const repository =
        createRepositoryMock();

      const input: TicketCommentCreateInput = {
        content: 'Comentário administrativo.',
        visibility: 'internal',
      };

      vi.mocked(
        repository.create,
      ).mockResolvedValue(
        comment,
      );

      const service =
        new TicketCommentService(
          repository,
        );

      await expect(
        service.create(
          'ticket-1',
          input,
        ),
      ).resolves.toEqual(
        comment,
      );

      expect(
        repository.create,
      ).toHaveBeenCalledWith(
        'ticket-1',
        input,
      );
    },
  );

});