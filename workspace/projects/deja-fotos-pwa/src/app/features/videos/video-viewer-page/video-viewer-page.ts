import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import {
  firstValueFrom,
} from 'rxjs';

interface MediaResponse {
  id: string;
  media_type: 'image' | 'video';
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
  selector: 'app-video-viewer-page',
  standalone: true,
  templateUrl: './video-viewer-page.html',
  styleUrl: './video-viewer-page.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class VideoViewerPageComponent
  implements OnInit, OnDestroy {
  private readonly http =
    inject(HttpClient);

  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);

  private objectUrl:
    string | null = null;

  private touchStartX:
    number | null = null;

  private touchStartY:
    number | null = null;

  private currentPage = 0;

  private totalPages = 0;

  private loadingMore = false;

  readonly year =
    signal<number | null>(null);

  readonly mediaId =
    signal<string | null>(null);

  readonly media =
    signal<MediaResponse | null>(null);

  readonly videos =
    signal<readonly MediaResponse[]>([]);

  readonly currentIndex =
    signal(-1);

  readonly mediaUrl =
    signal<string | null>(null);

  readonly loading =
    signal(true);

  readonly error =
    signal<string | null>(null);

  readonly total =
    signal(0);

  async ngOnInit(): Promise<void> {
    const yearParam =
      this.route.snapshot.paramMap.get(
        'year',
      );

    const mediaId =
      this.route.snapshot.paramMap.get(
        'mediaId',
      );

    const selectedYear =
      Number(yearParam);

    if (
      !yearParam
      || !mediaId
      || !Number.isInteger(selectedYear)
      || selectedYear < 1
      || selectedYear > 9999
    ) {
      this.error.set(
        'Vídeo inválido.',
      );

      this.loading.set(false);

      return;
    }

    this.year.set(selectedYear);
    this.mediaId.set(mediaId);

    try {
      await this.loadUntilMediaFound(
        mediaId,
      );

      await this.loadCurrentMedia();
    } catch {
      this.error.set(
        'Não foi possível carregar o vídeo.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  ngOnDestroy(): void {
    this.revokeObjectUrl();
  }

  goBack(): void {
    const selectedYear =
      this.year();

    if (selectedYear === null) {
      void this.router.navigateByUrl(
        '/videos',
      );

      return;
    }

    void this.router.navigate(
      [
        '/videos',
        selectedYear,
      ],
    );
  }

  async showPrevious(): Promise<void> {
    const index =
      this.currentIndex();

    if (index <= 0) {
      return;
    }

    await this.changeMedia(
      index - 1,
    );
  }

  async showNext(): Promise<void> {
    const index =
      this.currentIndex();

    const items =
      this.videos();

    if (index < 0) {
      return;
    }

    if (
      index
      >= items.length
        - PREFETCH_THRESHOLD
    ) {
      await this.loadNextPage();
    }

    const updatedItems =
      this.videos();

    if (
      index
      >= updatedItems.length - 1
    ) {
      return;
    }

    await this.changeMedia(
      index + 1,
    );
  }

  onTouchStart(
    event: TouchEvent,
  ): void {
    const touch =
      event.changedTouches[0];

    if (!touch) {
      return;
    }

    this.touchStartX =
      touch.clientX;

    this.touchStartY =
      touch.clientY;
  }

  async onTouchEnd(
    event: TouchEvent,
  ): Promise<void> {
    if (
      this.touchStartX === null
      || this.touchStartY === null
    ) {
      return;
    }

    const touch =
      event.changedTouches[0];

    if (!touch) {
      this.resetTouch();

      return;
    }

    const deltaX =
      touch.clientX
      - this.touchStartX;

    const deltaY =
      touch.clientY
      - this.touchStartY;

    this.resetTouch();

    const minimumSwipeDistance =
      50;

    if (
      Math.abs(deltaX)
      < minimumSwipeDistance
    ) {
      return;
    }

    if (
      Math.abs(deltaX)
      <= Math.abs(deltaY)
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
        this.videos().findIndex(
          item =>
            item.id === mediaId,
        );

      if (index >= 0) {
        this.currentIndex.set(
          index,
        );

        return;
      }

      if (
        page >= this.totalPages
      ) {
        throw new Error(
          'Vídeo não encontrado no ano.',
        );
      }

      page += 1;
    }
  }

  private async loadNextPage():
    Promise<void> {
    if (
      this.loadingMore
      || this.currentPage
        >= this.totalPages
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
    const selectedYear =
      this.year();

    if (selectedYear === null) {
      throw new Error(
        'Ano inválido.',
      );
    }

    const response =
      await firstValueFrom(
        this.http.get<
          MediaListResponse
        >(
          '/api/fotos/media',
          {
            params: {
              media_type:
                'video',
              original_year:
                selectedYear,
              page,
              page_size:
                PAGE_SIZE,
            },
          },
        ),
      );

    if (page === 1) {
      this.videos.set(
        response.items,
      );
    } else {
      this.videos.update(
        current => [
          ...current,
          ...response.items,
        ],
      );
    }

    this.currentPage =
      response.page;

    this.totalPages =
      response.total_pages;

    this.total.set(
      response.total,
    );
  }

  private async changeMedia(
    index: number,
  ): Promise<void> {
    const item =
      this.videos()[index];

    if (!item) {
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    try {
      this.currentIndex.set(
        index,
      );

      this.mediaId.set(
        item.id,
      );

      await this.loadCurrentMedia();

      const selectedYear =
        this.year();

      if (
        selectedYear !== null
      ) {
        await this.router.navigate(
          [
            '/videos',
            selectedYear,
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
        'Não foi possível carregar o vídeo.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  private async loadCurrentMedia():
    Promise<void> {
    const index =
      this.currentIndex();

    const item =
      this.videos()[index];

    if (!item) {
      throw new Error(
        'Vídeo inválido.',
      );
    }

    const media =
      await firstValueFrom(
        this.http.get<
          MediaResponse
        >(
          `/api/fotos/media/${item.id}`,
        ),
      );

    if (
      media.media_type
      !== 'video'
    ) {
      throw new Error(
        'Mídia não é vídeo.',
      );
    }

    this.media.set(media);

    await this.loadMediaBlob(
      media,
    );
  }

  private async loadMediaBlob(
    media: MediaResponse,
  ): Promise<void> {
    const blob =
      await firstValueFrom(
        this.http.get(
          `/api/fotos/media/${media.id}/preview`,
          {
            responseType:
              'blob',
          },
        ),
      );

    this.revokeObjectUrl();

    this.objectUrl =
      URL.createObjectURL(
        blob,
      );

    this.mediaUrl.set(
      this.objectUrl,
    );
  }

  private revokeObjectUrl():
    void {
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