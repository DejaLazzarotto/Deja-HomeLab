/*
 * Deja Fotos
 *
 * Album Form
 */

import {
  ChangeDetectionStrategy,
  Component,
  effect,
  input,
  output,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  FotosEnvironmentOption,
} from '../../../fotos-environment-option';

import {
  Album,
  AlbumInput,
} from '../../domain';

@Component({
  selector: 'deja-album-form',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './album-form.html',
  styleUrl: './album-form.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlbumFormComponent {
  readonly album = input<Album | null>(null);

  readonly environments =
    input<readonly FotosEnvironmentOption[]>([]);

  readonly defaultEnvironmentId =
    input<string | null>(null);

  readonly saving = input(false);

  readonly submitted = output<AlbumInput>();

  readonly cancelled = output<void>();

  protected readonly environmentId = signal('');

  protected readonly name = signal('');

  protected readonly description = signal('');

  protected readonly active = signal(true);

  protected readonly validationMessage =
    signal<string | null>(null);

  constructor() {
    effect(() => {
      const album = this.album();

      this.environmentId.set(
        album?.environmentId
        ?? this.defaultEnvironmentId()
        ?? this.environments()[0]?.id
        ?? '',
      );
      this.name.set(album?.name ?? '');
      this.description.set(
        album?.description ?? '',
      );
      this.active.set(album?.active ?? true);
      this.validationMessage.set(null);
    });
  }

  protected submit(): void {
    const environmentId =
      this.environmentId().trim();

    const name = this.name().trim();

    const description =
      this.description().trim();

    if (!environmentId) {
      this.validationMessage.set(
        'Selecione o ambiente do álbum.',
      );

      return;
    }

    if (!name) {
      this.validationMessage.set(
        'Informe o nome do álbum.',
      );

      return;
    }

    if (name.length > 150) {
      this.validationMessage.set(
        'O nome deve possuir no máximo 150 caracteres.',
      );

      return;
    }

    if (description.length > 5000) {
      this.validationMessage.set(
        'A descrição deve possuir no máximo 5.000 caracteres.',
      );

      return;
    }

    this.validationMessage.set(null);

    this.submitted.emit({
      environmentId,
      name,
      description: description || null,
      active: this.active(),
    });
  }

  protected cancel(): void {
    if (!this.saving()) {
      this.cancelled.emit();
    }
  }
}