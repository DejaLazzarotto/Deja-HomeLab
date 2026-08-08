import { WorkspaceRuntimeState, WorkspaceWidgetId } from '../contracts/workspace-contracts';
import {
  WorkspaceModuleManifest,
  WorkspaceRuntimeContext,
  WorkspaceRuntimeSnapshot,
  WorkspaceWidget,
} from '../models/workspace-models';
import { WorkspaceRegistries } from '../registries/workspace-registries';
import {
  WorkspaceAction,
  WorkspaceActionExecution,
  WorkspaceActionId,
  WorkspaceActionResult,
} from './workspace-action';
import { WorkspaceActionDispatcher } from './workspace-action-dispatcher';
import { WorkspaceActionRegistry } from './workspace-action-registry';
import {
  WorkspaceCommand,
  WorkspaceCommandExecution,
  WorkspaceCommandId,
  WorkspaceCommandResult,
} from './workspace-command';
import { WorkspaceCommandDispatcher } from './workspace-command-dispatcher';
import { WorkspaceCommandRegistry } from './workspace-command-registry';
import { WorkspaceRuntimeEventDispatcher } from './workspace-runtime-event-dispatcher';
import { WorkspaceRuntimeEvents } from './workspace-runtime-events';
import {
  WorkspaceRuntimeExtensionDispatcher,
  WorkspaceRuntimeExtensionDispatchResult,
} from './workspace-runtime-extension-dispatcher';
import {
  WorkspaceRuntimeExtension,
  WorkspaceRuntimeExtensionId,
  WorkspaceRuntimeExtensionPointId,
} from './workspace-runtime-extension-point';
import { WorkspaceRuntimeExtensionRegistry } from './workspace-runtime-extension-registry';
import { WorkspaceLayoutEngine } from './workspace-layout-engine';
import { WorkspaceRuntimeHookDispatcher } from './workspace-runtime-hook-dispatcher';
import { WorkspaceRuntimeHooks } from './workspace-runtime-hooks';
import { WorkspaceMenu, WorkspaceMenuId, WorkspaceMenuLocation } from '../ui/workspace-menu';
import { WorkspaceMenuRegistry } from '../ui/workspace-menu-registry';
import { WorkspaceToolbarRegistry } from '../ui/workspace-toolbar-registry';
import { WorkspaceContextMenu, WorkspaceContextMenuId } from '../ui/workspace-context-menu';
import { WorkspaceContextMenuRegistry } from '../ui/workspace-context-menu-registry';
import {
  WorkspaceCommandPalette,
  WorkspaceCommandPaletteId,
} from '../ui/workspace-command-palette';
import { WorkspaceCommandPaletteRegistry } from '../ui/workspace-command-palette-registry';
import { WorkspaceIcon } from '../ui/workspace-icon';
import { WorkspaceIconRegistry } from '../ui/workspace-icon-registry';
import { WorkspaceRenderContext } from './workspace-render-context';
import { WorkspaceRenderer } from './workspace-renderer';
import { WorkspaceRendererDispatcher } from './workspace-renderer-dispatcher';
import { WorkspaceRendererRegistry } from './workspace-renderer-registry';
import { WorkspaceResolvedDashboard } from './workspace-resolved-dashboard';
import { WorkspaceLayoutManager } from './workspace-layout-manager';
import { WorkspaceEditingManager } from './workspace-editing-manager';
import { WorkspaceDashboardState } from './workspace-dashboard-state';
import { WorkspaceNavigation, WorkspaceNavigationId } from './workspace-navigation';
import {
  WorkspaceNavigationDispatcher,
  WorkspaceNavigationResult,
} from './workspace-navigation-dispatcher';
import { WorkspaceNavigationRegistry } from './workspace-navigation-registry';
import { WorkspaceDashboardResolver } from './workspace-dashboard-resolver';

/**
 * Erro lançado quando uma operação não é permitida
 * no estado atual do Workspace Runtime.
 */
export class WorkspaceRuntimeStateError extends Error {
  constructor(
    readonly currentState: WorkspaceRuntimeState,
    readonly operation: string,
  ) {
    super(`Workspace runtime operation "${operation}" is not allowed in state "${currentState}"`);

    this.name = 'WorkspaceRuntimeStateError';
  }
}

