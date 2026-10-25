import { DestroyRef, inject, Injectable, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

import { MusicPlayerService } from '../music-player.service';

@Injectable({ providedIn: 'root' })
export class AlbumMusicController {
  private readonly router = inject(Router);
  private readonly player = inject(MusicPlayerService);
  private readonly destroyRef = inject(DestroyRef);

  readonly activeAlbumId = signal<string | null>(null);

  constructor() {
    this.updateAlbum(this.router.url);

    this.router.events
      .pipe(
        filter((event): event is NavigationEnd => event instanceof NavigationEnd),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((event) => {
        this.updateAlbum(event.urlAfterRedirects);
      });
  }

  private updateAlbum(url: string): void {
    const path = url.split(/[?#]/, 1)[0];
    const match = /^\/albums\/([^/]+)(?:\/|$)/.exec(path);
    const albumId = match ? decodeURIComponent(match[1]) : null;

    if (albumId === this.activeAlbumId()) {
      return;
    }

    this.activeAlbumId.set(albumId);

    if (albumId === null) {
      this.player.stop();
      return;
    }

    void this.player.initialize();
  }
}
