import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  TicketAssigneeService,
  TicketAttachmentService,
  TicketCommentService,
  TicketService,
  TicketTimelineService,
} from '../../application';

import {
  Ticket,
  TicketAssignee,
  TicketTimelineEvent,
} from '../../domain';

import {
  TicketDetailsComponent,
} from './ticket-details';

function createTicket(
  overrides: Partial<Ticket> = {},
): Ticket {
  return {
    id: 'ticket-1',
    organizationId: 'organization-1',
    tenantId: 'tenant-1',
    environmentId: 'environment-1',
    clientId: 'client-1',
    title: 'Chamado de teste',
    description: 'Descrição de teste',
    status: 'open',
    priority: 'medium',
    openedByUserId: 'user-1',
    assignedToUserId: 'assignee-1',
    assignedToUserName: 'Rodrigo Suporte N1',
    closedByUserId: null,
    closedAt: null,
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
    ...overrides,
  };
}

function createAssignee(
  overrides: Partial<TicketAssignee> = {},
): TicketAssignee {
  return {
    id: 'assignee-1',
    name: 'Rodrigo Suporte N1',
    email: 'rodrigo@example.com',
    role: 'analyst',
    ...overrides,
  };
}

function createTimelineEvent(
  overrides: Partial<TicketTimelineEvent> = {},
): TicketTimelineEvent {
  return {
    id: 'event-1',
    ticketId: 'ticket-1',
    eventType: 'assigned_changed',
    description: null,
    previousValue: 'assignee-1',
    newValue: 'assignee-2',
    previousDisplayValue: 'Rodrigo Suporte N1',
    newDisplayValue: 'Dejair Lazzarotto',
    createdByUserId: 'user-1',
    createdAt: '2026-09-01T11:00:00.000Z',
    ...overrides,
  } as TicketTimelineEvent;
}