/**
 * Runtime oficial do Workspace SDK.
 *
 * Responsabilidades:
 * - manter o estado do runtime;
 * - controlar o ciclo de vida;
 * - executar hooks de lifecycle;
 * - emitir eventos de lifecycle;
 * - registrar manifestos de módulos;
 * - registrar e executar Runtime Extensions;
 * - registrar e executar Workspace Commands;
 * - registrar e executar Workspace Actions;
 * - fornecer snapshots imutáveis;
 * - preservar independência de Angular.
 */
export class WorkspaceRuntime {
  private state: WorkspaceRuntimeState = 'created';

  private context?: WorkspaceRuntimeContext;

  private initializedAt?: Date;

  private startedAt?: Date;

  private stoppedAt?: Date;

  /**
   * Registry oficial de Workspace Commands.
   */
  private readonly commandRegistry: WorkspaceCommandRegistry;

  /**
   * Dispatcher oficial de Workspace Commands.
   */
  private readonly commandDispatcher: WorkspaceCommandDispatcher;

  /**
   * Registry oficial de Workspace Actions.
   */
  private readonly actionRegistry: WorkspaceActionRegistry;

  /**
   * Dispatcher oficial de Workspace Actions.
   */
  private readonly actionDispatcher: WorkspaceActionDispatcher;

  /**
   * Registry oficial de Workspace Navigation.
   */
  private readonly navigationRegistry: WorkspaceNavigationRegistry;

  /**
   * Dispatcher oficial de Workspace Navigation.
   */
  private readonly navigationDispatcher: WorkspaceNavigationDispatcher;

  /**
   * Registry oficial de Workspace Menus.
   */
  private readonly menuRegistry: WorkspaceMenuRegistry;

  /**
   * Registry oficial de Workspace Toolbars.
   */
  private readonly toolbarRegistry = new WorkspaceToolbarRegistry();

  /**
   * Registry oficial de Workspace Context Menus.
   */
  private readonly contextMenuRegistry = new WorkspaceContextMenuRegistry();

  /**
   * Registry oficial de Workspace Command Palette.
   */
  private readonly commandPaletteRegistry = new WorkspaceCommandPaletteRegistry();

  /**
   * Registry oficial de Workspace Icons.
   */
  private readonly iconRegistry = new WorkspaceIconRegistry();

  /**
   * Registry oficial de Workspace Renderers.
   */
  private readonly rendererRegistry: WorkspaceRendererRegistry;

  /**
   * Dispatcher oficial de Workspace Renderers.
   */
  private readonly rendererDispatcher: WorkspaceRendererDispatcher;

  readonly extensionDispatcher: WorkspaceRuntimeExtensionDispatcher;

  /**
   * Layout Engine associado ao Workspace Runtime.
   */
  private readonly layoutEngine?: WorkspaceLayoutEngine;

  /**
   * Fachada institucional do subsistema de Layout.
   */
  private readonly layoutManager?: WorkspaceLayoutManager;

  /**
   * Fachada institucional da Workspace Editing API.
   */
  private readonly editingManager?: WorkspaceEditingManager;

