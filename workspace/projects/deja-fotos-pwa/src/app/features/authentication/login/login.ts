import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';

import {
  FormBuilder,
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
} from '../../../core/authentication/authentication.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {
  private readonly formBuilder =
    inject(FormBuilder);

  private readonly authentication =
    inject(AuthenticationService);

  private readonly router =
    inject(Router);

  readonly loading =
    signal(false);

  readonly error =
    signal<string | null>(null);

  readonly form =
    this.formBuilder.nonNullable.group({
      organizationCode: [
        '',
        [
          Validators.required,
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
        ],
      ],
    });

  submit(): void {
    if (
      this.form.invalid
      || this.loading()
    ) {
      return;
    }

    this.error.set(null);
    this.loading.set(true);

    const {
      organizationCode,
      email,
      password,
    } = this.form.getRawValue();

    this.authentication
      .login(
        organizationCode,
        email,
        password,
      )
      .pipe(
        finalize(() => {
          this.loading.set(false);
        }),
      )
      .subscribe({
        next: () => {
          if (
            !this.authentication
              .canAccessFotos()
          ) {
            this.authentication.logout();

            this.error.set(
              'Este usuário não possui acesso ao Fotos.',
            );

            return;
          }

          void this.router.navigateByUrl(
            '/explore',
          );
        },
        error: () => {
          this.error.set(
            'Não foi possível entrar. Verifique os dados informados.',
          );
        },
      });
  }
}