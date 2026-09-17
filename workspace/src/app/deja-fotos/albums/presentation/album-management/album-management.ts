/*
 * Deja Fotos
 *
 * Album Management
 */

import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  computed,
  input,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  FotosEnvironmentOption,
} from '../../../fotos-environment-option';

import {
  AlbumService,
} from '../../application';

import {
  Album,
  AlbumFilters,
  AlbumInput,
} from '../../domain';

import {
  AlbumFormComponent,
} from '../album-form/album-form';

type AlbumActiveFilter =
  | 'all'
  | 'active'
  | 'inactive';

@Component({
  selector: 'deja-album-management',
  standalone: true,
  imports: [
    FormsModule,
    AlbumFormComponent,
  ],
  templateUrl: './album-management.html',
  styleUrl: './album-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlbumManagementComponent implements OnInit {
  readonly service = input.required<AlbumService>();

  readonly environments =
    input<readonly FotosEnvironmentOption[]>([]);

  readonly defaultEnvironmentId =
    input<string | null>(null);

  readonly canEdit = input(false);

  readonly canDelete = input(false);

  readonly albums = signal<readonly Album[]>([]);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly deletingAlbumId =
    signal<string | null>(null);

  readonly errorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  readonly operationError =
    signal<string | null>(null);

  readonly searchTerm = signal('');

  readonly environmentFilter = signal('');

  readonly activeFilter =
    signal<AlbumActiveFilter>('all');

  readonly selectedAlbum =
    signal<Album | null>(null);

  readonly formVisible = signal(false);

  readonly visibleAlbums = computed(() => {
    const search = this.searchTerm()
      .trim()
      .toLocaleLowerCase('pt-BR');

    if (!search) {
      return this.albums();
    }

    return this.albums().filter(album => (
      album.name
        .toLocaleLowerCase('pt-BR')
        .includes(search)
      || (
        album.description
          ?.toLocaleLowerCase('pt-BR')
          .includes(search)
        ?? false
      )
    ));
  });

  private requestSequence = 0;

  ngOnInit(): void {
    const defaultEnvironmentId =
      this.defaultEnvironmentId();

    if (defaultEnvironmentId) {
      this.environmentFilter.set(
        defaultEnvironmentId,
      );
    }

    void this.refresh();
  }

  async refresh(): Promise<void> {
    const requestSequence =
      this.requestSequence + 1;

    this.requestSequence = requestSequence;

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const albums = await this.service().list(
        this.createFilters(),
      );

      if (requestSequence === this.requestSequence) {
        this.albums.set(albums);
      }
    } catch {
      if (requestSequence === this.requestSequence) {
        this.errorMessage.set(
          'Não foi possível carregar os álbuns.',
        );
      }
    } finally {
      if (requestSequence === this.requestSequence) {
        this.loading.set(false);
      }
    }
  }

  applyFilters(): void {
    this.closeForm();

    void this.refresh();
  }

  clearFilters(): void {
    this.searchTerm.set('');
    this.environmentFilter.set(
      this.defaultEnvironmentId() ?? '',
    );
    this.activeFilter.set('all');

    this.applyFilters();
  }

  openCreate(): void {
    if (!this.canEdit()) {
      return;
    }

    this.selectedAlbum.set(null);
    this.clearOperationMessages();
    this.formVisible.set(true);
    this.scrollToForm();
  }

  openEdit(
    album: Album,
  ): void {
    if (!this.canEdit()) {
      return;
    }

    this.selectedAlbum.set(album);
    this.clearOperationMessages();
    this.formVisible.set(true);
    this.scrollToForm();
  }

  closeForm(): void {
    if (this.saving()) {
      return;
    }

    this.selectedAlbum.set(null);
    this.formVisible.set(false);
  }

  async saveAlbum(
    input: AlbumInput,
  ): Promise<void> {
    if (
      !this.canEdit()
      || this.saving()
    ) {
      return;
    }

    this.saving.set(true);
    this.clearOperationMessages();

    try {
      const selectedAlbum =
        this.selectedAlbum();

      if (selectedAlbum) {
        await this.service().update(
          selectedAlbum.id,
          input,
        );

        this.operationMessage.set(
          'Álbum atualizado com sucesso.',
        );
      } else {
        await this.service().create(input);

        this.operationMessage.set(
          'Álbum criado com sucesso.',
        );
      }

      this.selectedAlbum.set(null);
      this.formVisible.set(false);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  async deleteAlbum(
    album: Album,
  ): Promise<void> {
    if (
      !this.canDelete()
      || this.deletingAlbumId()
    ) {
      return;
    }

    if (
      !window.confirm(
        `Excluir o álbum "${album.name}"? A exclusão só será permitida se ele estiver vazio.`,
      )
    ) {
      return;
    }

    this.deletingAlbumId.set(album.id);
    this.clearOperationMessages();

    try {
      await this.service().delete(album.id);

      if (
        this.selectedAlbum()?.id === album.id
      ) {
        this.selectedAlbum.set(null);
        this.formVisible.set(false);
      }

      this.operationMessage.set(
        'Álbum excluído com sucesso.',
      );

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.deletingAlbumId.set(null);
    }
  }

  environmentName(
    environmentId: string,
  ): string {
    return this.environments().find(
      environment => environment.id === environmentId,
    )?.name ?? environmentId;
  }

  formatDate(
    value: string,
  ): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return 'Data inválida';
    }

    return new Intl.DateTimeFormat(
      'pt-BR',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      },
    ).format(date);
  }

  private createFilters(): AlbumFilters {
    const activeFilter = this.activeFilter();

    return {
      environmentId:
        this.environmentFilter() || undefined,
      active:
        activeFilter === 'all'
          ? undefined
          : activeFilter === 'active',
    };
  }

  private clearOperationMessages(): void {
    this.operationMessage.set(null);
    this.operationError.set(null);
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error
        ? error.message
        : 'Não foi possível concluir a operação.';
    }

    if (error.status === 0) {
      return 'Não foi possível acessar a API.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'O álbum não foi encontrado.';
    }

    if (error.status === 409) {
      return 'O álbum não pode ser excluído enquanto possuir mídias associadas.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

  private scrollToForm(): void {
    setTimeout(() => {
      document
        .querySelector('deja-album-form')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
    });
  }
}