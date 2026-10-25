import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { MusicLibraryService } from './music-library.service';

describe('MusicLibraryService', () => {
  let service: MusicLibraryService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(MusicLibraryService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    TestBed.resetTestingModule();
  });

  it('lista as músicas disponíveis na API', async () => {
    const promise = service.listTracks();

    const request = http.expectOne('/api/fotos/music');

    expect(request.request.method).toBe('GET');

    request.flush({
      tracks: ['primeira.mp3', 'segunda.mp3'],
    });

    expect(await promise).toEqual([
      'primeira.mp3',
      'segunda.mp3',
    ]);
  });

  it('carrega um MP3 como Blob', async () => {
    const promise = service.loadTrack('minha música.mp3');

    const request = http.expectOne(
      '/api/fotos/music/minha%20m%C3%BAsica.mp3',
    );

    expect(request.request.method).toBe('GET');
    expect(request.request.responseType).toBe('blob');

    const audio = new Blob(['audio'], {
      type: 'audio/mpeg',
    });

    request.flush(audio);

    expect(await promise).toBe(audio);
  });
});
