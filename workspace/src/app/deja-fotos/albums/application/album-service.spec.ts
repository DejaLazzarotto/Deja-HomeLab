import {
  AlbumRepository,
} from '../domain';

import {
  AlbumService,
} from './album-service';

describe('AlbumService', () => {
  let repository: AlbumRepository;
  let service: AlbumService;

  const environmentId =
    '33333333-3333-3333-3333-333333333333';

  beforeEach(() => {
    repository = {
      list: vi.fn(),
      findById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    };

    service = new AlbumService(repository);
  });

  it('should normalize input before creating an album', async () => {
    vi.mocked(repository.create)
      .mockResolvedValue({
        id: '44444444-4444-4444-4444-444444444444',
        organizationId: '11111111-1111-1111-1111-111111111111',
        tenantId: '22222222-2222-2222-2222-222222222222',
        environmentId,
        name: 'Viagem 2024',
        description: 'Registros da viagem.',
        active: true,
        createdAt: '2026-09-17T10:00:00',
        updatedAt: '2026-09-17T10:00:00',
      });

    await service.create({
      environmentId: ` ${environmentId} `,
      name: ' Viagem 2024 ',
      description: ' Registros da viagem. ',
      active: true,
    });

    expect(repository.create)
      .toHaveBeenCalledWith({
        environmentId,
        name: 'Viagem 2024',
        description: 'Registros da viagem.',
        active: true,
      });
  });

  it('should normalize an empty description to null', async () => {
    vi.mocked(repository.update)
      .mockResolvedValue({
        id: '44444444-4444-4444-4444-444444444444',
        organizationId: '11111111-1111-1111-1111-111111111111',
        tenantId: '22222222-2222-2222-2222-222222222222',
        environmentId,
        name: 'Família',
        description: null,
        active: true,
        createdAt: '2026-09-17T10:00:00',
        updatedAt: '2026-09-17T11:00:00',
      });

    await service.update(
      '44444444-4444-4444-4444-444444444444',
      {
        environmentId,
        name: ' Família ',
        description: '   ',
        active: true,
      },
    );

    expect(repository.update)
      .toHaveBeenCalledWith(
        '44444444-4444-4444-4444-444444444444',
        {
          environmentId,
          name: 'Família',
          description: null,
          active: true,
        },
      );
  });

  it('should reject an album without a name', () => {
    expect(() => service.create({
      environmentId,
      name: '   ',
      description: null,
      active: true,
    })).toThrowError(
      'Informe o nome do álbum.',
    );

    expect(repository.create)
      .not.toHaveBeenCalled();
  });
});