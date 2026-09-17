import {
  WorkspaceRuntimeContext,
} from '../../core/workspace-sdk/models/workspace-models';

import {
  WorkspaceRuntime,
} from '../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceBootstrapService,
} from './workspace-bootstrap.service';

import {
  bootstrapWorkspace,
} from './workspace-bootstrap';

describe('bootstrapWorkspace', () => {
  const context =
    {} as WorkspaceRuntimeContext;

  function createBootstrapMock(
    runtime: WorkspaceRuntime,
  ): WorkspaceBootstrapService {
    return {
      getRuntime: vi.fn().mockReturnValue(runtime),
      configure: vi.fn(),
    } as unknown as WorkspaceBootstrapService;
  }

  it('should not initialize a runtime that is already running', async () => {
    const runtime = {
      getState: vi.fn().mockReturnValue('running'),
      initialize: vi.fn(),
      start: vi.fn(),
    } as unknown as WorkspaceRuntime;

    const bootstrap = createBootstrapMock(runtime);

    await bootstrapWorkspace(
      bootstrap,
      context,
    );

    expect(bootstrap.configure)
      .not.toHaveBeenCalled();

    expect(runtime.initialize)
      .not.toHaveBeenCalled();

    expect(runtime.start)
      .not.toHaveBeenCalled();
  });

  it('should initialize and start each runtime only once', async () => {
    const getState = vi.fn()
      .mockReturnValueOnce('created')
      .mockReturnValueOnce('created')
      .mockReturnValueOnce('ready')
      .mockReturnValue('running');

    const runtime = {
      getState,
      initialize: vi.fn().mockResolvedValue(undefined),
      start: vi.fn().mockResolvedValue(undefined),
    } as unknown as WorkspaceRuntime;

    const bootstrap = createBootstrapMock(runtime);

    await bootstrapWorkspace(
      bootstrap,
      context,
    );

    await bootstrapWorkspace(
      bootstrap,
      context,
    );

    expect(bootstrap.configure)
      .toHaveBeenCalledOnce();

    expect(runtime.initialize)
      .toHaveBeenCalledOnce();

    expect(runtime.initialize)
      .toHaveBeenCalledWith(context);

    expect(runtime.start)
      .toHaveBeenCalledOnce();
  });
});