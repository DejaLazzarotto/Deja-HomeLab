
import { HttpErrorResponse } from '@angular/common/http';
import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import {
  AbstractControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';

import { finalize } from 'rxjs';
import { Router } from '@angular/router';

import { AuthenticationService } from '../../application/authentication.service';
import { canAccessWorkspace } from '../../application/workspace-access-policy';
import { PasswordResetService } from '../../application/password-reset.service';

function normalizeOrganizationCode(value: string): string {
  return value
    .trim()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();
}

function organizationCodeValidator(
  control: AbstractControl,
): ValidationErrors | null {
  const value = normalizeOrganizationCode(
    String(control.value ?? ''),
  );

  if (!value) {
    return null;
  }

  if (
    value.length < 3 ||
    value.length > 32 ||
    !/^[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(value)
  ) {
    return { organizationCodeInvalid: true };
  }

  return null;
}

@Component({
  selector: 'deja-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {
  private readonly authentication = inject(AuthenticationService);

  private readonly router = inject(Router);

  private readonly formBuilder = inject(NonNullableFormBuilder);

  private readonly passwordReset = inject(PasswordResetService);

  readonly resetStep = signal<'login' | 'request' | 'confirm' | 'completed'>('login');

  readonly resetLoading = signal(false);

  readonly resetError = signal('');

  readonly resetInformation = signal('');

  readonly submitting = signal(false);

  readonly errorMessage = signal('');

  readonly form = this.formBuilder.group({
    organizationCode: [
      '',
      [organizationCodeValidator],
    ],
    email: [
      '',
      [
        Validators.required,
        Validators.email,
      ],
    ],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(8),
        Validators.maxLength(128),
      ],
    ],
  });

  readonly resetIdentityForm = this.formBuilder.group({
    organizationCode: ['', [organizationCodeValidator]],
    email: ['', [Validators.required, Validators.email]],
  });

  readonly resetConfirmationForm = this.formBuilder.group({
    code: ['', [Validators.required, Validators.pattern(/^[0-9]{6}$/)]],
    newPassword: ['', [
      Validators.required,
      Validators.minLength(8),
      Validators.maxLength(128),
    ]],
    confirmPassword: ['', Validators.required],
  });

  beginPasswordReset(): void {
    if (this.submitting()) return;

    this.resetIdentityForm.patchValue({
      organizationCode: this.form.controls.organizationCode.value,
      email: this.form.controls.email.value.trim().toLowerCase(),
    });

    this.resetError.set('');
    this.resetInformation.set('');
    this.resetStep.set('request');
  }

  requestPasswordReset(): void {
    if (this.resetIdentityForm.invalid || this.resetLoading()) {
      this.resetIdentityForm.markAllAsTouched();
      return;
    }

    const identity = this.resetIdentityForm.getRawValue();

    this.resetError.set('');
    this.resetLoading.set(true);

    this.passwordReset.requestCode({
      organizationCode: normalizeOrganizationCode(identity.organizationCode),
      email: identity.email.trim().toLowerCase(),
    }).pipe(
      finalize(() => this.resetLoading.set(false)),
    ).subscribe({
      next: () => {
        this.resetInformation.set(
          'Se a conta estiver cadastrada e habilitada, enviaremos um código para o e-mail informado.',
        );
        this.resetStep.set('confirm');
      },
      error: () => {
        this.resetError.set(
          'Não foi possível solicitar o código. Tente novamente.',
        );
      },
    });
  }

  confirmPasswordReset(): void {
    if (this.resetConfirmationForm.invalid || this.resetLoading()) {
      this.resetConfirmationForm.markAllAsTouched();
      return;
    }

    const { code, newPassword, confirmPassword } =
      this.resetConfirmationForm.getRawValue();

    if (newPassword !== confirmPassword) {
      this.resetError.set('As senhas informadas não coincidem.');
      return;
    }

    const identity = this.resetIdentityForm.getRawValue();

    this.resetError.set('');
    this.resetLoading.set(true);

    this.passwordReset.confirm({
      organizationCode: normalizeOrganizationCode(identity.organizationCode),
      email: identity.email.trim().toLowerCase(),
      code,
      newPassword,
    }).pipe(
      finalize(() => this.resetLoading.set(false)),
    ).subscribe({
      next: () => {
        this.resetConfirmationForm.reset();
        this.resetInformation.set('Senha redefinida com sucesso.');
        this.resetStep.set('completed');
      },
      error: () => {
        this.resetError.set(
          'Não foi possível redefinir a senha. Verifique o código ou solicite outro.',
        );
      },
    });
  }

  requestAnotherCode(): void {
    if (this.resetLoading()) return;

    this.resetConfirmationForm.reset();
    this.resetError.set('');
    this.resetInformation.set('');
    this.resetStep.set('request');
  }

  backToLogin(): void {
    if (this.resetLoading()) return;

    this.resetConfirmationForm.reset();
    this.resetError.set('');
    this.resetInformation.set('');
    this.resetStep.set('login');
  }
  submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting.set(true);
    this.errorMessage.set('');

    const credentials = this.form.getRawValue();

    const organizationCode = normalizeOrganizationCode(
      credentials.organizationCode,
    );

    this.authentication
      .login({
        organizationCode: organizationCode || null,
        email: credentials.email
          .trim()
          .toLowerCase(),
        password: credentials.password,
      })
      .pipe(
        finalize(() => {
          this.submitting.set(false);
        }),
      )
      .subscribe({
        next: user => {
          if (user.role === 'client') {
            void this.router.navigateByUrl('/portal');
            return;
          }

          if (!canAccessWorkspace(user)) {
            this.errorMessage.set(
              'Seu usuário não possui permissão para acessar o Workspace Administrativo. Utilize o aplicativo correspondente ao seu perfil.',
            );
            this.authentication.logout();
            return;
          }

          void this.router.navigateByUrl('/');
        },
        error: error => {
          this.errorMessage.set(
            this.resolveErrorMessage(error),
          );
        },
      });
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return 'Não foi possível entrar no sistema.';
    }

    if (error.status === 0) {
      return 'A API não está disponível.';
    }

    if (error.status === 401) {
      return (
        'Código da organização, e-mail ou senha inválidos.'
      );
    }

    if (error.status === 422) {
      return 'Revise os dados informados.';
    }

    return 'Não foi possível entrar no sistema.';
  }
}
