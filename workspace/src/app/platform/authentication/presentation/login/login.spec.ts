import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { AuthenticationService } from '../../application/authentication.service';
import type { AuthenticatedUser } from '../../domain/authenticated-user';
import { LoginComponent } from './login';

function createUser(
  overrides: Partial<AuthenticatedUser> = {},
): AuthenticatedUser {
  return {
    id: 'user-1',
    organizationId: 'org-1',
    tenantId: 'tenant-1',
    environmentId: 'env-1',
    name: 'Usuário Teste',
    email: 'usuario@example.com',
    role: 'user',
    enabledModules: [],
    moduleAccess: [],
    ...overrides,
  };
}

describe('LoginComponent', () => {
  let component: LoginComponent;
  let login: ReturnType<typeof vi.fn>;
  let logout: ReturnType<typeof vi.fn>;
  let navigateByUrl: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    login = vi.fn();
    logout = vi.fn();
    navigateByUrl = vi.fn().mockResolvedValue(true);

    TestBed.configureTestingModule({
      providers: [
        {
          provide: AuthenticationService,
          useValue: { login, logout },
        },
        {
          provide: Router,
          useValue: { navigateByUrl },
        },
      ],
    });

    component = TestBed.runInInjectionContext(
      () => new LoginComponent(),
    );
  });

  afterEach(() => {
    TestBed.resetTestingModule();
  });

  function submitAs(user: AuthenticatedUser): void {
    login.mockReturnValue(of(user));

    component.form.setValue({
      organizationCode: 'FAMILIA-LAZZAROTTO',
      email: 'usuario@example.com',
      password: 'SenhaSegura123!',
    });

    component.submit();
  }

  it.each([
    'familia-lazzarotto',
    'Família-Lazzarotto',
    ' FAMÍLIA-LAZZAROTTO ',
  ])('normalizes organization code %s', organizationCode => {
    login.mockReturnValue(of(createUser({
      role: 'platform_admin',
    })));

    component.form.setValue({
      organizationCode,
      email: 'usuario@example.com',
      password: 'SenhaSegura123!',
    });

    expect(component.form.controls.organizationCode.valid).toBe(true);

    component.submit();

    expect(login).toHaveBeenCalledWith(
      expect.objectContaining({
        organizationCode: 'FAMILIA-LAZZAROTTO',
      }),
    );
  });

  it.each([
    'FAMILIA@LAZZAROTTO',
    'FAMILIA LAZZAROTTO',
    'FAMILIA--LAZZAROTTO',
    'FAMILIA_LAZZAROTTO',
    '-FAMILIA',
    'FAMILIA-',
    'AB',
    'A'.repeat(33),
  ])('rejects invalid organization code %s', organizationCode => {
    component.form.patchValue({ organizationCode });

    expect(component.form.controls.organizationCode.invalid).toBe(true);

    component.submit();

    expect(login).not.toHaveBeenCalled();
  });

  it('allows an empty organization code for platform admin', () => {
    login.mockReturnValue(of(createUser({
      role: 'platform_admin',
    })));

    component.form.setValue({
      organizationCode: '',
      email: 'usuario@example.com',
      password: 'SenhaSegura123!',
    });

    component.submit();

    expect(login).toHaveBeenCalledWith(
      expect.objectContaining({
        organizationCode: null,
      }),
    );
  });
  it('blocks Vivaro viewer from Workspace', () => {
    submitAs(createUser({
      enabledModules: ['fotos'],
      moduleAccess: [
        { moduleKey: 'fotos', role: 'viewer' },
      ],
    }));

    expect(navigateByUrl).not.toHaveBeenCalled();
    expect(logout).toHaveBeenCalledOnce();
    expect(component.errorMessage()).toContain(
      'não possui permissão',
    );
  });

  it('allows Vivaro manager into Workspace', () => {
    submitAs(createUser({
      enabledModules: ['fotos'],
      moduleAccess: [
        { moduleKey: 'fotos', role: 'manager' },
      ],
    }));

    expect(navigateByUrl).toHaveBeenCalledWith('/');
    expect(logout).not.toHaveBeenCalled();
  });

  it('allows platform administrator', () => {
    submitAs(createUser({
      role: 'platform_admin',
    }));

    expect(navigateByUrl).toHaveBeenCalledWith('/');
    expect(logout).not.toHaveBeenCalled();
  });

  it('requests a password reset code', () => {
    const requestCode = vi.fn().mockReturnValue(of({ message: 'OK' }));

    (component as unknown as {
      passwordReset: { requestCode: typeof requestCode };
    }).passwordReset = { requestCode };

    component.form.patchValue({
      organizationCode: 'Família-Lazzarotto',
      email: ' USUARIO@EXEMPLO.COM ',
    });

    component.beginPasswordReset();
    component.requestPasswordReset();

    expect(requestCode).toHaveBeenCalledWith({
      organizationCode: 'FAMILIA-LAZZAROTTO',
      email: 'usuario@exemplo.com',
    });

    expect(component.resetStep()).toBe('confirm');
    expect(component.resetInformation()).toContain('código');
  });
  it('confirms password reset with verification code', () => {
    const confirm = vi.fn().mockReturnValue(of({ message: 'OK' }));

    (component as unknown as {
      passwordReset: { confirm: typeof confirm };
    }).passwordReset = { confirm };

    component.resetIdentityForm.setValue({
      organizationCode: 'Família-Lazzarotto',
      email: 'usuario@exemplo.com',
    });

    component.resetConfirmationForm.setValue({
      code: '123456',
      newPassword: 'NovaSenhaSegura123!',
      confirmPassword: 'NovaSenhaSegura123!',
    });

    component.resetStep.set('confirm');
    component.confirmPasswordReset();

    expect(confirm).toHaveBeenCalledWith({
      organizationCode: 'FAMILIA-LAZZAROTTO',
      email: 'usuario@exemplo.com',
      code: '123456',
      newPassword: 'NovaSenhaSegura123!',
    });

    expect(component.resetStep()).toBe('completed');
    expect(component.resetInformation()).toContain('sucesso');
  });
  it('rejects mismatched passwords during reset', () => {
    const confirm = vi.fn();

    (component as unknown as {
      passwordReset: { confirm: typeof confirm };
    }).passwordReset = { confirm };

    component.resetIdentityForm.setValue({
      organizationCode: 'FAMILIA-LAZZAROTTO',
      email: 'usuario@exemplo.com',
    });

    component.resetConfirmationForm.setValue({
      code: '123456',
      newPassword: 'NovaSenhaSegura123!',
      confirmPassword: 'SenhaDiferente123!',
    });

    component.resetStep.set('confirm');
    component.confirmPasswordReset();

    expect(confirm).not.toHaveBeenCalled();
    expect(component.resetStep()).toBe('confirm');
    expect(component.resetError()).toContain('não coincidem');
  });
  it('handles an invalid password reset code', () => {
    const confirm = vi.fn().mockReturnValue(
      throwError(() => new Error('Código inválido')),
    );

    (component as unknown as {
      passwordReset: { confirm: typeof confirm };
    }).passwordReset = { confirm };

    component.resetIdentityForm.setValue({
      organizationCode: 'FAMILIA-LAZZAROTTO',
      email: 'usuario@exemplo.com',
    });

    component.resetConfirmationForm.setValue({
      code: '999999',
      newPassword: 'NovaSenhaSegura123!',
      confirmPassword: 'NovaSenhaSegura123!',
    });

    component.resetStep.set('confirm');
    component.confirmPasswordReset();

    expect(confirm).toHaveBeenCalledOnce();
    expect(component.resetStep()).toBe('confirm');
    expect(component.resetError()).toContain('Verifique o código');
    expect(component.resetLoading()).toBe(false);
  });
  it('handles password reset request failure', () => {
    const requestCode = vi.fn().mockReturnValue(
      throwError(() => new Error('API indisponível')),
    );

    (component as unknown as {
      passwordReset: { requestCode: typeof requestCode };
    }).passwordReset = { requestCode };

    component.resetIdentityForm.setValue({
      organizationCode: 'FAMILIA-LAZZAROTTO',
      email: 'usuario@exemplo.com',
    });

    component.resetStep.set('request');
    component.requestPasswordReset();

    expect(requestCode).toHaveBeenCalledOnce();
    expect(component.resetStep()).toBe('request');
    expect(component.resetError()).toContain(
      'Não foi possível solicitar o código',
    );
    expect(component.resetLoading()).toBe(false);
  });
  it('redirects client to Chamados portal', () => {
    submitAs(createUser({
      role: 'client',
    }));

    expect(navigateByUrl).toHaveBeenCalledWith('/portal');
    expect(logout).not.toHaveBeenCalled();
  });
});