  constructor(
    readonly registries: WorkspaceRegistries = new WorkspaceRegistries(),
    readonly events: WorkspaceRuntimeEventDispatcher = new WorkspaceRuntimeEventDispatcher(),
    readonly hooks: WorkspaceRuntimeHookDispatcher = new WorkspaceRuntimeHookDispatcher(),
    readonly extensions: WorkspaceRuntimeExtensionRegistry = new WorkspaceRuntimeExtensionRegistry(),
    layoutEngine?: WorkspaceLayoutEngine,
    layoutManager?: WorkspaceLayoutManager,
    editingManager?: WorkspaceEditingManager,
  ) {
    this.layoutEngine = layoutEngine;
    this.layoutManager = layoutManager;
    this.editingManager = editingManager;
    this.extensionDispatcher = new WorkspaceRuntimeExtensionDispatcher(this.extensions);

    this.commandRegistry = new WorkspaceCommandRegistry();
    this.commandDispatcher = new WorkspaceCommandDispatcher(this.commandRegistry);

    this.actionRegistry = new WorkspaceActionRegistry();
    this.actionDispatcher = new WorkspaceActionDispatcher(
      this.actionRegistry,
      this.commandDispatcher,
    );

    const dashboardResolver = new WorkspaceDashboardResolver(
      this.registries,
      this.layoutEngine!,
    );

    this.navigationRegistry = new WorkspaceNavigationRegistry();

    this.navigationDispatcher = new WorkspaceNavigationDispatcher(
      this.navigationRegistry,
      dashboardResolver,
      this.layoutManager,
    );

    this.menuRegistry = new WorkspaceMenuRegistry();

    this.rendererRegistry = new WorkspaceRendererRegistry();
    this.rendererDispatcher = new WorkspaceRendererDispatcher(
      this.rendererRegistry,
    );
  }

  getState(): WorkspaceRuntimeState {
    return this.state;
  }

  getContext(): WorkspaceRuntimeContext | undefined {
    return this.context;
  }

  /**
   * Retorna o Layout Engine associado ao Runtime.
   */
  getLayoutEngine(): WorkspaceLayoutEngine | undefined {
    return this.layoutEngine;
  }

  /**
   * Retorna a infraestrutura institucional de Layout.
   */
  get layout(): WorkspaceLayoutManager | undefined {
    return this.layoutManager;
  }

  /**
   * Retorna o estado institucional do Dashboard atualmente
   * controlado pelo subsistema de Layout.
   */
  get dashboardState(): WorkspaceDashboardState | undefined {
    return this.layoutManager?.dashboardState;
  }

  /**
   * Retorna a Workspace Editing API.
   */
  get editing(): WorkspaceEditingManager | undefined {
    return this.editingManager;
  }

  /**
   * Registra um Workspace Command.
   */
  registerCommand(command: WorkspaceCommand): void {
    this.commandRegistry.register(command);
  }

  /**
   * Registra múltiplos Workspace Commands.
   */
  registerCommands(commands: readonly WorkspaceCommand[]): void {
    this.commandRegistry.registerAll(commands);
  }

  /**
   * Remove um Workspace Command.
   */
  unregisterCommand(commandId: WorkspaceCommandId): WorkspaceCommand {
    return this.commandRegistry.unregister(commandId);
  }

  /**
   * Retorna todos os comandos registrados.
   */
  commands(): readonly WorkspaceCommand[] {
    return this.commandRegistry.list();
  }

  /**
   * Retorna um comando pelo identificador.
   */
  getCommand(commandId: WorkspaceCommandId): WorkspaceCommand {
    return this.commandRegistry.get(commandId);
  }

  /**
   * Verifica se um comando está registrado.
   */
  hasCommand(commandId: WorkspaceCommandId): boolean {
    return this.commandRegistry.has(commandId);
  }

  /**
   * Verifica se um comando pode ser executado.
   */
  canExecuteCommand<TPayload = unknown>(
    execution: WorkspaceCommandExecution<TPayload>,
  ): Promise<boolean> {
    return this.commandDispatcher.canExecute(execution);
  }

  /**
   * Executa um Workspace Command.
   */
  dispatchCommand<TPayload = unknown, TResult = unknown>(
    execution: WorkspaceCommandExecution<TPayload>,
  ): Promise<WorkspaceCommandResult<TResult>> {
    return this.commandDispatcher.dispatch<TPayload, TResult>(execution);
  }

  /**
   * Registra uma Workspace Action.
   */
  registerAction(action: WorkspaceAction): void {
    this.actionRegistry.register(action);
  }

  /**
   * Registra múltiplas Workspace Actions.
   */
  registerActions(actions: readonly WorkspaceAction[]): void {
    this.actionRegistry.registerAll(actions);
  }

  /**
   * Remove uma Workspace Action.
   */
  unregisterAction(actionId: WorkspaceActionId): WorkspaceAction {
    return this.actionRegistry.unregister(actionId);
  }

