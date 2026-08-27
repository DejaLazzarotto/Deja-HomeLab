/*
 * Deja Chamados
 *
 * Clients Presentation
 *
 * Card de resumo de um cliente.
 */

import { ChangeDetectionStrategy, Component, computed, input, output } from '@angular/core';

import { Client } from '../../domain';

import { formatDocument, formatPhone } from '../client-form/client-mask.utils';

@Component({
  selector: 'deja-client-card',
  standalone: true,
  templateUrl: './client-card.html',
  styleUrl: './client-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClientCardComponent {
  readonly client = input.required<Client>();

  readonly canManage = input(false);

  readonly deleting = input(false);

  readonly edit = output<Client>();

  readonly delete = output<string>();

  readonly formattedDocument = computed(() => formatDocument(this.client().document));

  readonly formattedPhone = computed(() => formatPhone(this.client().phone));

  readonly formattedWhatsapp = computed(() => formatPhone(this.client().whatsapp));

  onEdit(): void {
    if (this.canManage() && !this.deleting()) {
      this.edit.emit(this.client());
    }
  }

  onDelete(): void {
    if (this.canManage() && !this.deleting()) {
      this.delete.emit(this.client().id);
    }
  }
}
