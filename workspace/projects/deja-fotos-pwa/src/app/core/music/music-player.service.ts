import { inject, Injectable, signal } from '@angular/core';

import { MusicLibraryService } from './music-library.service';
import { shuffleTracks } from './shuffle-tracks';

@Injectable({
  providedIn: 'root',
})
export class MusicPlayerService {
  private readonly library = inject(MusicLibraryService);
  private readonly audio = new Audio();

  readonly isPlaying = signal(false);
  readonly isLoading = signal(false);
  readonly error = signal<string | null>(null);

  private tracks: string[] = [];
  private queue: string[] = [];
  private currentTrack: string | null = null;
  private objectUrl: string | null = null;
  private requestVersion = 0;

  constructor() {
    this.audio.addEventListener('ended', () => {
      void this.playNext();
    });

    this.audio.addEventListener('pause', () => {
      this.isPlaying.set(false);
    });

    this.audio.addEventListener('play', () => {
      this.isPlaying.set(true);
    });
  }

  async initialize(): Promise<void> {
    this.stop();

    const version = this.requestVersion;
    this.isLoading.set(true);

    try {
      const tracks = await this.library.listTracks();

      if (version !== this.requestVersion) {
        return;
      }

      this.tracks = [...new Set(tracks)];
      this.queue = shuffleTracks(this.tracks);

      if (this.tracks.length === 0) {
        this.error.set('Nenhuma música disponível.');
        return;
      }

      await this.playNext();
    } catch {
      if (version === this.requestVersion) {
        this.error.set('Não foi possível carregar as músicas.');
      }
    } finally {
      if (version === this.requestVersion) {
        this.isLoading.set(false);
      }
    }
  }

  async play(): Promise<void> {
    if (this.currentTrack && this.objectUrl) {
      try {
        await this.audio.play();
        this.error.set(null);
      } catch {
        this.isPlaying.set(false);
      }
      return;
    }

    await this.playNext();
  }

  pause(): void {
    this.resumeAfterVideo = false;
    this.requestVersion++;
    this.audio.pause();
    this.isPlaying.set(false);
    this.isLoading.set(false);
  }

  private resumeAfterVideo = false;

  pauseForVideo(): void {
    this.resumeAfterVideo = this.isPlaying() || this.isLoading();

    if (this.resumeAfterVideo) {
      this.pause();
      this.resumeAfterVideo = true;
    }
  }

  resumeFromVideo(): void {
    if (!this.resumeAfterVideo) {
      return;
    }

    this.resumeAfterVideo = false;
    void this.play();
  }
  stop(): void {
    this.resumeAfterVideo = false;
    this.requestVersion++;
    this.audio.pause();
    this.audio.removeAttribute('src');
    this.audio.load();

    this.revokeObjectUrl();

    this.currentTrack = null;
    this.tracks = [];
    this.queue = [];

    this.isPlaying.set(false);
    this.isLoading.set(false);
    this.error.set(null);
  }

  private async playNext(): Promise<void> {
    const version = ++this.requestVersion;

    if (this.queue.length === 0) {
      this.queue = shuffleTracks(this.tracks);

      if (
        this.tracks.length > 1 &&
        this.queue[0] === this.currentTrack
      ) {
        const lastIndex = this.queue.length - 1;

        [this.queue[0], this.queue[lastIndex]] = [
          this.queue[lastIndex],
          this.queue[0],
        ];
      }
    }

    const nextTrack = this.queue.shift();

    if (!nextTrack) {
      this.isPlaying.set(false);
      return;
    }

    this.isLoading.set(true);

    try {
      const blob = await this.library.loadTrack(nextTrack);

      if (version !== this.requestVersion) {
        if (this.tracks.includes(nextTrack)) {
          this.queue.unshift(nextTrack);
        }
        return;
      }

      this.audio.pause();
      this.revokeObjectUrl();

      this.objectUrl = URL.createObjectURL(blob);
      this.audio.src = this.objectUrl;
      this.currentTrack = nextTrack;

      await this.audio.play();

      if (version === this.requestVersion) {
        this.error.set(null);
      }
    } catch {
      if (version === this.requestVersion) {
        this.isPlaying.set(false);
        this.error.set('Não foi possível reproduzir a música.');
      }
    } finally {
      if (version === this.requestVersion) {
        this.isLoading.set(false);
      }
    }
  }

  private revokeObjectUrl(): void {
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
      this.objectUrl = null;
    }
  }
}
