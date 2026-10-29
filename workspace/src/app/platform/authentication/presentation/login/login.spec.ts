import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

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

  it('redirects client to Chamados portal', () => {
    submitAs(createUser({
      role: 'client',
    }));

    expect(navigateByUrl).toHaveBeenCalledWith('/portal');
    expect(logout).not.toHaveBeenCalled();
  });
});
