import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';

import { HttpErrorResponse } from '@angular/common/http';

import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { finalize } from 'rxjs';

import { AuthenticationService } from '../../application/authentication.service';

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

  private readonly formBuilder = inject(NonNullableFormBuilder);

  readonly submitting = signal(false);

  readonly errorMessage = signal('');

  readonly form = this.formBuilder.group({
    organizationCode: [
      '',
      [
        Validators.minLength(3),
        Validators.maxLength(32),
        Validators.pattern(/^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/),
      ],
    ],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(128)]],
  });

  submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting.set(true);
    this.errorMessage.set('');

    const credentials = this.form.getRawValue();
    const organizationCode = credentials.organizationCode.trim().toUpperCase();

    this.authentication
      .login({
        organizationCode: organizationCode || null,
        email: credentials.email.trim().toLowerCase(),
        password: credentials.password,
      })
      .pipe(
        finalize(() => {
          this.submitting.set(false);
        }),
      )
      .subscribe({
        next: () => {
          window.location.replace('/');
        },
        error: (error) => {
          this.errorMessage.set(this.resolveErrorMessage(error));
        },
      });
  }

  private resolveErrorMessage(error: unknown): string {
    if (!(error instanceof HttpErrorResponse)) {
      return 'Não foi possível entrar no sistema.';
    }

    if (error.status === 0) {
      return 'A API não está disponível.';
    }

    if (error.status === 401) {
      return 'Código da organização, e-mail ou senha inválidos.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados.';
    }

    return 'Não foi possível entrar no sistema.';
  }
}
