import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  Media,
  MediaBulkResult,
  MediaPage,
  MediaService,
} from '../../../media';

import {
  AlbumService,
} from '../../application';

import {
  Album,
  AlbumPeriod,
} from '../../domain';

import {
  AlbumManagementComponent,
} from './album-management';

function createAlbum(
  overrides: Partial<Album> = {},
): Album {
  return {
    id: 'album-source',
    organizationId: 'organization-1',
    tenantId: 'tenant-1',
    environmentId: 'environment-1',
    name: 'Source album',
    description: null,
    active: true,
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
    ...overrides,
  };
}

function createMedia(
  overrides: Partial<Media> = {},
): Media {
  return {
    id: 'media-1',
    organizationId: 'organization-1',
    tenantId: 'tenant-1',
    environmentId: 'environment-1',
    albumId: 'album-source',
    originalName: 'photo.jpg',
    sourceContentType: 'image/jpeg',
    sourceFileExtension: 'jpg',
    sourceFileSize: 100,
    sourceChecksumSha256: 'source-checksum',
    mediaType: 'image',
    contentType: 'image/jpeg',
    fileExtension: 'jpg',
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
    width: 100,
    height: 80,
    durationSeconds: null,
    viewCount: 0,
    createdByUserId: 'user-1',
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
    deletedAt: null,
    ...overrides,
  };
}

function createPage(
  items: readonly Media[],
): MediaPage {
  return {
    items,
    page: 1,
    pageSize: 100,
    total: items.length,
    totalPages: items.length > 0 ? 1 : 0,
  };
}

const septemberPeriod: AlbumPeriod = {
  year: 2026,
  month: 9,
  mediaCount: 2,
  description: 'September',
};

