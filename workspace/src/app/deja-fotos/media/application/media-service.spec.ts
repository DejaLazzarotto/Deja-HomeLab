import {
  MediaRepository,
} from '../domain';

import {
  MediaService,
} from './media-service';

describe('MediaService', () => {
  let repository: MediaRepository;
  let service: MediaService;

  beforeEach(() => {
    repository = {
      list: vi.fn(),
      findById: vi.fn(),
      bulkUpdate: vi.fn(),
      loadThumbnail: vi.fn(),
    };

    service = new MediaService(repository);
  });

  it('should reject an empty bulk selection', () => {
    expect(() => service.bulkUpdate({
      operation: 'verify_original_date',
      mediaIds: [],
    })).toThrowError(
      'Selecione ao menos uma mídia.',
    );

    expect(repository.bulkUpdate)
      .not.toHaveBeenCalled();
  });

  it('should reject more than 100 media items', () => {
    const mediaIds = Array.from(
      {
        length: 101,
      },
      (_, index) => `media-${index}`,
    );

    expect(() => service.bulkUpdate({
      operation: 'clear_original_date_conflict',
      mediaIds,
    })).toThrowError(
      'Selecione no máximo 100 mídias por operação.',
    );

    expect(repository.bulkUpdate)
      .not.toHaveBeenCalled();
  });

  it('should reject duplicated media identifiers', () => {
    expect(() => service.bulkUpdate({
      operation: 'set_album',
      mediaIds: [
        'media-1',
        'media-1',
      ],
      albumId: null,
    })).toThrowError(
      'A seleção contém mídias repetidas.',
    );

    expect(repository.bulkUpdate)
      .not.toHaveBeenCalled();
  });

  it('should delegate a valid bulk operation', async () => {
    vi.mocked(repository.bulkUpdate)
      .mockResolvedValue({
        operation: 'set_original_date',
        requestedCount: 1,
        succeededCount: 1,
        failedCount: 0,
        results: [],
      });

    const operation = {
      operation: 'set_original_date' as const,
      mediaIds: [
        'media-1',
      ],
      originalDate: '2024-03-10T15:00:00.000Z',
    };

    await expect(
      service.bulkUpdate(operation),
    ).resolves.toMatchObject({
      requestedCount: 1,
      succeededCount: 1,
      failedCount: 0,
    });

    expect(repository.bulkUpdate)
      .toHaveBeenCalledOnce();

    expect(repository.bulkUpdate)
      .toHaveBeenCalledWith(operation);
  });
});