  /**
   * Retorna todas as Actions registradas.
   */
  actions(): readonly WorkspaceAction[] {
    return this.actionRegistry.list();
  }

  /**
   * Retorna uma Action pelo identificador.
   */
  getAction(actionId: WorkspaceActionId): WorkspaceAction {
    return this.actionRegistry.get(actionId);
  }

  /**
   * Verifica se uma Action está registrada.
   */
  hasAction(actionId: WorkspaceActionId): boolean {
    return this.actionRegistry.has(actionId);
  }

  /**
   * Verifica se uma Action pode ser executada.
   */
  canExecuteAction<TPayload = unknown>(
    execution: WorkspaceActionExecution<TPayload>,
  ): Promise<boolean> {
    return this.actionDispatcher.canExecute(execution);
  }

  /**
   * Executa uma Workspace Action.
   */
  dispatchAction<TPayload = unknown, TResult = unknown>(
    execution: WorkspaceActionExecution<TPayload>,
  ): Promise<WorkspaceActionResult<TResult>> {
    return this.actionDispatcher.dispatch<TPayload, TResult>(execution);
  }

  /**
   * Registra um item de Workspace Navigation.
   */
  registerNavigation(navigation: WorkspaceNavigation): void {
    this.navigationRegistry.register(navigation);
  }

  /**
   * Registra múltiplos itens de Workspace Navigation.
   */
  registerNavigations(navigations: readonly WorkspaceNavigation[]): void {
    this.navigationRegistry.registerAll(navigations);
  }

  /**
   * Remove um item de Workspace Navigation.
   */
  unregisterNavigation(navigationId: WorkspaceNavigationId): WorkspaceNavigation {
    return this.navigationRegistry.unregister(navigationId);
  }

  /**
   * Retorna todos os itens de navegação registrados.
   */
  navigations(): readonly WorkspaceNavigation[] {
    return this.navigationRegistry.list();
  }

  /**
   * Retorna os itens de navegação habilitados.
   */
  enabledNavigations(): readonly WorkspaceNavigation[] {
    return this.navigationRegistry.listEnabled();
  }

  /**
   * Retorna os itens habilitados e visíveis
   * na navegação principal do Workspace.
   */
  visibleNavigations(): readonly WorkspaceNavigation[] {
    return this.navigationRegistry.listVisible();
  }

  /**
   * Retorna um item de navegação pelo identificador.
   */
  getNavigation(navigationId: WorkspaceNavigationId): WorkspaceNavigation {
    return this.navigationRegistry.get(navigationId);
  }

  /**
   * Verifica se um item de navegação está registrado.
   */
  hasNavigation(navigationId: WorkspaceNavigationId): boolean {
    return this.navigationRegistry.has(navigationId);
  }

  /**
   * Retorna o item de navegação atualmente ativo.
   */
  currentNavigation(): WorkspaceNavigation | undefined {
    return this.navigationDispatcher.current();
  }

  /**
   * Verifica se um item de navegação está ativo.
   */
  isNavigationActive(navigationId: WorkspaceNavigationId): boolean {
    return this.navigationDispatcher.isActive(navigationId);
  }

  /**
   * Executa uma navegação institucional.
   */
  navigate(navigationId: WorkspaceNavigationId): Promise<WorkspaceNavigationResult> {
    return this.navigationDispatcher.dispatch(navigationId);
  }

  /**
   * Encerra a navegação institucional ativa.
   */
  clearNavigation(): Promise<void> {
    return this.navigationDispatcher.clear();
  }

  /**
   * Registra um Workspace Menu.
   */
  registerMenu(menu: WorkspaceMenu): void {
    this.menuRegistry.register(menu);
  }

  /**
   * Registra múltiplos Workspace Menus.
   */
  registerMenus(menus: readonly WorkspaceMenu[]): void {
    this.menuRegistry.registerMany(menus);
  }

  /**
   * Remove um Workspace Menu.
   */
  unregisterMenu(menuId: WorkspaceMenuId): boolean {
    return this.menuRegistry.unregister(menuId);
  }

