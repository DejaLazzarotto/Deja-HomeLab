import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Output,
} from '@angular/core';

import {
  NonNullableFormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import {
  inject,
} from '@angular/core';

import {
  PortalTicketCreate,
} from '../../domain/portal-ticket';

@Component({
  selector: 'deja-portal-ticket-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
  ],
  templateUrl: './portal-ticket-form.html',
  styleUrl: './portal-ticket-form.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PortalTicketFormComponent {

  private readonly formBuilder =
    inject(NonNullableFormBuilder);

  @Output()
  readonly submitted =
    new EventEmitter<PortalTicketCreate>();

  @Output()
  readonly cancelled =
    new EventEmitter<void>();

  readonly form =
    this.formBuilder.group({
      title: [
        '',
        [
          Validators.required,
          Validators.maxLength(150),
        ],
      ],
      description: [
        '',
        [
          Validators.required,
          Validators.maxLength(5000),
        ],
      ],
    });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value =
      this.form.getRawValue();

    this.submitted.emit({
      title: value.title.trim(),
      description: value.description.trim(),
    });
  }

  cancel(): void {
    this.cancelled.emit();
  }

}