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
      listByPerson: vi.fn(),
      findById: vi.fn(),
      upload: vi.fn(),
      delete: vi.fn(),
      updateDescription: vi.fn(),
      bulkUpdate: vi.fn(),
      loadThumbnail: vi.fn(),
    };

    service = new MediaService(repository);
  });

  it('should reject an upload without environment', () => {
    const file = new File(
      [
        'photo',
      ],
      'photo.jpg',
      {
        type: 'image/jpeg',
      },
    );

    expect(() => service.upload({
      environmentId: '   ',
      albumId: null,
      file,
    })).toThrowError(
      'Selecione o ambiente de destino.',
    );

    expect(repository.upload)
      .not.toHaveBeenCalled();
  });

  it('should reject an unsupported upload format', () => {
    const file = new File(
      [
        'document',
      ],
      'document.pdf',
      {
        type: 'application/pdf',
      },
    );

    expect(() => service.upload({
      environmentId: 'environment-1',
      albumId: null,
      file,
    })).toThrowError(
      'O formato do arquivo document.pdf não é aceito.',
    );

    expect(repository.upload)
      .not.toHaveBeenCalled();
  });

  it('should normalize and delegate a valid upload', async () => {
    vi.mocked(repository.upload)
      .mockResolvedValue({} as never);

    const file = new File(
      [
        'photo',
      ],
      'photo.jpg',
      {
        type: 'image/jpeg',
      },
    );

    await service.upload({
      environmentId: ' environment-1 ',
      albumId: ' album-1 ',
      file,
    });

    expect(repository.upload)
      .toHaveBeenCalledOnce();

    expect(repository.upload)
      .toHaveBeenCalledWith({
        environmentId: 'environment-1',
        albumId: 'album-1',
        file,
      });
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

  it('should normalize and delegate a media description update', async () => {
    vi.mocked(repository.updateDescription)
      .mockResolvedValue({} as never);

    await service.updateDescription(
      'media-1',
      '  Vídeo do casamento  ',
    );

    expect(repository.updateDescription)
      .toHaveBeenCalledWith(
        'media-1',
        'Vídeo do casamento',
      );
  });

  it('should normalize an empty media description to null', async () => {
    vi.mocked(repository.updateDescription)
      .mockResolvedValue({} as never);

    await service.updateDescription(
      'media-1',
      '   ',
    );

    expect(repository.updateDescription)
      .toHaveBeenCalledWith(
        'media-1',
        null,
      );
  });

  it('should reject a media description longer than 5000 characters', () => {
    expect(() => service.updateDescription(
      'media-1',
      'a'.repeat(5001),
    )).toThrowError(
      'A descrição deve ter no máximo 5.000 caracteres.',
    );

    expect(repository.updateDescription)
      .not.toHaveBeenCalled();
  });
  it.each([
    'image',
    'video',
  ] as const)(
    'should delegate thumbnail loading for %s media',
    async mediaType => {
      const thumbnail = new Blob([
        mediaType,
      ]);

      vi.mocked(repository.loadThumbnail)
        .mockResolvedValue(thumbnail);

      await expect(
        service.loadThumbnail('media-1', mediaType),
      ).resolves.toBe(thumbnail);

      expect(repository.loadThumbnail)
        .toHaveBeenCalledWith(
          'media-1',
          mediaType,
        );
    },
  );

});
