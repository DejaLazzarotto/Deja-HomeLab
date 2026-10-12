
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

import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import {
  FotosVerificationService,
} from '../../../core/authentication/fotos-verification.service';

@Component({
  selector: 'app-password-reset',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './password-reset.html',
  styleUrl: './password-reset.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PasswordResetComponent {
  private readonly formBuilder = inject(FormBuilder);
  private readonly verification = inject(FotosVerificationService);

  readonly step = signal<'request' | 'confirm' | 'completed'>('request');
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly information = signal<string | null>(null);

  readonly identityForm = this.formBuilder.nonNullable.group({
    organizationCode: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
  });

  readonly confirmationForm = this.formBuilder.nonNullable.group({
    code: ['', [Validators.required, Validators.pattern(/^[0-9]{6}$/)]],
    newPassword: [
      '',
      [
        Validators.required,
        Validators.minLength(8),
        Validators.maxLength(128),
      ],
    ],
    confirmPassword: ['', Validators.required],
  });

  requestCode(): void {
    if (this.identityForm.invalid || this.loading()) {
      return;
    }

    this.error.set(null);
    this.information.set(null);
    this.loading.set(true);

    this.verification.requestPasswordReset(
      this.identityForm.getRawValue(),
    ).pipe(
      finalize(() => this.loading.set(false)),
    ).subscribe({
      next: () => {
        this.information.set(
          'Se a conta estiver cadastrada e habilitada, enviaremos um código para o e-mail informado.',
        );
        this.step.set('confirm');
      },
      error: () => {
        this.error.set(
          'Não foi possível processar a solicitação. Tente novamente.',
        );
      },
    });
  }

  confirmPasswordReset(): void {
    if (this.confirmationForm.invalid || this.loading()) {
      return;
    }

    const { code, newPassword, confirmPassword } =
      this.confirmationForm.getRawValue();

    if (newPassword !== confirmPassword) {
      this.error.set('As senhas informadas não coincidem.');
      return;
    }

    this.error.set(null);
    this.loading.set(true);

    this.verification.confirmPasswordReset({
      ...this.identityForm.getRawValue(),
      code,
      newPassword,
    }).pipe(
      finalize(() => this.loading.set(false)),
    ).subscribe({
      next: () => {
        this.confirmationForm.reset();
        this.information.set('Sua senha foi redefinida com sucesso.');
        this.step.set('completed');
      },
      error: () => {
        this.error.set(
          'Não foi possível redefinir a senha. Verifique o código ou solicite outro.',
        );
      },
    });
  }

  backToRequest(): void {
    if (this.loading()) {
      return;
    }

    this.error.set(null);
    this.information.set(null);
    this.confirmationForm.reset();
    this.step.set('request');
  }
}
