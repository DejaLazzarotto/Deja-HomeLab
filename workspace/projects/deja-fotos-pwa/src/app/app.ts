import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { AlbumMusicController } from './core/music/album-music-controller/album-music-controller';
import { AlbumMusicButtonComponent } from './shared/components/album-music-button/album-music-button';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, AlbumMusicButtonComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected readonly title = signal('deja-fotos-pwa');
  protected readonly albumMusic = inject(AlbumMusicController);
}
