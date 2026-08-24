/*
 * Deja Chamados
 *
 * Clients Presentation
 *
 * Listagem visual dos clientes.
 */

import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

import { Client } from '../../domain';

import { ClientCardComponent } from '../client-card/client-card';

@Component({
  selector: 'deja-client-list',
  standalone: true,
  imports: [ClientCardComponent],
  templateUrl: './client-list.html',
  styleUrl: './client-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClientListComponent {
  readonly clients = input.required<readonly Client[]>();

  readonly loading = input(false);

  readonly canManage = input(false);

  readonly deletingClientId = input<string | null>(null);

  readonly edit = output<Client>();

  readonly delete = output<string>();
}
