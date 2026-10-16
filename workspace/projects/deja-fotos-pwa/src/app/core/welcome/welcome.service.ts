import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class WelcomeService {
  private readonly storagePrefix =
    'vivaro.welcome.completed.v1';

  private storageKey(
    organization: string,
    email: string,
  ): string {
    const normalizedOrganization =
      organization.trim().toUpperCase();

    const normalizedEmail =
      email.trim().toLowerCase();

    return [
      this.storagePrefix,
      encodeURIComponent(normalizedOrganization),
      encodeURIComponent(normalizedEmail),
    ].join('.');
  }

  shouldShow(
    organization: string,
    email: string,
  ): boolean {
    if (!organization.trim() || !email.trim()) {
      return false;
    }

    try {
      return localStorage.getItem(
        this.storageKey(organization, email),
      ) !== 'true';
    } catch {
      return false;
    }
  }

  markCompleted(
    organization: string,
    email: string,
  ): void {
    if (!organization.trim() || !email.trim()) {
      return;
    }

    try {
      localStorage.setItem(
        this.storageKey(organization, email),
        'true',
      );
    } catch {
      // Falhas no armazenamento nao impedem o uso do aplicativo.
    }
  }
}
