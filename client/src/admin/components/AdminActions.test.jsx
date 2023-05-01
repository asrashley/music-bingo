import React from 'react';
import { fireEvent, screen, within } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';
import { saveAs } from 'file-saver';

import { renderWithProviders, installFetchMocks, jsonResponse, MockResponse } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { MockFileReader } from '../../mocks/MockFileReader';
import { MockReadableStream } from '../../mocks/MockReadableStream';

import { AdminActionsComponent, AdminActions } from './AdminActions';
import { DisplayDialog } from '../../components/DisplayDialog';

import user from '../../fixtures/userState.json';
import game from '../../fixtures/game/159.json';

jest.mock('file-saver');

describe('AdminGameActions component', () => {
  const originalLocation = window.location;

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
  let apiMock;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    delete window.location;
    window.location = {
      reload: jest.fn()
    };
  });

  afterEach(() => {
    window.location = originalLocation;
    jest.clearAllTimers();
    fetchMock.mockReset();
    jest.clearAllMocks();
    log.resetLevel();
    jest.restoreAllMocks();
    jest.useRealTimers();
    apiMock = null;
  });

  it('allows game to be exported', async () => {
    const store = createStore(initialState);
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: jest.fn(),
      game,
      importing,
      user
    };
    const result = renderWithProviders(<DisplayDialog>
      <AdminActionsComponent {...props} />
    </DisplayDialog>, { store });
    fireEvent.click(result.getByText('Export game'));
    jest.clearAllTimers();
    jest.useRealTimers();
    await waitForExpect(() => {
      expect(saveAs).toHaveBeenCalledTimes(1);
    });
  });

  it('allows database to be exported', async () => {
    const store = createStore({
      ...initialState,
      user
    });
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: jest.fn(),
      database: true,
      game,
      importing,
      user
    };
    fetchMock.get('/api/database', async (url, opts) => {
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
    const result = renderWithProviders(<DisplayDialog>
      <AdminActionsComponent {...props} />
    </DisplayDialog>, { store });
    fireEvent.click(result.getByText('Export Database'));
    jest.clearAllTimers();
    jest.useRealTimers();
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
      onDelete: jest.fn(),
      game,
      importing,
      user
    };
    const deleteGame = new Promise((resolve) => {
      fetchMock.delete('/api/game/159', (url, opts) => {
        resolve(JSON.parse(opts.body));
        return apiMock.jsonResponse({}, 204);
      });
    });
    const result = renderWithProviders(<DisplayDialog>
      <AdminActionsComponent {...props} />
    </DisplayDialog>, { store });
    fireEvent.click(result.getByText('Delete game'));
    await screen.findByText("Confirm delete game");
    fireEvent.click(screen.getByText('Yes Please'));
    const body = await deleteGame;
    expect(body).toEqual(game);
  });

  it('allows a database to be uploaded', async () => {
    const file = new File([new ArrayBuffer(1)], 'exported-db.json', {
      type: 'application/json'
    });
    const fileReader = new MockFileReader(file.name, null);
    jest.spyOn(window, 'FileReader').mockImplementation(() => fileReader);
    jest.spyOn(window, 'Response').mockImplementation(() => MockResponse);
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
      },
      user
    });
    const { dispatch } = store;
    const props = {
      dispatch,
      onDelete: jest.fn(),
      database: true,
      game,
    };

    const progress = function* () {
      const status = (phase) => {
        jest.advanceTimersByTime(250);
        jest.setSystemTime(Date.now() + 250);
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
      yield status({ text: 'users', pct: 12 });
      yield status({ text: 'albums', pct: 24 });
      yield status({ text: 'artists', pct: 36 });
      yield status({ text: 'directories', pct: 48 });
      yield status({ text: 'songs', pct: 60 });
      yield status({ text: 'games', pct: 72 });
      yield status({ text: 'tracks', pct: 84 });
      yield status({ text: 'bingo tickets', pct: 96 });
      yield status({ text: 'Import complete', pct: 100, done: true });
    };
    const readFileProm = new Promise((resolve) => {
      const mockReadableStream = new MockReadableStream(progress(), resolve);
      fetchMock.put('/api/database', (url, opts) => {
        const resp = new MockResponse(mockReadableStream, {
          status: 200,
          headers: {
            'Content-Type': `multipart/mixed; boundary=${mockReadableStream.boundary}`
          }
        });
        resp.body = {
          getReader: () => mockReadableStream
        };
        return resp;
      });
    });
    const { getByText } = renderWithProviders(<DisplayDialog>
      <AdminActions {...props} />
    </DisplayDialog>, { store });
    fireEvent.click(getByText('Import Database'));
    fireEvent.change(screen.getByTestId("choose-file"), {
      target: {
        files: [file],
      },
    });
    fireEvent.click(screen.getByText('Import database'));
    await screen.findByText('Importing database from "exported-db.json"');
    await readFileProm;
    await screen.findByText('Import complete');
    fireEvent.click(within(document.querySelector('.modal-dialog')).getByText("Close"));
    //await waitForElementToBeRemoved(() => screen.queryByText('Import complete'));
    expect(document.querySelector('.modal-dialog')).toBeNull();
    expect(window.location.reload).toHaveBeenCalledTimes(1);
  });
});
