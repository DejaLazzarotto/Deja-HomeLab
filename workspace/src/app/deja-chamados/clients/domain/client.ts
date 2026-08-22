/*
 * Deja Chamados
 *
 * Clients Domain
 *
 * Representa um cliente atendido dentro do escopo da plataforma.
 */

export interface Client {
  id: string;

  organizationId: string;
  tenantId: string;
  environmentId: string;

  companyName: string;
  fantasyName: string;
  document: string;

  contactName: string;

  phone: string;
  whatsapp: string;
  email: string;

  city: string;
  state: string;

  notes: string;

  active: boolean;

  createdAt: string;
  updatedAt: string;

  totalTickets: number;
}

export interface ClientInput {
  environmentId: string;

  companyName: string;
  fantasyName: string;
  document: string;

  contactName: string;

  phone: string;
  whatsapp: string;
  email: string;

  city: string;
  state: string;

  notes: string;

  active: boolean;
}