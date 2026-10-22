/*
 * Deja Workspace Angular Integration
 *
 * Workspace Icon Provider
 *
 * Adaptador institucional responsável por traduzir
 * identificadores lógicos de ícones em recursos físicos
 * publicados pela camada de Branding.
 *
 * O Workspace SDK permanece completamente desacoplado
 * da localização física dos recursos visuais.
 */

import {
  inject,
  Injectable,
} from '@angular/core';
import { APP_BASE_HREF } from '@angular/common';

/**
 * Provider Angular responsável pela resolução dos
 * recursos institucionais de ícones.
 *
 * Exemplos:
 *
 * dashboard
 *   ->
 * /branding/icons/dashboard.svg
 *
 * settings
 *   ->
 * /branding/icons/settings.svg
 */
@Injectable({
  providedIn: 'root',
})
export class WorkspaceIconProvider {

  private readonly baseHref = inject(APP_BASE_HREF, { optional: true })
    ?? document.querySelector('base')?.getAttribute('href')
    ?? '/';

  private readonly brandingPath =
    `${this.baseHref.replace(/\/$/, '')}/branding/icons`;

  /**
   * Resolve o caminho físico correspondente a um
   * identificador institucional de ícone.
   */
  resolve(
    iconId: string | undefined,
  ): string | undefined {

    if (!iconId) {
      return undefined;
    }

    return `${this.brandingPath}/${iconId}.svg`;

  }

}