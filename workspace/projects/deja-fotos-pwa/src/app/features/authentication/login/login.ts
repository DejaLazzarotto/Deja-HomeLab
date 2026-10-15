
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
  RouterLink,
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
    RouterLink,
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

  readonly showPassword = signal(false);

  togglePasswordVisibility(): void {
    this.showPassword.update((visible) => !visible);
  }

  readonly loading =
    signal(false);

  readonly error =
    signal<string | null>(null);

  private readonly rememberedOrganizationKey =
    'deja-fotos.remembered-organization';

  private readonly rememberedEmailKey =
    'deja-fotos.remembered-email';

  private readRememberedValue(key: string): string {
    try {
      return localStorage.getItem(key) ?? '';
    } catch {
      return '';
    }
  }
  readonly form =
    this.formBuilder.nonNullable.group({
      organizationCode: [
        this.readRememberedValue(this.rememberedOrganizationKey),
        [
          Validators.required,
        ],
      ],
      email: [
        this.readRememberedValue(this.rememberedEmailKey),
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

          try {
            localStorage.setItem(
              this.rememberedOrganizationKey,
              organizationCode.trim().toUpperCase(),
            );

            localStorage.setItem(
              this.rememberedEmailKey,
              email.trim().toLowerCase(),
            );
          } catch {
            // O login continua normalmente se o armazenamento falhar.
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