  /**
   * Retorna todos os Workspace Menus.
   */
  menus(): readonly WorkspaceMenu[] {
    return this.menuRegistry.getAll();
  }

  /**
   * Retorna um Workspace Menu.
   */
  getMenu(menuId: WorkspaceMenuId): WorkspaceMenu {
    return this.menuRegistry.get(menuId);
  }

  /**
   * Verifica se um Workspace Menu está registrado.
   */
  hasMenu(menuId: WorkspaceMenuId): boolean {
    return this.menuRegistry.has(menuId);
  }

  /**
   * Retorna Workspace Menus por localização.
   */
  getMenusByLocation(location: WorkspaceMenuLocation): readonly WorkspaceMenu[] {
    return this.menuRegistry.getByLocation(location);
  }

  /**
   * Registra um Workspace Context Menu.
   */
  registerContextMenu(contextMenu: WorkspaceContextMenu): void {
    this.contextMenuRegistry.register(contextMenu);
  }

  /**
   * Registra múltiplos Workspace Context Menus.
   */
  registerContextMenus(contextMenus: readonly WorkspaceContextMenu[]): void {
    this.contextMenuRegistry.registerMany(contextMenus);
  }

  /**
   * Remove um Workspace Context Menu.
   */
  unregisterContextMenu(contextMenuId: WorkspaceContextMenuId): boolean {
    return this.contextMenuRegistry.unregister(contextMenuId);
  }

  /**
   * Retorna todos os Workspace Context Menus.
   */
  contextMenus(): readonly WorkspaceContextMenu[] {
    return this.contextMenuRegistry.getAll();
  }

  /**
   * Retorna um Workspace Context Menu pelo identificador.
   */
  getContextMenu(contextMenuId: WorkspaceContextMenuId): WorkspaceContextMenu {
    return this.contextMenuRegistry.get(contextMenuId);
  }

  /**
   * Verifica se um Workspace Context Menu está registrado.
   */
  hasContextMenu(contextMenuId: WorkspaceContextMenuId): boolean {
    return this.contextMenuRegistry.has(contextMenuId);
  }

  /**
   * Registra um Workspace Command Palette.
   */
  registerCommandPalette(commandPalette: WorkspaceCommandPalette): void {
    this.commandPaletteRegistry.register(commandPalette);
  }

  /**
   * Registra múltiplos Workspace Command Palette.
   */
  registerCommandPalettes(commandPalettes: readonly WorkspaceCommandPalette[]): void {
    this.commandPaletteRegistry.registerMany(commandPalettes);
  }

  /**
   * Remove um Workspace Command Palette.
   */
  unregisterCommandPalette(commandPaletteId: WorkspaceCommandPaletteId): boolean {
    return this.commandPaletteRegistry.unregister(commandPaletteId);
  }

  /**
   * Retorna todos os Workspace Command Palette.
   */
  commandPalettes(): readonly WorkspaceCommandPalette[] {
    return this.commandPaletteRegistry.getAll();
  }

  /**
   * Retorna um Workspace Command Palette pelo identificador.
   */
  getCommandPalette(commandPaletteId: WorkspaceCommandPaletteId): WorkspaceCommandPalette {
    return this.commandPaletteRegistry.get(commandPaletteId);
  }

  /**
   * Verifica se um Workspace Command Palette está registrado.
   */
  hasCommandPalette(commandPaletteId: WorkspaceCommandPaletteId): boolean {
    return this.commandPaletteRegistry.has(commandPaletteId);
  }

  /**
   * Pesquisa itens da Workspace Command Palette.
   */
  searchCommandPalette(text: string): readonly WorkspaceCommandPalette[] {
    return this.commandPaletteRegistry.search(text);
  }

  /**
   * Registra um Workspace Icon.
   */
  registerIcon(icon: WorkspaceIcon): void {
    this.iconRegistry.register(icon);
  }

  /**
   * Registra múltiplos Workspace Icons.
   */
  registerIcons(icons: readonly WorkspaceIcon[]): void {
    this.iconRegistry.registerMany(icons);
  }

  /**
   * Remove um Workspace Icon.
   */
  unregisterIcon(iconId: string): boolean {
    return this.iconRegistry.unregister(iconId);
  }

