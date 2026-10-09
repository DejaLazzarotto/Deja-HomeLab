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
  selector: 'app-activation',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './activation.html',
  styleUrl: './activation.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivationComponent {
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
    newPassword: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(128)]],
    confirmPassword: ['', Validators.required],
  });

  requestCode(): void {
    if (this.identityForm.invalid || this.loading()) {
      return;
    }

    this.error.set(null);
    this.information.set(null);
    this.loading.set(true);

    this.verification.requestActivation(
      this.identityForm.getRawValue(),
    ).pipe(
      finalize(() => this.loading.set(false)),
    ).subscribe({
      next: () => {
        this.information.set(
          'Se sua conta estiver habilitada, enviaremos um código para o e-mail informado.',
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

  confirmActivation(): void {
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

    this.verification.confirmActivation({
      ...this.identityForm.getRawValue(),
      code,
      newPassword,
    }).pipe(
      finalize(() => this.loading.set(false)),
    ).subscribe({
      next: () => {
        this.confirmationForm.reset();
        this.information.set('Sua senha foi definida com sucesso.');
        this.step.set('completed');
      },
      error: () => {
        this.error.set(
          'Código inválido ou expirado. Solicite um novo código.',
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
