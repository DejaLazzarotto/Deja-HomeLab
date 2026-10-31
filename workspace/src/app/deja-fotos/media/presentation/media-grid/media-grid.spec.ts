import { TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { MediaService } from '../../application';
import { Media } from '../../domain';
import { MediaGridComponent } from './media-grid';

function createMedia(
  overrides: Partial<Media> = {},
): Media {
  return {
    id: 'media-1',
    organizationId: 'organization-1',
    tenantId: 'tenant-1',
    environmentId: 'environment-1',
    albumId: null,
    originalName: 'video.mp4',
    description: null,
    sourceContentType: 'video/mp4',
    sourceFileExtension: 'mp4',
    sourceFileSize: 100,
    sourceChecksumSha256: 'source-checksum',
    mediaType: 'video',
    contentType: 'video/mp4',
    fileExtension: 'mp4',
    fileSize: 100,
    checksumSha256: 'managed-checksum',
    wasConverted: false,
    processingStatus: 'received',
    processingError: null,
    originalDate: '2026-09-15T10:00:00',
    originalDateSource: 'embedded_metadata',
    originalDatePrecision: 'datetime',
    originalDateVerified: false,
    originalDateConflict: false,
    width: 1920,
    height: 1080,
    durationSeconds: 60,
    viewCount: 0,
    createdByUserId: 'user-1',
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
    deletedAt: null,
    ...overrides,
  };
}

describe('MediaGridComponent', () => {
  let service: {
    loadThumbnail: ReturnType<typeof vi.fn>;
    updateDescription: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    service = {
      loadThumbnail: vi.fn(),
      updateDescription: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MediaGridComponent],
    }).compileComponents();
  });

  function createFixture(
    media: Media,
    canEditDescription = true,
  ) {
    const fixture = TestBed.createComponent(
      MediaGridComponent,
    );

    fixture.componentRef.setInput('items', [media]);
    fixture.componentRef.setInput(
      'service',
      service as unknown as MediaService,
    );
    fixture.componentRef.setInput(
      'canEditDescription',
      canEditDescription,
    );
    fixture.detectChanges();

    return fixture;
  }

  it('shows the saved description and edit action for a video', () => {
    const fixture = createFixture(createMedia({
      description: 'Vídeo do casamento',
    }));

    const text = (
      fixture.nativeElement as HTMLElement
    ).textContent;

    expect(text).toContain('Vídeo do casamento');
    expect(text).toContain('Editar descrição');
  });

  it('does not show description controls for a photo', () => {
    const fixture = createFixture(createMedia({
      originalName: 'foto.jpg',
      description: null,
      mediaType: 'image',
      sourceContentType: 'image/jpeg',
      sourceFileExtension: 'jpg',
      contentType: 'image/jpeg',
      fileExtension: 'jpg',
      durationSeconds: null,
    }));

    const text = (
      fixture.nativeElement as HTMLElement
    ).textContent;

    expect(text).not.toContain('Adicionar descrição');
    expect(text).not.toContain('Editar descrição');
  });

  it('saves a video description and emits the updated media', async () => {
    const media = createMedia({
      description: 'Descrição antiga',
    });

    const updated = {
      ...media,
      description: 'Descrição nova',
    };

    service.updateDescription.mockResolvedValue(updated);

    const fixture = createFixture(media);
    const emitted = vi.fn();

    fixture.componentInstance.mediaUpdated.subscribe(emitted);

    fixture.componentInstance['editDescription'](media);
    fixture.componentInstance.descriptionDraft.set(
      'Descrição nova',
    );

    await fixture.componentInstance['saveDescription'](media);

    expect(service.updateDescription).toHaveBeenCalledWith(
      media.id,
      'Descrição nova',
    );
    expect(emitted).toHaveBeenCalledWith(updated);
    expect(
      fixture.componentInstance.editingDescriptionId(),
    ).toBeNull();
  });

  it('clears a saved video description', async () => {
    const media = createMedia({
      description: 'Descrição existente',
    });

    const updated = {
      ...media,
      description: null,
    };

    service.updateDescription.mockResolvedValue(updated);

    const fixture = createFixture(media);

    fixture.componentInstance['editDescription'](media);

    await fixture.componentInstance['clearDescription'](media);

    expect(service.updateDescription).toHaveBeenCalledWith(
      media.id,
      null,
    );
  });
  it('reloads the thumbnail when the media version changes', async () => {
    const media = createMedia({
      id: 'photo-1',
      mediaType: 'image',
      originalName: 'photo.jpg',
      processingStatus: 'ready',
    });

    const createObjectURL = vi.spyOn(URL, 'createObjectURL')
      .mockReturnValueOnce('blob:photo-original')
      .mockReturnValueOnce('blob:photo-updated');

    const revokeObjectURL = vi.spyOn(URL, 'revokeObjectURL')
      .mockImplementation(() => {});

    service.loadThumbnail.mockResolvedValue(
      new Blob(['image'], { type: 'image/webp' }),
    );

    try {
      const fixture = createFixture(media);

      await fixture.whenStable();

      expect(service.loadThumbnail).toHaveBeenCalledTimes(1);

      fixture.componentRef.setInput('items', [{
        ...media,
        updatedAt: '2026-10-30T23:50:00.000Z',
      }]);

      fixture.detectChanges();
      await fixture.whenStable();

      expect(service.loadThumbnail).toHaveBeenCalledTimes(2);
      expect(revokeObjectURL).toHaveBeenCalledWith(
        'blob:photo-original',
      );

      fixture.destroy();
    } finally {
      createObjectURL.mockRestore();
      revokeObjectURL.mockRestore();
    }
  });
  it('reloads the latest thumbnail after an in-flight update', async () => {
    const media = createMedia({
      id: 'photo-concurrent',
      mediaType: 'image',
      originalName: 'photo.jpg',
      processingStatus: 'ready',
    });

    let resolveFirst!: (blob: Blob) => void;

    const firstRequest = new Promise<Blob>(resolve => {
      resolveFirst = resolve;
    });

    service.loadThumbnail
      .mockReturnValueOnce(firstRequest)
      .mockResolvedValue(
        new Blob(['updated'], { type: 'image/webp' }),
      );

    const createUrl = vi.spyOn(URL, 'createObjectURL')
      .mockReturnValue('blob:updated');

    const revokeUrl = vi.spyOn(URL, 'revokeObjectURL')
      .mockImplementation(() => {});

    const fixture = createFixture(media);

    try {
      expect(service.loadThumbnail).toHaveBeenCalledTimes(1);

      fixture.componentRef.setInput('items', [{
        ...media,
        updatedAt: '2026-10-30T23:55:00.000Z',
      }]);

      fixture.detectChanges();

      resolveFirst(
        new Blob(['old'], { type: 'image/webp' }),
      );

      await fixture.whenStable();
      await Promise.resolve();
      await fixture.whenStable();

      expect(service.loadThumbnail).toHaveBeenCalledTimes(2);
      expect(createUrl).toHaveBeenCalledTimes(1);
    } finally {
      fixture.destroy();
      createUrl.mockRestore();
      revokeUrl.mockRestore();
    }
  });
});