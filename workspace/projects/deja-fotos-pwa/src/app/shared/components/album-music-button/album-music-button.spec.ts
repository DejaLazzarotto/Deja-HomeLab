import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { MusicPlayerService } from '../../../core/music/music-player.service';
import { AlbumMusicButtonComponent } from './album-music-button';

describe('AlbumMusicButtonComponent', () => {
  let fixture: ComponentFixture<AlbumMusicButtonComponent>;

  const isPlaying = signal(false);
  const isLoading = signal(false);

  const music = {
    isPlaying,
    isLoading,
    play: vi.fn().mockResolvedValue(undefined),
    pause: vi.fn(),
  };

  beforeEach(async () => {
    isPlaying.set(false);
    isLoading.set(false);
    vi.clearAllMocks();

    await TestBed.configureTestingModule({
      imports: [AlbumMusicButtonComponent],
      providers: [
        { provide: MusicPlayerService, useValue: music },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AlbumMusicButtonComponent);
    fixture.detectChanges();
  });

  it('mostra Play quando a música está pausada', () => {
    const button = fixture.nativeElement.querySelector('button');

    expect(button.getAttribute('aria-label')).toBe('Reproduzir música');
    expect(button.textContent).toContain('▶');
  });

  it('mostra Pause durante a reprodução', () => {
    isPlaying.set(true);
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('button');

    expect(button.getAttribute('aria-label')).toBe('Pausar música');
    expect(button.textContent).toContain('Ⅱ');
  });

  it('permite pausar durante o carregamento', () => {
    isLoading.set(true);
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('button');

    expect(button.getAttribute('aria-label')).toBe('Pausar música');

    button.click();

    expect(music.pause).toHaveBeenCalledOnce();
    expect(music.play).not.toHaveBeenCalled();
  });

  it('executa Play quando está pausado', () => {
    const button = fixture.nativeElement.querySelector('button');

    button.click();

    expect(music.play).toHaveBeenCalledOnce();
    expect(music.pause).not.toHaveBeenCalled();
  });
});
