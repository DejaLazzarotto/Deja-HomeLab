import {
  InvalidTicketError,
} from './invalid-ticket.error';

import {
  TicketCreateInput,
} from './ticket';

import {
  TicketValidator,
} from './ticket-validator';

describe('TicketValidator', () => {

  const validator = new TicketValidator();

  const validInput: TicketCreateInput = {
    environmentId:
      '33333333-3333-4333-8333-333333333333',
    clientId:
      '44444444-4444-4444-8444-444444444444',
    title: ' Falha no acesso ao sistema ',
    description: ' Usuário não consegue acessar o sistema. ',
    priority: 'high',
    assignedToUserId:
      '55555555-5555-4555-8555-555555555555',
  };

  it('normaliza os dados de abertura', () => {
    expect(
      validator.validateCreate(validInput),
    ).toEqual({
      ...validInput,
      title: 'Falha no acesso ao sistema',
      description:
        'Usuário não consegue acessar o sistema.',
    });
  });

  it('aceita chamado sem responsável', () => {
    expect(
      validator.validateCreate({
        ...validInput,
        assignedToUserId: null,
      }).assignedToUserId,
    ).toBeNull();
  });

  it('rejeita ambiente com UUID inválido', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        environmentId: 'ambiente-invalido',
      }),
    ).toThrowError(InvalidTicketError);
  });

  it('rejeita cliente com UUID inválido', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        clientId: 'cliente-invalido',
      }),
    ).toThrowError(InvalidTicketError);
  });

  it('rejeita responsável com UUID inválido', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        assignedToUserId: 'usuario-invalido',
      }),
    ).toThrowError(InvalidTicketError);
  });

  it('rejeita título vazio', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        title: '   ',
      }),
    ).toThrowError(
      'O título do chamado é obrigatório.',
    );
  });

  it('rejeita título acima do limite', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        title: 'a'.repeat(151),
      }),
    ).toThrowError(
      'O título do chamado deve possuir no máximo 150 caracteres.',
    );
  });

  it('rejeita descrição vazia', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        description: '   ',
      }),
    ).toThrowError(
      'A descrição do chamado é obrigatória.',
    );
  });

  it('rejeita descrição acima do limite', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        description: 'a'.repeat(5001),
      }),
    ).toThrowError(
      'A descrição do chamado deve possuir no máximo 5000 caracteres.',
    );
  });

  it('rejeita prioridade desconhecida', () => {
    expect(() =>
      validator.validateCreate({
        ...validInput,
        priority: 'urgent' as never,
      }),
    ).toThrowError(
      'A prioridade do chamado é inválida.',
    );
  });

  it('valida e normaliza uma edição', () => {
    expect(
      validator.validateUpdate({
        title: ' Título atualizado ',
        description: ' Descrição atualizada ',
        priority: 'critical',
        assignedToUserId: null,
      }),
    ).toEqual({
      title: 'Título atualizado',
      description: 'Descrição atualizada',
      priority: 'critical',
      assignedToUserId: null,
    });
  });

  it('aceita um status conhecido', () => {
    expect(
      validator.validateStatus({
        status: 'in_progress',
      }),
    ).toEqual({
      status: 'in_progress',
    });
  });

  it('rejeita status desconhecido', () => {
    expect(() =>
      validator.validateStatus({
        status: 'cancelled' as never,
      }),
    ).toThrowError(
      'O status do chamado é inválido.',
    );
  });

});