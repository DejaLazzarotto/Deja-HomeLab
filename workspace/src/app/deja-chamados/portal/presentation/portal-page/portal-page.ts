import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  AuthenticationService,
} from '../../../../platform/authentication/application/authentication.service';

import {
  PortalTicket,
  PortalTicketCreate,
} from '../../domain/portal-ticket';

import {
  PortalComposition,
} from '../../portal-composition';

import {
  PortalTicketFormComponent,
} from '../portal-ticket-form/portal-ticket-form';

@Component({
  selector: 'deja-portal-page',
  standalone: true,
  imports: [
    PortalTicketFormComponent,
  ],
  templateUrl: './portal-page.html',
  styleUrl: './portal-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PortalPageComponent implements OnInit {
  private readonly authentication =
    inject(AuthenticationService);

  private readonly http =
    inject(HttpClient);

  private readonly composition =
    new PortalComposition(
      this.http,
    );

  readonly user =
    this.authentication.user;

  readonly tickets =
    signal<readonly PortalTicket[]>([]);

  readonly loading =
    signal(false);

  readonly creating =
    signal(false);

  readonly formVisible =
    signal(false);

  readonly errorMessage =
    signal('');

  readonly createErrorMessage =
    signal('');

  ngOnInit(): void {
    void this.loadTickets();
  }

  async loadTickets(): Promise<void> {
    if (this.loading()) {
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');

    try {
      const tickets =
        await this.composition.service.list();

      this.tickets.set(tickets);
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar os chamados.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openForm(): void {
    if (this.creating()) {
      return;
    }

    this.createErrorMessage.set('');
    this.formVisible.set(true);
  }

  closeForm(): void {
    if (this.creating()) {
      return;
    }

    this.createErrorMessage.set('');
    this.formVisible.set(false);
  }

  async createTicket(
    input: PortalTicketCreate,
  ): Promise<void> {
    if (this.creating()) {
      return;
    }

    this.creating.set(true);
    this.createErrorMessage.set('');

    try {
      const ticket =
        await this.composition.service.create(input);

      this.tickets.update(
        tickets => [
          ticket,
          ...tickets,
        ],
      );

      this.formVisible.set(false);
    } catch {
      this.createErrorMessage.set(
        'Não foi possível abrir o chamado.',
      );
    } finally {
      this.creating.set(false);
    }
  }

  logout(): void {
    this.authentication.logout();

    window.location.replace('/login');
  }
}