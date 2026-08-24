/*
 * Deja Chamados
 *
 * Clients Presentation
 *
 * Formulário visual de cadastro e edição de clientes.
 */

import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  input,
  output,
  signal,
} from '@angular/core';

import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';

import { MatCheckboxModule } from '@angular/material/checkbox';

import { MatFormFieldModule } from '@angular/material/form-field';

import { MatInputModule } from '@angular/material/input';

import { MatSelectModule } from '@angular/material/select';

import { Client, ClientInput } from '../../domain';

import { ClientEnvironmentOption } from '../client-environment-option';

import { formatDocument, formatPhone } from './client-mask.utils';

import { businessEmailValidator, documentValidator, phoneValidator } from './client-validators';

@Component({
  selector: 'deja-client-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './client-form.html',
  styleUrl: './client-form.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClientFormComponent {
  private readonly formBuilder = inject(FormBuilder);

  readonly client = input<Client | null>(null);

  readonly environments = input<readonly ClientEnvironmentOption[]>([]);

  readonly defaultEnvironmentId = input<string | null>(null);

  readonly saving = input(false);

  readonly save = output<ClientInput>();

  readonly cancel = output<void>();

  readonly submitAttempted = signal(false);

  readonly title = computed(() => (this.client() ? 'Editar cliente' : 'Novo cliente'));

  readonly environmentOptions = computed<readonly ClientEnvironmentOption[]>(() => {
    const environments = this.environments();

    const requiredEnvironmentId = this.client()?.environmentId ?? this.defaultEnvironmentId();

    if (
      !requiredEnvironmentId ||
      environments.some((environment) => environment.id === requiredEnvironmentId)
    ) {
      return environments;
    }

    return [
      ...environments,
      {
        id: requiredEnvironmentId,
        name: 'Ambiente atual',
      },
    ];
  });

  readonly form = this.formBuilder.nonNullable.group({
    environmentId: ['', [Validators.required]],
    companyName: ['', [Validators.required, Validators.maxLength(255)]],
    fantasyName: ['', [Validators.required, Validators.maxLength(255)]],
    document: ['', [Validators.required, documentValidator]],
    contactName: ['', [Validators.required, Validators.maxLength(255)]],
    phone: ['', [Validators.required, phoneValidator]],
    whatsapp: ['', [Validators.required, phoneValidator]],
    email: ['', [Validators.required, Validators.maxLength(255), businessEmailValidator]],
    city: ['', [Validators.required, Validators.maxLength(100)]],
    state: ['RS', [Validators.required, Validators.minLength(2), Validators.maxLength(2)]],
    notes: ['', [Validators.maxLength(1000)]],
    active: [true],
  });

  private readonly synchronizeForm = effect(() => {
    const client = this.client();

    if (client) {
      this.form.reset({
        environmentId: client.environmentId,
        companyName: client.companyName,
        fantasyName: client.fantasyName,
        document: formatDocument(client.document),
        contactName: client.contactName,
        phone: formatPhone(client.phone),
        whatsapp: formatPhone(client.whatsapp),
        email: client.email,
        city: client.city,
        state: client.state,
        notes: client.notes,
        active: client.active,
      });

      this.prepareForm();
      return;
    }

    this.resetForm();
  });

  resetForm(): void {
    this.form.reset({
      environmentId: this.defaultEnvironmentId() ?? this.environments()[0]?.id ?? '',
      companyName: '',
      fantasyName: '',
      document: '',
      contactName: '',
      phone: '',
      whatsapp: '',
      email: '',
      city: '',
      state: 'RS',
      notes: '',
      active: true,
    });

    this.prepareForm();
  }

  onDocumentInput(): void {
    const control = this.form.controls.document;

    control.setValue(formatDocument(control.value), {
      emitEvent: false,
    });
  }

  onPhoneInput(): void {
    const control = this.form.controls.phone;

    control.setValue(formatPhone(control.value), {
      emitEvent: false,
    });
  }

  onWhatsappInput(): void {
    const control = this.form.controls.whatsapp;

    control.setValue(formatPhone(control.value), {
      emitEvent: false,
    });
  }

  onStateInput(): void {
    const control = this.form.controls.state;

    control.setValue(
      control.value
        .replace(/[^a-zA-Z]/g, '')
        .slice(0, 2)
        .toUpperCase(),
      {
        emitEvent: false,
      },
    );
  }

  onFieldBlur(controlName: keyof typeof this.form.controls): void {
    const control = this.form.controls[controlName];

    control.markAsTouched();
    control.updateValueAndValidity();
  }

  onSubmit(): void {
    if (this.saving()) {
      return;
    }

    this.submitAttempted.set(true);
    this.form.updateValueAndValidity();

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.save.emit(this.form.getRawValue());
  }

  onCancel(): void {
    if (!this.saving()) {
      this.cancel.emit();
    }
  }

  private prepareForm(): void {
    this.form.markAsPristine();
    this.form.markAsUntouched();
    this.submitAttempted.set(false);
    this.form.updateValueAndValidity();
  }
}
