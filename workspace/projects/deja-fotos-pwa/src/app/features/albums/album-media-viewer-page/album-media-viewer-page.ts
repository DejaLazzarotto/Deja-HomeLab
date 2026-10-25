import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { ActivatedRoute, Router } from '@angular/router';

import { firstValueFrom } from 'rxjs';

import { FavoritesService } from '../../../core/favorites/favorites.service';
import { MusicPlayerService } from '../../../core/music/music-player.service';

interface MediaResponse {
  id: string;
  media_type: 'image' | 'video';
  is_animated: boolean;
  original_date: string | null;
  original_name: string;
}

interface MediaListResponse {
  items: readonly MediaResponse[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

const PAGE_SIZE = 30;
const PREFETCH_THRESHOLD = 5;

@Component({
  selector: 'app-album-media-viewer-page',
  standalone: true,
  templateUrl: './album-media-viewer-page.html',
  styleUrl: './album-media-viewer-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlbumMediaViewerPageComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);

  private readonly favoritesService = inject(FavoritesService);

  private readonly music = inject(MusicPlayerService);

  private readonly route = inject(ActivatedRoute);

  private readonly router = inject(Router);

  private objectUrl: string | null = null;

  private touchStartX: number | null = null;

  private touchStartY: number | null = null;

  private currentPage = 0;

  private totalPages = 0;

  private totalMedia = 0;

  private loadingMore = false;

  readonly albumId = signal<string | null>(null);

  readonly year = signal<number | null>(null);

  readonly month = signal<number | null>(null);

  readonly mediaId = signal<string | null>(null);

  readonly media = signal<MediaResponse | null>(null);

  readonly monthMedia = signal<readonly MediaResponse[]>([]);

  readonly currentIndex = signal<number>(-1);

  readonly mediaUrl = signal<string | null>(null);

  readonly isFavorite = signal(false);

  readonly favoriteLoading = signal(false);

  readonly favoriteSaving = signal(false);

  readonly loading = signal(true);

  readonly error = signal<string | null>(null);

  readonly total = signal<number>(0);

  async ngOnInit(): Promise<void> {
    const albumId = this.route.snapshot.paramMap.get('albumId');

    const yearParam =
      this.route.snapshot.paramMap.get('year');

    const monthParam =
      this.route.snapshot.paramMap.get('month');

    const mediaId =
      this.route.snapshot.paramMap.get('mediaId');

    const selectedYear = Number(yearParam);

    const selectedMonth = Number(monthParam);

    if (
      !albumId ||
      !yearParam ||
      !monthParam ||
      !mediaId ||
      !Number.isInteger(selectedYear) ||
      !Number.isInteger(selectedMonth) ||
      selectedYear < 1 ||
      selectedYear > 9999 ||
      selectedMonth < 1 ||
      selectedMonth > 12
    ) {
      this.error.set('Mídia inválida.');

      this.loading.set(false);

      return;
    }

    this.albumId.set(albumId);
    this.year.set(selectedYear);
    this.month.set(selectedMonth);
    this.mediaId.set(mediaId);

    try {
      await this.loadUntilMediaFound(mediaId);

      await this.loadCurrentMedia();
    } catch {
      this.error.set(
        'Não foi possível carregar a mídia.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  onVideoPlay(event?: Event): void {
    if (this.loading()) {
      return;
    }

    if (event) {
      const video = event.target;

      if (
        !(video instanceof HTMLVideoElement) ||
        !video.isConnected ||
        video !== document.querySelector('.album-media-viewer-page .viewer-video')
      ) {
        return;
      }
    }

    this.music.pauseForVideo();
  }

  onVideoStop(event?: Event): void {
    if (this.loading()) {
      return;
    }

    if (event) {
      const video = event.target;

      if (
        !(video instanceof HTMLVideoElement) ||
        !video.isConnected ||
        video !== document.querySelector('.album-media-viewer-page .viewer-video')
      ) {
        return;
      }
    }

    this.music.resumeFromVideo();
  }

  ngOnDestroy(): void {
    const destination = this.router.getCurrentNavigation()?.finalUrl?.toString() ?? this.router.url;
    const albumId = this.albumId();
    if (albumId && destination.startsWith('/albums/' + encodeURIComponent(albumId) + '/')) {
      this.music.resumeFromVideo();
    }
    this.revokeObjectUrl();
  }

  goBack(): void {
    const albumId = this.albumId();
    const selectedYear = this.year();
    const selectedMonth = this.month();

    if (
      !albumId ||
      selectedYear === null ||
      selectedMonth === null
    ) {
      void this.router.navigateByUrl('/albums');
      return;
    }

    void this.router.navigate([
      '/albums',
      albumId,
      selectedYear,
      selectedMonth,
    ]);
  }

  async showPrevious(): Promise<void> {
    const index = this.currentIndex();

    if (index <= 0) {
      return;
    }

    await this.changeMedia(index - 1);
  }

  async showNext(): Promise<void> {
    const index = this.currentIndex();

    const items = this.monthMedia();

    if (index < 0) {
      return;
    }

    if (
      index >= items.length - PREFETCH_THRESHOLD
    ) {
      await this.loadNextPage();
    }

    const updatedItems = this.monthMedia();

    if (index >= updatedItems.length - 1) {
      return;
    }

    await this.changeMedia(index + 1);
  }

  onTouchStart(event: TouchEvent): void {
    const touch = event.changedTouches[0];

    if (!touch) {
      return;
    }

    this.touchStartX = touch.clientX;

    this.touchStartY = touch.clientY;
  }

  async onTouchEnd(
    event: TouchEvent,
  ): Promise<void> {
    if (
      this.touchStartX === null ||
      this.touchStartY === null
    ) {
      return;
    }

    const touch = event.changedTouches[0];

    if (!touch) {
      this.resetTouch();

      return;
    }

    const deltaX =
      touch.clientX - this.touchStartX;

    const deltaY =
      touch.clientY - this.touchStartY;

    this.resetTouch();

    const minimumSwipeDistance = 50;

    if (
      Math.abs(deltaX) <
      minimumSwipeDistance
    ) {
      return;
    }

    if (
      Math.abs(deltaX) <=
      Math.abs(deltaY)
    ) {
      return;
    }

    if (deltaX < 0) {
      await this.showNext();

      return;
    }

    await this.showPrevious();
  }

  private async loadUntilMediaFound(
    mediaId: string,
  ): Promise<void> {
    let page = 1;

    while (true) {
      await this.loadPage(page);

      const index =
        this.monthMedia().findIndex(
          (item) => item.id === mediaId,
        );

      if (index >= 0) {
        this.currentIndex.set(index);

        return;
      }

      if (page >= this.totalPages) {
        throw new Error(
          'Mídia não encontrada no período.',
        );
      }

      page += 1;
    }
  }

  private async loadNextPage(): Promise<void> {
    if (
      this.loadingMore ||
      this.currentPage >= this.totalPages
    ) {
      return;
    }

    this.loadingMore = true;

    try {
      await this.loadPage(
        this.currentPage + 1,
      );
    } finally {
      this.loadingMore = false;
    }
  }

  private async loadPage(
    page: number,
  ): Promise<void> {
    const albumId = this.albumId();
    const selectedYear = this.year();
    const selectedMonth = this.month();

    if (
      !albumId ||
      selectedYear === null ||
      selectedMonth === null
    ) {
      throw new Error('Álbum ou período inválido.');
    }

    const response = await firstValueFrom(
      this.http.get<MediaListResponse>(
        '/api/fotos/media',
        {
          params: {
            album_id: albumId,
            original_year: selectedYear,
            original_month: selectedMonth,
            page,
            page_size: PAGE_SIZE,
          },
        },
      ),
    );

    if (page === 1) {
      this.monthMedia.set(response.items);
    } else {
      this.monthMedia.update(
        (current) => [
          ...current,
          ...response.items,
        ],
      );
    }

    this.currentPage = response.page;
    this.totalPages = response.total_pages;
    this.totalMedia = response.total;

    this.total.set(this.totalMedia);
  }

  private async changeMedia(
    index: number,
  ): Promise<void> {
    const items = this.monthMedia();

    const item = items[index];

    if (!item) {
      return;
    }

    if (item.media_type !== 'video') {
      this.music.resumeFromVideo();
    }

    this.loading.set(true);
    this.error.set(null);

    try {
      this.currentIndex.set(index);
      this.mediaId.set(item.id);

      await this.loadCurrentMedia();

      const albumId = this.albumId();
      const selectedYear = this.year();
      const selectedMonth = this.month();

      if (
        albumId &&
        selectedYear !== null &&
        selectedMonth !== null
      ) {
        await this.router.navigate(
          [
            '/albums',
            albumId,
            selectedYear,
            selectedMonth,
            'media',
            item.id,
          ],
          {
            replaceUrl: true,
          },
        );
      }
    } catch {
      this.error.set(
        'Não foi possível carregar a mídia.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  private favoriteRequestVersion = 0;

  private readonly favoriteSavingMediaIds = new Set<string>();

  private async refreshFavorite(mediaId: string): Promise<void> {
    const version = ++this.favoriteRequestVersion;

    this.isFavorite.set(false);
    this.favoriteSaving.set(
      this.favoriteSavingMediaIds.has(mediaId),
    );
    this.favoriteLoading.set(true);

    try {
      const favorite = await this.favoritesService.isFavorite(mediaId);

      if (version === this.favoriteRequestVersion && this.mediaId() === mediaId) {
        this.isFavorite.set(favorite);
      }
    } catch {
      if (version === this.favoriteRequestVersion && this.mediaId() === mediaId) {
        this.isFavorite.set(false);
      }
    } finally {
      if (version === this.favoriteRequestVersion) {
        this.favoriteLoading.set(false);
      }
    }
  }

  async toggleFavorite(): Promise<void> {
    const mediaId = this.mediaId();

    if (!mediaId || this.favoriteLoading() || this.favoriteSavingMediaIds.has(mediaId)) {
      return;
    }

    const version = this.favoriteRequestVersion;
    const shouldAdd = !this.isFavorite();

    this.favoriteSavingMediaIds.add(mediaId);
    this.favoriteSaving.set(true);

    try {
      if (shouldAdd) {
        await this.favoritesService.add(mediaId);
      } else {
        await this.favoritesService.remove(mediaId);
      }

      if (version === this.favoriteRequestVersion && this.mediaId() === mediaId) {
        this.isFavorite.set(shouldAdd);
      }
    } catch {
      if (version === this.favoriteRequestVersion && this.mediaId() === mediaId) {
        void this.refreshFavorite(mediaId);
      }
    } finally {
      this.favoriteSavingMediaIds.delete(mediaId);
      this.favoriteSaving.set(
        this.favoriteSavingMediaIds.has(this.mediaId() ?? ''),
      );
    }
  }

  private async loadCurrentMedia(): Promise<void> {
    const index = this.currentIndex();

    const item =
      this.monthMedia()[index];

    if (!item) {
      throw new Error('Mídia inválida.');
    }

    const media = await firstValueFrom(
      this.http.get<MediaResponse>(
        `/api/fotos/media/${item.id}`,
      ),
    );

    this.media.set(media);

    void this.refreshFavorite(media.id);

    await this.loadMediaBlob(media);
  }

  private async loadMediaBlob(
    media: MediaResponse,
  ): Promise<void> {
    const derivative =
      media.media_type === 'image' && media.is_animated
        ? 'original'
        : 'preview';

    const blob = await firstValueFrom(
      this.http.get(
        `/api/fotos/media/${media.id}/${derivative}`,
        {
          responseType: 'blob',
        },
      ),
    );

    this.revokeObjectUrl();

    this.objectUrl =
      URL.createObjectURL(blob);

    this.mediaUrl.set(this.objectUrl);
  }

  private revokeObjectUrl(): void {
    if (!this.objectUrl) {
      return;
    }

    URL.revokeObjectURL(
      this.objectUrl,
    );

    this.objectUrl = null;
  }

  private resetTouch(): void {
    this.touchStartX = null;
    this.touchStartY = null;
  }
}