  /**
   * Retorna todos os Workspace Icons registrados.
   */
  icons(): readonly WorkspaceIcon[] {
    return this.iconRegistry.getAll();
  }

  /**
   * Retorna um Workspace Icon pelo identificador.
   */
  getIcon(iconId: string): WorkspaceIcon | undefined {
    return this.iconRegistry.resolve(iconId);
  }

  /**
   * Verifica se um Workspace Icon está registrado.
   */
  hasIcon(iconId: string): boolean {
    return this.iconRegistry.has(iconId);
  }

  /**
   * Retorna o Registry institucional de Workspace Icons.
   */
  getIconRegistry(): WorkspaceIconRegistry {
    return this.iconRegistry;
  }

  /**
   * Registra um Workspace Renderer.
   */
  registerRenderer(renderer: WorkspaceRenderer): void {
    this.rendererRegistry.register(renderer);
  }

  /**
   * Registra múltiplos Workspace Renderers.
   */
  registerRenderers(renderers: readonly WorkspaceRenderer[]): void {
    renderers.forEach((renderer) => this.rendererRegistry.register(renderer));
  }

  /**
   * Remove um Workspace Renderer.
   */
  unregisterRenderer(rendererId: string): boolean {
    return this.rendererRegistry.unregister(rendererId);
  }

  /**
   * Retorna todos os Workspace Renderers registrados.
   */
  renderers(): readonly WorkspaceRenderer[] {
    return this.rendererRegistry.list();
  }

  /**
   * Renderiza um Workspace Dashboard resolvido.
   */
  async renderDashboard(
    dashboard: WorkspaceResolvedDashboard,
    context: WorkspaceRenderContext,
  ): Promise<void> {
    await this.rendererDispatcher.render(dashboard, context);
  }

  /**
   * Libera os recursos do Renderer associado ao contexto.
   */
  async disposeRenderer(context: WorkspaceRenderContext): Promise<void> {
    await this.rendererDispatcher.dispose(context);
  }

  /**
   * Registra um Workspace Widget.
   */
  registerWidget(widget: WorkspaceWidget): void {
    this.registries.widgets.register(widget);
  }

  /**
   * Registra múltiplos Workspace Widgets.
   */
  registerWidgets(widgets: readonly WorkspaceWidget[]): void {
    this.registries.widgets.registerMany(widgets);
  }

  /**
   * Substitui um Workspace Widget registrado.
   */
  replaceWidget(widget: WorkspaceWidget): void {
    this.registries.widgets.replace(widget);
  }

  /**
   * Remove um Workspace Widget.
   */
  unregisterWidget(widgetId: WorkspaceWidgetId): boolean {
    return this.registries.widgets.unregister(widgetId);
  }

  /**
   * Retorna todos os Workspace Widgets registrados.
   */
  widgets(): readonly WorkspaceWidget[] {
    return this.registries.widgets.list();
  }

  /**
   * Retorna um Workspace Widget pelo identificador.
   */
  getWidget(widgetId: WorkspaceWidgetId): WorkspaceWidget | undefined {
    return this.registries.widgets.get(widgetId);
  }

  /**
   * Retorna obrigatoriamente um Workspace Widget.
   *
   * Lança WorkspaceRegistryResourceNotFoundError quando o Widget
   * solicitado não está registrado.
   */
  requireWidget(widgetId: WorkspaceWidgetId): WorkspaceWidget {
    return this.registries.widgets.require(widgetId);
  }

  /**
   * Verifica se um Workspace Widget está registrado.
   */
  hasWidget(widgetId: WorkspaceWidgetId): boolean {
    return this.registries.widgets.has(widgetId);
  }

  /**
   * Retorna os Workspace Widgets pertencentes a um determinado tipo.
   */
  getWidgetsByType(widgetType: string): readonly WorkspaceWidget[] {
    return this.registries.widgets.listByType(widgetType);
  }

