import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class WelcomeService {
  private readonly storageKey =
    'vivaro.welcome.completed.v1';

  shouldShow(): boolean {
    try {
      return localStorage.getItem(
        this.storageKey,
      ) !== 'true';
    } catch {
      return true;
    }
  }

  markCompleted(): void {
    try {
      localStorage.setItem(
        this.storageKey,
        'true',
      );
    } catch {
      // O armazenamento indisponivel nao bloqueia o aplicativo.
    }
  }
}