describe('AlbumManagementComponent', () => {
  let fixture: ComponentFixture<AlbumManagementComponent>;
  let component: AlbumManagementComponent;

  let listAlbumsMock: ReturnType<typeof vi.fn>;
  let listPeriodsMock: ReturnType<typeof vi.fn>;
  let listMediaMock: ReturnType<typeof vi.fn>;
  let bulkUpdateMock: ReturnType<typeof vi.fn>;

  const sourceAlbum = createAlbum();

  const destinationAlbum = createAlbum({
    id: 'album-destination',
    name: 'Destination album',
  });

  const incompatibleAlbum = createAlbum({
    id: 'album-incompatible',
    environmentId: 'environment-2',
    name: 'Incompatible album',
  });

  const firstMedia = createMedia();

  const secondMedia = createMedia({
    id: 'media-2',
    originalName: 'second-photo.jpg',
    sourceChecksumSha256: 'source-checksum-2',
    checksumSha256: 'managed-checksum-2',
  });

  beforeEach(async () => {
    listAlbumsMock = vi.fn().mockResolvedValue([
      sourceAlbum,
      destinationAlbum,
      incompatibleAlbum,
    ]);

    listPeriodsMock = vi.fn().mockResolvedValue([
      septemberPeriod,
    ]);

    listMediaMock = vi.fn().mockImplementation(
      (filters: {
        readonly albumId?: string;
      }) => Promise.resolve(
        filters.albumId
          ? createPage([
              firstMedia,
              secondMedia,
            ])
          : createPage([]),
      ),
    );

    bulkUpdateMock = vi.fn();

    const albumService = {
      list: listAlbumsMock,
      listPeriods: listPeriodsMock,
    } as unknown as AlbumService;

    const mediaService = {
      list: listMediaMock,
      bulkUpdate: bulkUpdateMock,
      loadThumbnail: vi.fn(),
    } as unknown as MediaService;

    await TestBed.configureTestingModule({
      imports: [
        AlbumManagementComponent,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      AlbumManagementComponent,
    );

    component = fixture.componentInstance;

    fixture.componentRef.setInput(
      'service',
      albumService,
    );
    fixture.componentRef.setInput(
      'mediaService',
      mediaService,
    );
    fixture.componentRef.setInput(
      'canEdit',
      true,
    );
    fixture.componentRef.setInput(
      'canOrganize',
      true,
    );

    fixture.detectChanges();
    await fixture.whenStable();
  });

  async function loadSourcePeriod(): Promise<void> {
    component.selectDashboardAlbum(sourceAlbum.id);
    await fixture.whenStable();

    component.togglePeriod('2026-09');
    await fixture.whenStable();
  }

  it('offers only compatible destination albums', () => {
    component.selectDashboardAlbum(sourceAlbum.id);

    expect(
      component.destinationAlbums().map(
        album => album.id,
      ),
    ).toEqual([
      destinationAlbum.id,
    ]);
  });

  it('keeps individual and loaded-period selection when collapsed', async () => {
    await loadSourcePeriod();

    component.toggleMediaSelection(
      firstMedia.id,
      true,
    );

    component.togglePeriod('2026-09');

    expect(
      component.selectedMediaIds().has(firstMedia.id),
    ).toBe(true);

    component.togglePeriod('2026-09');

    const period = component.albumMediaPeriods()[0];

    component.toggleLoadedPeriodSelection(
      period.key,
      true,
    );

    expect(
      component.selectedMediaIds(),
    ).toEqual(
      new Set([
        firstMedia.id,
        secondMedia.id,
      ]),
    );
  });

  it('moves selected media and refreshes affected periods', async () => {
    listPeriodsMock
      .mockResolvedValueOnce([
        septemberPeriod,
      ])
      .mockResolvedValueOnce([]);

    await loadSourcePeriod();

    component.toggleMediaSelection(
      firstMedia.id,
      true,
    );

    const movedMedia = createMedia({
      albumId: destinationAlbum.id,
    });

    const result: MediaBulkResult = {
      operation: 'set_album',
      requestedCount: 1,
      succeededCount: 1,
      failedCount: 0,
      results: [
        {
          mediaId: firstMedia.id,
          success: true,
          media: movedMedia,
          errorCode: null,
          errorMessage: null,
        },
      ],
    };

    bulkUpdateMock.mockResolvedValue(result);

    await component.executeAlbumBulkAction({
      operation: 'set_album',
      albumId: destinationAlbum.id,
    });

    expect(bulkUpdateMock).toHaveBeenCalledWith({
      operation: 'set_album',
      mediaIds: [
        firstMedia.id,
      ],
      albumId: destinationAlbum.id,
    });

    expect(component.albumMediaPeriods()).toEqual([]);
    expect(component.selectedMediaIds().size).toBe(0);
    expect(component.operationMessage()).toContain(
      '1 m\u00eddia movida',
    );
  });

  it('asks for confirmation before removing media from the album', async () => {
    await loadSourcePeriod();

    component.toggleMediaSelection(
      firstMedia.id,
      true,
    );

    const confirmMock = vi
      .spyOn(window, 'confirm')
      .mockReturnValue(false);

    await component.executeAlbumBulkAction({
      operation: 'set_album',
      albumId: null,
    });

    expect(confirmMock).toHaveBeenCalledOnce();
    expect(bulkUpdateMock).not.toHaveBeenCalled();

    confirmMock.mockRestore();
  });

  it('keeps only failed media selected after a partial result', async () => {
    component.selectDashboardAlbum(sourceAlbum.id);
    await fixture.whenStable();

    component.toggleMediaSelection(
      firstMedia.id,
      true,
    );
    component.toggleMediaSelection(
      secondMedia.id,
      true,
    );

    const result: MediaBulkResult = {
      operation: 'set_album',
      requestedCount: 2,
      succeededCount: 1,
      failedCount: 1,
      results: [
        {
          mediaId: firstMedia.id,
          success: true,
          media: createMedia({
            albumId: destinationAlbum.id,
          }),
          errorCode: null,
          errorMessage: null,
        },
        {
          mediaId: secondMedia.id,
          success: false,
          media: null,
          errorCode: 'fotos_media_album_scope_mismatch',
          errorMessage: 'Scope mismatch.',
        },
      ],
    };

    bulkUpdateMock.mockResolvedValue(result);

    await component.executeAlbumBulkAction({
      operation: 'set_album',
      albumId: destinationAlbum.id,
    });

    expect(component.selectedMediaIds()).toEqual(
      new Set([
        secondMedia.id,
      ]),
    );

    expect(component.operationError()).toContain(
      '1 m\u00eddia n\u00e3o p\u00f4de',
    );
  });
});