describe('TicketDetailsComponent', () => {

  let fixture: ComponentFixture<TicketDetailsComponent>;
  let component: TicketDetailsComponent;

  let findByIdMock: ReturnType<typeof vi.fn>;
  let updateMock: ReturnType<typeof vi.fn>;
  let updateStatusMock: ReturnType<typeof vi.fn>;

  let listAssigneesMock: ReturnType<typeof vi.fn>;

  let listTimelineMock: ReturnType<typeof vi.fn>;

  let listCommentsMock: ReturnType<typeof vi.fn>;
  let createCommentMock: ReturnType<typeof vi.fn>;

  let listAttachmentsMock: ReturnType<typeof vi.fn>;
  let uploadAttachmentMock: ReturnType<typeof vi.fn>;
  let deleteAttachmentMock: ReturnType<typeof vi.fn>;
  let downloadAttachmentMock: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    findByIdMock = vi.fn();
    updateMock = vi.fn();
    updateStatusMock = vi.fn();

    listAssigneesMock = vi.fn();

    listTimelineMock = vi.fn();

    listCommentsMock = vi.fn();
    createCommentMock = vi.fn();

    listAttachmentsMock = vi.fn();
    uploadAttachmentMock = vi.fn();
    deleteAttachmentMock = vi.fn();
    downloadAttachmentMock = vi.fn();

    const service = {
      findById: findByIdMock,
      update: updateMock,
      updateStatus: updateStatusMock,
    } as unknown as TicketService;

    const assigneeService = {
      list: listAssigneesMock,
    } as unknown as TicketAssigneeService;

    const timelineService = {
      listByTicketId: listTimelineMock,
    } as unknown as TicketTimelineService;

    const commentService = {
      listByTicketId: listCommentsMock,
      create: createCommentMock,
    } as unknown as TicketCommentService;

    const attachmentService = {
      listByTicketId: listAttachmentsMock,
      upload: uploadAttachmentMock,
      delete: deleteAttachmentMock,
      download: downloadAttachmentMock,
    } as unknown as TicketAttachmentService;

    await TestBed.configureTestingModule({
      imports: [
        TicketDetailsComponent,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      TicketDetailsComponent,
    );

    component = fixture.componentInstance;

    fixture.componentRef.setInput(
      'ticketId',
      'ticket-1',
    );

    fixture.componentRef.setInput(
      'service',
      service,
    );

    fixture.componentRef.setInput(
      'assigneeService',
      assigneeService,
    );

    fixture.componentRef.setInput(
      'timelineService',
      timelineService,
    );

    fixture.componentRef.setInput(
      'commentService',
      commentService,
    );

    fixture.componentRef.setInput(
      'attachmentService',
      attachmentService,
    );

    findByIdMock.mockResolvedValue(
      createTicket(),
    );

    listAssigneesMock.mockResolvedValue([
      createAssignee(),
    ]);

    listTimelineMock.mockResolvedValue([]);

    listCommentsMock.mockResolvedValue([]);

    listAttachmentsMock.mockResolvedValue([]);
  });

  it('carrega chamado, timeline, comentários e responsáveis', async () => {
    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    await component.loadDetails();

    expect(findByIdMock).toHaveBeenCalledWith(
      'ticket-1',
    );

    expect(listTimelineMock).toHaveBeenCalledWith(
      'ticket-1',
    );

    expect(listCommentsMock).toHaveBeenCalledWith(
      'ticket-1',
    );

    expect(listAttachmentsMock).toHaveBeenCalledWith(
      'ticket-1',
    );

    expect(listAssigneesMock).toHaveBeenCalledWith(
      'client-1',
    );

    expect(component.ticket()?.id).toBe(
      'ticket-1',
    );

    expect(component.assignees()).toHaveLength(1);

    expect(
      component.assignees()[0].name,
    ).toBe('Rodrigo Suporte N1');
  });

  it('não carrega responsáveis para usuário sem permissão de gerenciamento', async () => {
    fixture.componentRef.setInput(
      'canManage',
      false,
    );

    await component.loadDetails();

    expect(
      listAssigneesMock,
    ).not.toHaveBeenCalled();

    expect(
      component.assignees(),
    ).toEqual([]);
  });

  it('retorna somente transições válidas de status', () => {
    const ticket = createTicket({
      status: 'open',
    });

    expect(
      component.statusOptions(ticket),
    ).toEqual([
      'open',
      'in_progress',
      'pending',
      'closed',
    ]);
  });

  it('não altera status sem permissão', async () => {
    component.ticket.set(
      createTicket(),
    );

    fixture.componentRef.setInput(
      'canManage',
      false,
    );

    await component.changeStatus(
      'in_progress',
    );

    expect(
      updateStatusMock,
    ).not.toHaveBeenCalled();
  });

  it('não executa transição de status inválida', async () => {
    component.ticket.set(
      createTicket({
        status: 'closed',
      }),
    );

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    await component.changeStatus(
      'pending',
    );

    expect(
      updateStatusMock,
    ).not.toHaveBeenCalled();
  });

  it('altera status e recarrega os detalhes', async () => {
    const ticket = createTicket();

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    updateStatusMock.mockResolvedValue(
      createTicket({
        status: 'in_progress',
      }),
    );

    const loadDetailsSpy = vi
      .spyOn(component, 'loadDetails')
      .mockResolvedValue();

    await component.changeStatus(
      'in_progress',
    );

    expect(updateStatusMock).toHaveBeenCalledWith(
      ticket.id,
      {
        status: 'in_progress',
      },
    );

    expect(
      loadDetailsSpy,
    ).toHaveBeenCalledOnce();
  });

  it('altera prioridade preservando os demais dados editáveis', async () => {
    const ticket = createTicket({
      priority: 'medium',
    });

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    updateMock.mockResolvedValue(
      createTicket({
        priority: 'high',
      }),
    );

    const loadDetailsSpy = vi
      .spyOn(component, 'loadDetails')
      .mockResolvedValue();

    await component.changePriority(
      'high',
    );

    expect(updateMock).toHaveBeenCalledWith(
      ticket.id,
      {
        title: ticket.title,
        description: ticket.description,
        priority: 'high',
        assignedToUserId: ticket.assignedToUserId,
      },
    );

    expect(
      loadDetailsSpy,
    ).toHaveBeenCalledOnce();
  });

  it('altera responsável preservando os demais dados editáveis', async () => {
    const ticket = createTicket({
      assignedToUserId: 'assignee-1',
    });

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    updateMock.mockResolvedValue(
      createTicket({
        assignedToUserId: 'assignee-2',
        assignedToUserName: 'Dejair Lazzarotto',
      }),
    );

    const loadDetailsSpy = vi
      .spyOn(component, 'loadDetails')
      .mockResolvedValue();

    await component.changeAssignee(
      'assignee-2',
    );

    expect(updateMock).toHaveBeenCalledWith(
      ticket.id,
      {
        title: ticket.title,
        description: ticket.description,
        priority: ticket.priority,
        assignedToUserId: 'assignee-2',
      },
    );

    expect(
      loadDetailsSpy,
    ).toHaveBeenCalledOnce();
  });

  it('permite remover o responsável do chamado', async () => {
    const ticket = createTicket({
      assignedToUserId: 'assignee-1',
    });

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    updateMock.mockResolvedValue(
      createTicket({
        assignedToUserId: null,
        assignedToUserName: null,
      }),
    );

    const loadDetailsSpy = vi
      .spyOn(component, 'loadDetails')
      .mockResolvedValue();

    await component.changeAssignee('');

    expect(updateMock).toHaveBeenCalledWith(
      ticket.id,
      {
        title: ticket.title,
        description: ticket.description,
        priority: ticket.priority,
        assignedToUserId: null,
      },
    );

    expect(
      loadDetailsSpy,
    ).toHaveBeenCalledOnce();
  });

  it('inicia edição carregando título e descrição atuais', () => {
    const ticket = createTicket({
      title: 'Título atual',
      description: 'Descrição atual',
    });

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    component.startEditingDetails();

    expect(
      component.editingDetails(),
    ).toBe(true);

    expect(
      component.editingTitle(),
    ).toBe('Título atual');

    expect(
      component.editingDescription(),
    ).toBe('Descrição atual');
  });

  it('não inicia edição sem permissão de gerenciamento', () => {
    component.ticket.set(
      createTicket(),
    );

    fixture.componentRef.setInput(
      'canManage',
      false,
    );

    component.startEditingDetails();

    expect(
      component.editingDetails(),
    ).toBe(false);
  });

  it('cancela edição restaurando título e descrição atuais', () => {
    const ticket = createTicket({
      title: 'Título original',
      description: 'Descrição original',
    });

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    component.startEditingDetails();

    component.onEditingTitleChange(
      'Título alterado',
    );

    component.onEditingDescriptionChange(
      'Descrição alterada',
    );

    component.cancelEditingDetails();

    expect(
      component.editingDetails(),
    ).toBe(false);

    expect(
      component.editingTitle(),
    ).toBe('Título original');

    expect(
      component.editingDescription(),
    ).toBe('Descrição original');
  });

  it('salva título e descrição preservando prioridade e responsável', async () => {
    const ticket = createTicket({
      title: 'Título original',
      description: 'Descrição original',
      priority: 'high',
      assignedToUserId: 'assignee-1',
    });

    component.ticket.set(ticket);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    component.startEditingDetails();

    component.onEditingTitleChange(
      '  Novo título  ',
    );

    component.onEditingDescriptionChange(
      'Nova descrição',
    );

    updateMock.mockResolvedValue(
      createTicket({
        title: 'Novo título',
        description: 'Nova descrição',
      }),
    );

    const loadDetailsSpy = vi
      .spyOn(component, 'loadDetails')
      .mockResolvedValue();

    await component.saveDetails();

    expect(updateMock).toHaveBeenCalledWith(
      ticket.id,
      {
        title: 'Novo título',
        description: 'Nova descrição',
        priority: 'high',
        assignedToUserId: 'assignee-1',
      },
    );

    expect(
      component.editingDetails(),
    ).toBe(false);

    expect(
      loadDetailsSpy,
    ).toHaveBeenCalledOnce();
  });

  it('usa nomes de apresentação na timeline de troca de responsável', () => {
    const event = createTimelineEvent();

    expect(
      component.timelineDescription(event),
    ).toBe(
      'Responsável alterado de Rodrigo Suporte N1 para Dejair Lazzarotto.',
    );
  });

  it('usa valores técnicos como fallback na timeline de responsável', () => {
    const event = createTimelineEvent({
      previousDisplayValue: null,
      newDisplayValue: null,
      previousValue: 'user-previous',
      newValue: 'user-next',
    });

    expect(
      component.timelineDescription(event),
    ).toBe(
      'Responsável alterado de user-previous para user-next.',
    );
  });

});