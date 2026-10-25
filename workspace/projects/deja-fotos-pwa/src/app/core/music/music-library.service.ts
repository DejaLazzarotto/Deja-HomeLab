import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export interface MusicListResponse {
  readonly tracks: readonly string[];
}

@Injectable({
  providedIn: 'root',
})
export class MusicLibraryService {
  private readonly http = inject(HttpClient);

  async listTracks(): Promise<readonly string[]> {
    const response = await firstValueFrom(
      this.http.get<MusicListResponse>('/api/fotos/music'),
    );

    return response.tracks;
  }

  async loadTrack(filename: string): Promise<Blob> {
    return firstValueFrom(
      this.http.get(
        `/api/fotos/music/${encodeURIComponent(filename)}`,
        { responseType: 'blob' },
      ),
    );
  }
}
