import { FormControl } from '@angular/forms';

import { formatDocument, formatPhone, onlyDigits } from './client-mask.utils';

import { businessEmailValidator, documentValidator, phoneValidator } from './client-validators';

describe('client form utilities', () => {
  it('should keep only digits', () => {
    expect(onlyDigits('12.345.678/0001-81')).toBe('12345678000181');
  });

  it('should format CPF', () => {
    expect(formatDocument('52998224725')).toBe('529.982.247-25');
  });

  it('should format CNPJ', () => {
    expect(formatDocument('11222333000181')).toBe('11.222.333/0001-81');
  });

  it('should format landline and mobile phones', () => {
    expect(formatPhone('5432224455')).toBe('(54) 3222-4455');

    expect(formatPhone('54999887766')).toBe('(54) 99988-7766');
  });

  it('should validate CPF and CNPJ check digits', () => {
    expect(documentValidator(new FormControl('529.982.247-25'))).toBeNull();

    expect(documentValidator(new FormControl('11.222.333/0001-81'))).toBeNull();

    expect(documentValidator(new FormControl('111.111.111-11'))).toEqual({
      invalidDocument: true,
    });
  });

  it('should validate phone length', () => {
    expect(phoneValidator(new FormControl('(54) 3222-4455'))).toBeNull();

    expect(phoneValidator(new FormControl('(54) 99988-7766'))).toBeNull();

    expect(phoneValidator(new FormControl('1234'))).toEqual({
      invalidPhone: true,
    });
  });

  it('should validate business email', () => {
    expect(businessEmailValidator(new FormControl('contato@example.com'))).toBeNull();

    expect(businessEmailValidator(new FormControl('contato-invalido'))).toEqual({
      invalidEmail: true,
    });
  });

  it('should allow empty values for optional validator composition', () => {
    const emptyControl = new FormControl('');

    expect(documentValidator(emptyControl)).toBeNull();

    expect(phoneValidator(emptyControl)).toBeNull();

    expect(businessEmailValidator(emptyControl)).toBeNull();
  });
});