  async initialize(context: WorkspaceRuntimeContext): Promise<void> {
    this.assertState('initialize', ['created', 'stopped']);

    const previousState = this.state;

    this.state = 'initializing';

    try {
      await this.hooks.execute(WorkspaceRuntimeHooks.BeforeInitialize, {
        runtimeContext: context,
        operation: 'initialize',
        data: {
          previousState,
          currentState: this.state,
        },
      });

      await this.events.emit(WorkspaceRuntimeEvents.BeforeInitialize, {
        previousState,
        currentState: this.state,
        context,
      });

      this.context = context;
      this.initializedAt = new Date();
      this.startedAt = undefined;
      this.stoppedAt = undefined;
      this.state = 'ready';

      await this.events.emit(WorkspaceRuntimeEvents.AfterInitialize, {
        previousState,
        currentState: this.state,
        context,
      });

      await this.hooks.execute(WorkspaceRuntimeHooks.AfterInitialize, {
        runtimeContext: context,
        operation: 'initialize',
        data: {
          previousState,
          currentState: this.state,
        },
      });
    } catch (error) {
      await this.fail('initialize', error);
      throw error;
    }
  }

  registerManifest(manifest: WorkspaceModuleManifest): void {
    this.assertState('registerManifest', ['created', 'initializing', 'ready']);

    if (manifest.domains?.length) {
      this.registries.domains.registerMany(manifest.domains);
    }

    if (manifest.views?.length) {
      this.registries.views.registerMany(manifest.views);
    }

    if (manifest.navigation?.length) {
      this.registries.navigation.registerMany(manifest.navigation);
    }

    if (manifest.widgets?.length) {
      this.registries.widgets.registerMany(manifest.widgets);
    }

    if (manifest.dashboards?.length) {
      this.registries.dashboards.registerMany(manifest.dashboards);
    }

    if (manifest.services?.length) {
      this.registries.services.registerMany(manifest.services);
    }
  }

  /**
   * Registra uma Runtime Extension.
   */
  registerExtension(extension: WorkspaceRuntimeExtension): void {
    this.assertState('registerExtension', ['created', 'initializing', 'ready']);

    this.extensions.register(extension);
  }

  /**
   * Registra múltiplas Runtime Extensions.
   */
  registerExtensions(extensions: readonly WorkspaceRuntimeExtension[]): void {
    this.assertState('registerExtensions', ['created', 'initializing', 'ready']);

    this.extensions.registerMany(extensions);
  }

  /**
   * Remove uma Runtime Extension.
   */
  unregisterExtension(extensionId: WorkspaceRuntimeExtensionId): boolean {
    this.assertState('unregisterExtension', ['created', 'initializing', 'ready', 'stopped']);

    return this.extensions.unregister(extensionId);
  }

  /**
   * Registry oficial de Workspace Toolbars.
   */
  getToolbarRegistry(): WorkspaceToolbarRegistry {
    return this.toolbarRegistry;
  }

  /**
   * Executa as Runtime Extensions habilitadas de um ponto de extensão.
   */
  async dispatchExtensionPoint<TPayload = unknown, TResult = unknown>(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
    payload: TPayload,
  ): Promise<readonly WorkspaceRuntimeExtensionDispatchResult<TResult>[]> {
    this.assertState('dispatchExtensionPoint', ['ready', 'running']);

    return this.extensionDispatcher.dispatch<TPayload, TResult>(
      extensionPoint,
      payload,
      this.context,
    );
  }

  /**
   * Executa um ponto de extensão e retorna apenas os valores
   * produzidos pelos handlers.
   */
  async dispatchExtensionResults<TPayload = unknown, TResult = unknown>(
    extensionPoint: WorkspaceRuntimeExtensionPointId,
    payload: TPayload,
  ): Promise<readonly TResult[]> {
    this.assertState('dispatchExtensionResults', ['ready', 'running']);

    return this.extensionDispatcher.dispatchResults<TPayload, TResult>(
      extensionPoint,
      payload,
      this.context,
    );
  }

