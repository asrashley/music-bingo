import React from 'react';
import { vi } from 'vitest';
import { act, screen, within } from '@testing-library/react';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';
import { saveAs } from 'file-saver';

import {
  fetchMock,
  renderWithProviders,
  installFetchMocks,
  jsonResponse,
  MockResponse
} from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { MockFileReader } from '../../../tests/MockFileReader';
import { MockReadableStream } from '../../../tests/MockReadableStream';

import { AdminActionsComponent, AdminActions } from './AdminActions';
import { DisplayDialog } from '../../components/DisplayDialog';

import user from '../../../tests/fixtures/userState.json';
import gameData from '../../../tests/fixtures/game/159.json';

const game = {
  ...gameData,
  slug: 'slug',
};

vi.mock('file-saver', () => {
  return {
    saveAs: vi.fn(),
  };
});

Object.defineProperty(window, 'location', {
  writable: true,
  value: {
    reload: vi.fn(),
  },
});

describe('AdminGameActions component', () => {
  const importing = {
    added: [],
    done: false,
    errors: [],
    filename: '',
    text: '',
    timestamp: 0,
    numPhases: 1,
    pct: 0,
    phase: 1
  };

  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    vi.clearAllMocks();
    log.resetLevel();
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('allows game to be exported', async () => {
    const store = createStore(initialState);
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: vi.fn(),
      game,
      importing,
      user
    };
    const { events, getByText } = renderWithProviders(<AdminActionsComponent {...props} />, { store });
    await events.click(getByText('Export game'));
    await waitForExpect(() => {
      expect(saveAs).toHaveBeenCalledTimes(1);
    });
    expect(saveAs).toHaveBeenCalledWith(expect.anything(), "game-18-04-22-2.json");
  });

  it('allows database to be exported', async () => {
    const store = createStore({
      ...initialState,
      user
    });
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: vi.fn(),
      database: true,
      game,
      importing,
      user
    };
    let dbResolve;
    const dbResponseProm = new Promise((resolve) => {
      dbResolve = resolve;
    });
    fetchMock.get('/api/database', async () => {
      await dbResponseProm;
      return jsonResponse({
        "Users": [],
        "Albums": [],
        "Directories": [],
        "Songs": [],
        "Games": [],
        "Tracks": [],
        "BingoTickets": []
      });
    });
    const { events, findByText, getByText } = renderWithProviders(
      <AdminActionsComponent {...props} />, { store });
    await events.click(getByText('Export Database'));
    await findByText("Please wait, exporting database...");
    await act(() => {
      dbResolve();
    });
    await waitForExpect(() => {
      expect(saveAs).toHaveBeenCalledTimes(1);
    });
  });

  it('allows game to be deleted', async () => {
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        games: {
          [game.pk]: game
        },
        gameIds: {
          [game.id]: game.pk
        },
        pastOrder: [
          game.pk
        ],
        user: user.pk,
        invalid: false
      }
    });
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: vi.fn(),
      game,
      importing,
      user
    };
    const deleteGame = new Promise((resolve) => {
      fetchMock.delete('/api/game/159', (url, opts) => {
        resolve(JSON.parse(opts.body));
        return jsonResponse('', 204);
      });
    });
    const { events, findByText, getByText } = renderWithProviders(<DisplayDialog>
      <AdminActionsComponent {...props} />
    </DisplayDialog>, { store });
    await events.click(getByText('Delete game'));
    await findByText("Confirm delete game");
    await events.click(getByText('Yes Please'));
    const body = await deleteGame;
    expect(body).toEqual(game);
  });

  it.each(['database', 'game'])('allows a %s to be uploaded', async (importType) => {
    const inputFilename = importType === 'database' ? 'exported-db.json' : 'exported-game.json';
    const file = new File([new ArrayBuffer(1)], inputFilename, {
      type: 'application/json'
    });
    const fileReader = new MockFileReader(file.name, null);
    vi.spyOn(window, 'FileReader').mockImplementationOnce(() => fileReader);
    vi.spyOn(window, 'Response').mockImplementationOnce(() => MockResponse);
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        games: {
          [game.pk]: game,
        },
        gameIds: {
          [game.id]: game.pk
        },
        pastOrder: [
          game.pk
        ],
        user: user.pk,
        invalid: false
      },
      user
    });
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: vi.fn(),
      database: true,
      game,
    };

    const progress = async function* () {
      const status = (phase) => {
        return ({
          "errors": [],
          "text": "",
          "pct": 0,
          "phase": 1,
          "numPhases": 1,
          "done": false,
          ...phase
        });
      };
      if (importType === 'database') {
        await Promise.resolve();
        yield status({ text: 'options', pct: 1 });
        await Promise.resolve();
        yield status({ text: 'users', pct: 12 });
        await Promise.resolve();
        yield status({ text: 'albums', pct: 24 });
        await Promise.resolve();
        yield status({ text: 'artists', pct: 36 });
      }
      await Promise.resolve();
      yield status({ text: 'directories', pct: 48 });
      await Promise.resolve();
      yield status({ text: 'songs', pct: 60 });
      await Promise.resolve();
      yield status({ text: 'games', pct: 72 });
      await Promise.resolve();
      yield status({ text: 'tracks', pct: 84 });
      await Promise.resolve();
      yield status({ text: 'bingo tickets', pct: 96 });
      await Promise.resolve();
      yield status({ text: 'Import complete', pct: 100, done: true });
    };
    const readFileProm = new Promise((resolve) => {
      const mockReadableStream = new MockReadableStream(progress(), resolve);
      const importUrl = importType === 'database' ? '/api/database' : '/api/games'
      fetchMock.put(importUrl, () => {
        const resp = new MockResponse(mockReadableStream, {
          status: 200,
          headers: {
            'Content-Type': `multipart/mixed; boundary=${mockReadableStream.boundary}`
          }
        });
        Object.defineProperty(resp, 'body', {
          value: {
            getReader: () => mockReadableStream
          }
        });
        return resp;
      });
    });
    const { events, getByText, getByTestId } = renderWithProviders(<AdminActions {...props} />, { store });
    if (importType === 'database') {
      await events.click(getByText('Import Database'));
    } else {
      await events.click(getByText('Import Game'));
    }
    await events.upload(getByTestId("choose-file"), file);
    if (importType === 'database') {
      await events.click(screen.getByText('Import database'));
    } else {
      await events.click(screen.getByText('Import game'));
    }
    await screen.findByText(`Importing ${importType} from "${inputFilename}"`);
    await readFileProm;
    await screen.findByText('Import complete');
    await events.click(within(document.querySelector('.modal-dialog')).getByText("Close"));
    //await waitForElementToBeRemoved(() => screen.queryByText('Import complete'));
    expect(document.querySelector('.modal-dialog')).toBeNull();
    if (importType === 'database') {
      expect(window.location.reload).toHaveBeenCalledTimes(1);
    }
  });
});
