import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FotosVerificationIdentity {
  organizationCode: string;
  email: string;
}

export interface FotosVerificationConfirmation extends FotosVerificationIdentity {
  code: string;
  newPassword: string;
}

export interface FotosVerificationResponse {
  message: string;
}

@Injectable({
  providedIn: 'root',
})
export class FotosVerificationService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/fotos/auth';

  requestActivation(identity: FotosVerificationIdentity): Observable<FotosVerificationResponse> {
    return this.requestCode('activation', identity);
  }

  requestPasswordReset(identity: FotosVerificationIdentity): Observable<FotosVerificationResponse> {
    return this.requestCode('password-reset', identity);
  }

  confirmActivation(data: FotosVerificationConfirmation): Observable<FotosVerificationResponse> {
    return this.confirmCode('activation', data);
  }

  confirmPasswordReset(data: FotosVerificationConfirmation): Observable<FotosVerificationResponse> {
    return this.confirmCode('password-reset', data);
  }

  private requestCode(
    purpose: 'activation' | 'password-reset',
    identity: FotosVerificationIdentity,
  ): Observable<FotosVerificationResponse> {
    return this.http.post<FotosVerificationResponse>(
      `${this.baseUrl}/${purpose}/request`,
      {
        organization_code: identity.organizationCode.trim(),
        email: identity.email.trim(),
      },
    );
  }

  private confirmCode(
    purpose: 'activation' | 'password-reset',
    data: FotosVerificationConfirmation,
  ): Observable<FotosVerificationResponse> {
    return this.http.post<FotosVerificationResponse>(
      `${this.baseUrl}/${purpose}/confirm`,
      {
        organization_code: data.organizationCode.trim(),
        email: data.email.trim(),
        code: data.code,
        new_password: data.newPassword,
      },
    );
  }
}