  async start(): Promise<void> {
    this.assertState('start', ['ready']);

    const previousState = this.state;

    try {
      await this.hooks.execute(WorkspaceRuntimeHooks.BeforeStart, {
        runtimeContext: this.context,
        operation: 'start',
        data: {
          previousState,
          currentState: this.state,
        },
      });

      await this.events.emit(WorkspaceRuntimeEvents.BeforeStart, {
        previousState,
        currentState: this.state,
      });

      this.startedAt = new Date();
      this.stoppedAt = undefined;
      this.state = 'running';

      await this.events.emit(WorkspaceRuntimeEvents.AfterStart, {
        previousState,
        currentState: this.state,
      });

      await this.hooks.execute(WorkspaceRuntimeHooks.AfterStart, {
        runtimeContext: this.context,
        operation: 'start',
        data: {
          previousState,
          currentState: this.state,
        },
      });
    } catch (error) {
      await this.fail('start', error);
      throw error;
    }
  }

  async stop(): Promise<void> {
    this.assertState('stop', ['ready', 'running']);

    const previousState = this.state;

    this.state = 'stopping';

    try {
      await this.hooks.execute(WorkspaceRuntimeHooks.BeforeStop, {
        runtimeContext: this.context,
        operation: 'stop',
        data: {
          previousState,
          currentState: this.state,
        },
      });

      await this.events.emit(WorkspaceRuntimeEvents.BeforeStop, {
        previousState,
        currentState: this.state,
      });

      this.stoppedAt = new Date();
      this.state = 'stopped';

      await this.events.emit(WorkspaceRuntimeEvents.AfterStop, {
        previousState,
        currentState: this.state,
      });

      await this.hooks.execute(WorkspaceRuntimeHooks.AfterStop, {
        runtimeContext: this.context,
        operation: 'stop',
        data: {
          previousState,
          currentState: this.state,
        },
      });
    } catch (error) {
      await this.fail('stop', error);
      throw error;
    }
  }

  async reset(): Promise<void> {
    const previousState = this.state;

    try {
      await this.hooks.execute(WorkspaceRuntimeHooks.BeforeReset, {
        runtimeContext: this.context,
        operation: 'reset',
        data: {
          previousState,
          currentState: this.state,
        },
      });

      await this.events.emit(WorkspaceRuntimeEvents.BeforeReset, {
        previousState,
        currentState: this.state,
      });

      this.registries.clear();
      this.extensions.clear();
      this.commandRegistry.clear();
      this.actionRegistry.clear();
      this.menuRegistry.clear();
      this.toolbarRegistry.clear();
      this.contextMenuRegistry.clear();
      this.commandPaletteRegistry.clear();
      this.iconRegistry.clear();
      this.rendererRegistry.clear();
      this.context = undefined;
      this.initializedAt = undefined;
      this.startedAt = undefined;
      this.stoppedAt = undefined;
      this.state = 'created';

      await this.events.emit(WorkspaceRuntimeEvents.AfterReset, {
        previousState,
        currentState: this.state,
      });

      await this.hooks.execute(WorkspaceRuntimeHooks.AfterReset, {
        operation: 'reset',
        data: {
          previousState,
          currentState: this.state,
        },
      });
    } catch (error) {
      await this.fail('reset', error);
      throw error;
    }
  }

  async fail(operation: string, error?: unknown): Promise<void> {
    const previousState = this.state;

    this.state = 'failed';

    await this.events.emit(WorkspaceRuntimeEvents.Failed, {
      previousState,
      currentState: this.state,
      operation,
      error,
    });
  }

  snapshot(): WorkspaceRuntimeSnapshot {
    return {
      state: this.state,
      initializedAt: this.initializedAt,
      startedAt: this.startedAt,
      stoppedAt: this.stoppedAt,
      domains: this.registries.domains.count(),
      views: this.registries.views.count(),
      navigationItems: this.registries.navigation.count(),
      widgets: this.registries.widgets.count(),
      dashboards: this.registries.dashboards.count(),
      services: this.registries.services.count(),
    };
  }

  private assertState(
    operation: string,
    allowedStates: readonly WorkspaceRuntimeState[],
  ): void {
    if (!allowedStates.includes(this.state)) {
      throw new WorkspaceRuntimeStateError(
        this.state,
        operation,
      );
    }
  }
}
