import { describe, expect, it, vi } from 'vitest';

import { UserListComponent } from './user-list';

describe('UserListComponent - administração de senhas', () => {
  function setup() {
    const component = new UserListComponent();
    component.currentUserId = "administrador-global-1";
    component.currentUserRole = "platform_admin";
    const setPassword = vi.fn().mockResolvedValue(undefined);

    component.service = {
      setPassword,
    } as unknown as UserListComponent['service'];

    const user = {
      id: 'usuario-1',
      name: 'Usuário de Teste',
      email: 'usuario@exemplo.com',
      role: 'user',
    };

    return { component, setPassword, user };
  }

  it('impede redefinir senha de administrador global', () => {
    const { component, setPassword, user } = setup();

    component.openPasswordForm({
      ...user,
      role: 'platform_admin',
    } as Parameters<typeof component.openPasswordForm>[0]);

    expect(component.passwordFormVisible()).toBe(false);
    expect(setPassword).not.toHaveBeenCalled();
  });

  it('rejeita senha com menos de oito caracteres', async () => {
    const { component, setPassword, user } = setup();

    component.openPasswordForm(
      user as Parameters<typeof component.openPasswordForm>[0],
    );

    component.newPassword = '1234567';
    component.confirmPassword = '1234567';

    await component.savePassword();

    expect(setPassword).not.toHaveBeenCalled();
    expect(component.operationError()).toContain('8 e 128');
  });

  it('rejeita confirmação divergente', async () => {
    const { component, setPassword, user } = setup();

    component.openPasswordForm(
      user as Parameters<typeof component.openPasswordForm>[0],
    );

    component.newPassword = 'SenhaSegura123';
    component.confirmPassword = 'OutraSenha123';

    await component.savePassword();

    expect(setPassword).not.toHaveBeenCalled();
    expect(component.operationError()).toContain('não coincidem');
  });

  it('envia senha válida e limpa os campos após sucesso', async () => {
    const { component, setPassword, user } = setup();

    component.openPasswordForm(
      user as Parameters<typeof component.openPasswordForm>[0],
    );

    component.newPassword = 'SenhaSegura123';
    component.confirmPassword = 'SenhaSegura123';

    await component.savePassword();

    expect(setPassword).toHaveBeenCalledWith(
      'usuario-1',
      'SenhaSegura123',
    );
    expect(component.passwordFormVisible()).toBe(false);
    expect(component.passwordUser()).toBeNull();
    expect(component.newPassword).toBe('');
    expect(component.confirmPassword).toBe('');
  });

  it('limpa os campos ao cancelar', () => {
    const { component, user } = setup();

    component.openPasswordForm(
      user as Parameters<typeof component.openPasswordForm>[0],
    );

    component.newPassword = 'SenhaSegura123';
    component.confirmPassword = 'SenhaSegura123';

    component.cancelPasswordForm();

    expect(component.passwordFormVisible()).toBe(false);
    expect(component.newPassword).toBe('');
    expect(component.confirmPassword).toBe('');
  });

  it('trata falha do serviço sem manter senhas nos campos', async () => {
    const { component, setPassword, user } = setup();

    setPassword.mockRejectedValue(new Error('Falha simulada'));

    component.openPasswordForm(
      user as Parameters<typeof component.openPasswordForm>[0],
    );

    component.newPassword = 'SenhaSegura123';
    component.confirmPassword = 'SenhaSegura123';

    await component.savePassword();

    expect(component.operationError()).toBe('Falha simulada');
    expect(component.newPassword).toBe('');
    expect(component.confirmPassword).toBe('');
    expect(component.passwordFormVisible()).toBe(true);
  });

  it('impede redefinir a propria senha', () => {
    const { component, user } = setup();

    component.currentUserId = user.id;

    expect(component.canSetPassword(user as Parameters<typeof component.canSetPassword>[0])).toBe(false);
  });

  it('respeita a hierarquia de administradores de organizacao', () => {
    const { component, user } = setup();

    component.currentUserRole = 'organization_admin';
    component.defaultOrganizationId = 'organizacao-1';

    const target = {
      ...user,
      organizationId: 'organizacao-1',
    };

    expect(component.canSetPassword({
      ...target,
      role: 'organization_admin',
    } as Parameters<typeof component.canSetPassword>[0])).toBe(false);

    expect(component.canSetPassword({
      ...target,
      role: 'tenant_admin',
    } as Parameters<typeof component.canSetPassword>[0])).toBe(true);
  });

  it('restringe administradores de tenant ao proprio tenant', () => {
    const { component, user } = setup();

    component.currentUserRole = 'tenant_admin';
    component.defaultOrganizationId = 'organizacao-1';
    component.defaultTenantId = 'tenant-1';

    const target = {
      ...user,
      organizationId: 'organizacao-1',
      tenantId: 'tenant-1',
    };

    expect(component.canSetPassword({
      ...target,
      role: 'viewer',
    } as Parameters<typeof component.canSetPassword>[0])).toBe(true);

    expect(component.canSetPassword({
      ...target,
      role: 'tenant_admin',
    } as Parameters<typeof component.canSetPassword>[0])).toBe(false);

    expect(component.canSetPassword({
      ...target,
      tenantId: 'tenant-2',
    } as Parameters<typeof component.canSetPassword>[0])).toBe(false);
  });

  it('impede redefinicao fora da organizacao', () => {
    const { component, user } = setup();

    component.currentUserRole = 'organization_admin';
    component.defaultOrganizationId = 'organizacao-1';

    expect(component.canSetPassword({
      ...user,
      organizationId: 'organizacao-2',
    } as Parameters<typeof component.canSetPassword>[0])).toBe(false);
  });

});
