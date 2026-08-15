import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';

import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  NonNullableFormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import {
  Router,
} from '@angular/router';

import {
  finalize,
} from 'rxjs';

import {
  AuthenticationService,
} from '../../application/authentication.service';

@Component({
  selector: 'deja-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {

  private readonly authentication =
    inject(AuthenticationService);

  private readonly router =
    inject(Router);

  private readonly formBuilder =
    inject(NonNullableFormBuilder);

  readonly submitting = signal(false);

  readonly errorMessage = signal('');

  readonly form = this.formBuilder.group({
    organizationId: [
      '',
      [
        Validators.minLength(36),
        Validators.maxLength(36),
      ],
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

  submit(): void {
    if (
      this.form.invalid
      || this.submitting()
    ) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting.set(true);
    this.errorMessage.set('');

    const credentials = this.form.getRawValue();
    const organizationId =
      credentials.organizationId.trim();

    this.authentication.login({
      organizationId: organizationId || null,
      email: credentials.email.trim().toLowerCase(),
      password: credentials.password,
    }).pipe(
      finalize(() => {
        this.submitting.set(false);
      }),
    ).subscribe({
      next: () => {
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
      return 'E-mail ou senha inválidos.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados.';
    }

    return 'Não foi possível entrar no sistema.';
  }

}