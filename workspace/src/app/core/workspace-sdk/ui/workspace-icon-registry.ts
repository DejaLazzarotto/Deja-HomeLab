/*
 * Deja Workspace UI SDK
 *
 * Workspace Icon Registry
 *
 * Registro institucional responsável pelo catálogo
 * oficial de ícones utilizados pelo Workspace.
 */

import {
  WorkspaceIcon,
} from './workspace-icon';

export class WorkspaceIconRegistry {

  private readonly icons =
    new Map<string, WorkspaceIcon>();

  /**
   * Registra um ícone institucional.
   */
  register(
    icon: WorkspaceIcon,
  ): void {

    this.icons.set(
      icon.id,
      icon,
    );

  }

  /**
   * Registra múltiplos ícones institucionais.
   */
  registerMany(
    icons: readonly WorkspaceIcon[],
  ): void {

    icons.forEach(
      (icon) => this.register(icon),
    );

  }

  /**
   * Resolve um ícone pelo identificador.
   */
  resolve(
    id: string,
  ): WorkspaceIcon | undefined {

    return this.icons.get(id);

  }

  /**
   * Verifica se um ícone está registrado.
   */
  has(
    id: string,
  ): boolean {

    return this.icons.has(id);

  }

  /**
   * Remove um ícone do registro.
   */
  unregister(
    id: string,
  ): boolean {

    return this.icons.delete(id);

  }

  /**
   * Retorna todos os ícones registrados.
   */
  getAll(): readonly WorkspaceIcon[] {

    return [
      ...this.icons.values(),
    ];

  }

  /**
   * Remove todos os ícones registrados.
   */
  clear(): void {

    this.icons.clear();

  }

}