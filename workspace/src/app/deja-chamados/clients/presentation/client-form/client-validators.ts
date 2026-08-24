/*
 * Deja Chamados
 *
 * Clients Presentation
 *
 * Validadores utilizados exclusivamente pelo formulário visual.
 */

import { AbstractControl, ValidationErrors } from '@angular/forms';

import { onlyDigits } from './client-mask.utils';

export function documentValidator(control: AbstractControl): ValidationErrors | null {
  const value = onlyDigits(control.value);

  if (!value) {
    return null;
  }

  if (value.length === 11 && isValidCpf(value)) {
    return null;
  }

  if (value.length === 14 && isValidCnpj(value)) {
    return null;
  }

  return {
    invalidDocument: true,
  };
}

export function phoneValidator(control: AbstractControl): ValidationErrors | null {
  const value = onlyDigits(control.value);

  if (!value) {
    return null;
  }

  if (value.length === 10 || value.length === 11) {
    return null;
  }

  return {
    invalidPhone: true,
  };
}

export function businessEmailValidator(control: AbstractControl): ValidationErrors | null {
  const value = String(control.value ?? '').trim();

  if (!value) {
    return null;
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  if (emailPattern.test(value)) {
    return null;
  }

  return {
    invalidEmail: true,
  };
}

function isValidCpf(value: string): boolean {
  if (/^(\d)\1+$/.test(value)) {
    return false;
  }

  let sum = 0;

  for (let index = 0; index < 9; index += 1) {
    sum += Number(value[index]) * (10 - index);
  }

  let digit = 11 - (sum % 11);

  const firstDigit = digit >= 10 ? 0 : digit;

  if (firstDigit !== Number(value[9])) {
    return false;
  }

  sum = 0;

  for (let index = 0; index < 10; index += 1) {
    sum += Number(value[index]) * (11 - index);
  }

  digit = 11 - (sum % 11);

  const secondDigit = digit >= 10 ? 0 : digit;

  return secondDigit === Number(value[10]);
}

function isValidCnpj(value: string): boolean {
  if (/^(\d)\1+$/.test(value)) {
    return false;
  }

  const firstWeights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];

  const secondWeights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];

  const firstDigit = calculateCnpjDigit(value.slice(0, 12), firstWeights);

  const secondDigit = calculateCnpjDigit(value.slice(0, 12) + firstDigit, secondWeights);

  return firstDigit === Number(value[12]) && secondDigit === Number(value[13]);
}

function calculateCnpjDigit(value: string, weights: readonly number[]): number {
  const sum = value.split('').reduce((total, digit, index) => {
    return total + Number(digit) * weights[index];
  }, 0);

  const rest = sum % 11;

  return rest < 2 ? 0 : 11 - rest;
}
