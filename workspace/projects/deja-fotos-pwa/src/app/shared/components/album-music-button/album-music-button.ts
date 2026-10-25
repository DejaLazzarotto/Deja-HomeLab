import {
  ChangeDetectionStrategy,
  Component,
  inject,
} from '@angular/core';

import { MusicPlayerService } from '../../../core/music/music-player.service';

@Component({
  selector: 'app-album-music-button',
  standalone: true,
  template: `
    <button
      class="music-button"
      type="button"
      [attr.aria-label]="(music.isPlaying() || music.isLoading()) ? 'Pausar música' : 'Reproduzir música'"
      [attr.aria-pressed]="music.isPlaying() || music.isLoading()"
      (click)="toggle()"
    >
      @if (music.isPlaying() || music.isLoading()) {
        <span aria-hidden="true">Ⅱ</span>
      } @else {
        <span aria-hidden="true">▶</span>
      }
    </button>
  `,
  styles: [`
    .music-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      padding: 0;
      border: 1px solid rgba(255, 255, 255, 0.65);
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.15);
      color: inherit;
      font-size: 18px;
      cursor: pointer;
    }

    .music-button:focus-visible {
      outline: 2px solid currentColor;
      outline-offset: 3px;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlbumMusicButtonComponent {
  readonly music = inject(MusicPlayerService);

  toggle(): void {
    if (this.music.isPlaying() || this.music.isLoading()) {
      this.music.pause();
    } else {
      void this.music.play();
    }
  }
}
