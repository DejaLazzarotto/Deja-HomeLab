import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  OnDestroy,
  inject,
  signal,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  Router,
} from '@angular/router';

import {
  firstValueFrom,
} from 'rxjs';

interface AlbumResponse {
  id: string;
  organization_id: string;
  tenant_id: string;
  environment_id: string;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface MediaResponse {
  readonly id: string;
  readonly media_type: 'image' | 'video';
}

interface MediaListResponse {
  readonly items: readonly MediaResponse[];
}

interface AlbumView extends AlbumResponse {
  readonly coverUrl: string | null;
}

@Component({
  selector: 'app-albums-page',
  standalone: true,
  templateUrl: './albums-page.html',
  styleUrl: './albums-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class AlbumsPageComponent
  implements OnInit, OnDestroy {
  private readonly http =
    inject(HttpClient);

  private readonly router =
    inject(Router);

  openAlbum(albumId: string): void {
    void this.router.navigate([
      '/albums',
      albumId,
    ]);
  }

  goBack(): void {
    void this.router.navigateByUrl('/explore');
  }

  private readonly objectUrls =
    new Set<string>();

  private destroyed = false;

  readonly albums =
    signal<readonly AlbumView[]>([]);

  readonly loading =
    signal(true);

  readonly error =
    signal<string | null>(null);

  async ngOnInit(): Promise<void> {
    try {
      const albums =
        await firstValueFrom(
          this.http.get<
            readonly AlbumResponse[]
          >(
            '/api/fotos/albums',
          ),
        );

      const activeAlbums = albums.filter(
        album => album.active,
      );

      this.albums.set(
        activeAlbums.map(album => ({
          ...album,
          coverUrl: null,
        })),
      );

      void this.loadCovers(activeAlbums);
    } catch {
      this.error.set(
        'Não foi possível carregar os álbuns.',
      );
    } finally {
      this.loading.set(false);
    }
  }
  ngOnDestroy(): void {
    this.destroyed = true;

    for (const url of this.objectUrls) {
      URL.revokeObjectURL(url);
    }

    this.objectUrls.clear();
  }

  private async loadCovers(
    albums: readonly AlbumResponse[],
  ): Promise<void> {
    let nextIndex = 0;

    const worker = async (): Promise<void> => {
      while (!this.destroyed && nextIndex < albums.length) {
        const album = albums[nextIndex++];

        const coverUrl =
          await this.loadAlbumCover(album.id);

        if (this.destroyed) {
          return;
        }

        this.albums.update(current =>
          current.map(item =>
            item.id === album.id
              ? { ...item, coverUrl }
              : item,
          ),
        );
      }
    };

    await Promise.all(
      Array.from(
        { length: Math.min(3, albums.length) },
        () => worker(),
      ),
    );
  }

  private async loadAlbumCover(
    albumId: string,
  ): Promise<string | null> {
    try {
      let media = await this.findCoverMedia(
        albumId,
        'image',
      );

      if (!media) {
        media = await this.findCoverMedia(
          albumId,
          'video',
        );
      }

      if (!media || this.destroyed) {
        return null;
      }

      const derivative =
        media.media_type === 'video'
          ? 'poster'
          : 'thumbnail';

      const blob = await firstValueFrom(
        this.http.get(
          `/api/fotos/media/${media.id}/${derivative}`,
          {
            responseType: 'blob',
          },
        ),
      );

      if (this.destroyed) {
        return null;
      }

      const url = URL.createObjectURL(blob);
      this.objectUrls.add(url);

      return url;
    } catch {
      return null;
    }
  }

  private async findCoverMedia(
    albumId: string,
    mediaType: 'image' | 'video',
  ): Promise<MediaResponse | null> {
    const response = await firstValueFrom(
      this.http.get<MediaListResponse>(
        '/api/fotos/media',
        {
          params: {
            album_id: albumId,
            media_type: mediaType,
            page: 1,
            page_size: 1,
          },
        },
      ),
    );

    return response.items[0] ?? null;
  }}