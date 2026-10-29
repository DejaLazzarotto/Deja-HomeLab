import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface PasswordResetIdentity {
  organizationCode: string;
  email: string;
}

export interface PasswordResetConfirmation extends PasswordResetIdentity {
  code: string;
  newPassword: string;
}

interface PasswordResetResponse {
  message: string;
}

@Injectable({
  providedIn: 'root',
})
export class PasswordResetService {
  private readonly http = inject(HttpClient);

  requestCode(
    identity: PasswordResetIdentity,
  ): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(
      '/api/fotos/auth/password-reset/request',
      {
        organization_code: identity.organizationCode.trim(),
        email: identity.email.trim().toLowerCase(),
      },
    );
  }

  confirm(
    data: PasswordResetConfirmation,
  ): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(
      '/api/fotos/auth/password-reset/confirm',
      {
        organization_code: data.organizationCode.trim(),
        email: data.email.trim().toLowerCase(),
        code: data.code,
        new_password: data.newPassword,
      },
    );
  }
}