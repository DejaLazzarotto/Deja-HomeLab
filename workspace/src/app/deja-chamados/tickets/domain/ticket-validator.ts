/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Valida e normaliza os dados enviados para a API.
 */

import {
  InvalidTicketError,
} from './invalid-ticket.error';

import {
  TicketCreateInput,
  TicketPriority,
  TicketStatus,
  TicketStatusInput,
  TicketUpdateInput,
} from './ticket';

const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

const TICKET_PRIORITIES: readonly TicketPriority[] = [
  'low',
  'medium',
  'high',
  'critical',
];

const TICKET_STATUSES: readonly TicketStatus[] = [
  'open',
  'in_progress',
  'pending',
  'closed',
];

export class TicketValidator {

  validateCreate(
    input: TicketCreateInput,
  ): TicketCreateInput {
    this.validateUuid(
      input.environmentId,
      'O ambiente',
    );

    this.validateUuid(
      input.clientId,
      'O cliente',
    );

    this.validateAssignedUserId(
      input.assignedToUserId,
    );

    return {
      environmentId: input.environmentId,
      clientId: input.clientId,
      title: this.validateTitle(input.title),
      description: this.validateDescription(
        input.description,
      ),
      priority: this.validatePriority(
        input.priority,
      ),
      assignedToUserId: input.assignedToUserId,
    };
  }

  validateUpdate(
    input: TicketUpdateInput,
  ): TicketUpdateInput {
    this.validateAssignedUserId(
      input.assignedToUserId,
    );

    return {
      title: this.validateTitle(input.title),
      description: this.validateDescription(
        input.description,
      ),
      priority: this.validatePriority(
        input.priority,
      ),
      assignedToUserId: input.assignedToUserId,
    };
  }

  validateStatus(
    input: TicketStatusInput,
  ): TicketStatusInput {
    if (!TICKET_STATUSES.includes(input.status)) {
      throw new InvalidTicketError(
        'O status do chamado é inválido.',
      );
    }

    return {
      status: input.status,
    };
  }

  private validateTitle(
    value: string,
  ): string {
    const title = value.trim();

    if (!title) {
      throw new InvalidTicketError(
        'O título do chamado é obrigatório.',
      );
    }

    if (title.length > 150) {
      throw new InvalidTicketError(
        'O título do chamado deve possuir no máximo 150 caracteres.',
      );
    }

    return title;
  }

  private validateDescription(
    value: string,
  ): string {
    const description = value.trim();

    if (!description) {
      throw new InvalidTicketError(
        'A descrição do chamado é obrigatória.',
      );
    }

    if (description.length > 5000) {
      throw new InvalidTicketError(
        'A descrição do chamado deve possuir no máximo 5000 caracteres.',
      );
    }

    return description;
  }

  private validatePriority(
    value: TicketPriority,
  ): TicketPriority {
    if (!TICKET_PRIORITIES.includes(value)) {
      throw new InvalidTicketError(
        'A prioridade do chamado é inválida.',
      );
    }

    return value;
  }

  private validateAssignedUserId(
    value: string | null,
  ): void {
    if (value === null) {
      return;
    }

    this.validateUuid(
      value,
      'O responsável',
    );
  }

  private validateUuid(
    value: string,
    fieldName: string,
  ): void {
    if (!UUID_PATTERN.test(value)) {
      throw new InvalidTicketError(
        `${fieldName} deve possuir um UUID válido.`,
      );
    }
  }

}