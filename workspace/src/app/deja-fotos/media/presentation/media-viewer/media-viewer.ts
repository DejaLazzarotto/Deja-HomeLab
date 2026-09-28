import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, HostListener, OnDestroy, effect, inject, input, output, signal, untracked } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { Media } from '../../domain';

@Component({
  selector: 'deja-media-viewer',
  standalone: true,
  templateUrl: './media-viewer.html',
  styleUrl: './media-viewer.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MediaViewerComponent implements OnDestroy {
  readonly media = input.required<Media>();
  readonly closed = output<void>();
  readonly url = signal<string | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  private readonly http = inject(HttpClient);
  private request = 0;
  private destroyed = false;

  constructor() {
    effect(() => {
      const media = this.media();
      untracked(() => { void this.load(media); });
    });
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.closed.emit();
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.request++;
    this.releaseUrl();
  }

  private async load(media: Media): Promise<void> {
    const request = ++this.request;
    this.releaseUrl();
    this.loading.set(true);
    this.error.set(null);
    try {
      const blob = await firstValueFrom(this.http.get(
        `/api/fotos/media/${media.id}/preview`, { responseType: 'blob' },
      ));
      if (this.destroyed || request !== this.request) return;
      this.url.set(URL.createObjectURL(blob));
    } catch {
      if (!this.destroyed && request === this.request) {
        this.error.set('Não foi possível abrir a mídia. Tente novamente.');
      }
    } finally {
      if (!this.destroyed && request === this.request) this.loading.set(false);
    }
  }

  private releaseUrl(): void {
    const url = this.url();
    if (url) URL.revokeObjectURL(url);
    this.url.set(null);
  }
}
