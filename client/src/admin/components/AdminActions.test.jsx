import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';
import { saveAs } from 'file-saver';

import { renderWithProviders, installFetchMocks, MockResponse } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { AdminActionsComponent } from './AdminActions';
import { DisplayDialog } from '../../components/DisplayDialog';

import * as user from '../../fixtures/userState.json';
import * as game from '../../fixtures/game/159.json';

jest.mock('file-saver');

class MockFileReader {
  constructor(filename, error) {
    this.filename = filename;
    this.error = error;
  }
  onload = (ev) => false;
  onerror = (ev) => false;

  readAsText(file) {
    if (this.error) {
      this.onerror(this.error);
    } else {
      import(`../../fixtures/${this.filename}`)
        .then((result) => {
          const event = {
            target: {
              result: JSON.stringify(result.default)
            }
          };
          this.onload(event);
        });
    }
  }
}

class MockReadableStream extends ReadableStream {
  constructor(parts, done) {
    super();
    this.parts = parts;
    this.textEnc = new TextEncoder();
    this.boundary = `${Date.now()}`;
    this.pos = 0;
    this.onDone = done;
  }

  read() {
    return new Promise((resolve) => {
      const done = (this.pos === this.parts.length);
      let value;
      if (!done) {
        const payload = JSON.stringify(this.parts[this.pos]);
        const headers = `Content-Type: application/json\r\nContent-Length: ${payload.length}\r\n`;
        value = `--${this.boundary}\r\n${headers}\r\n${payload}\r\n\r\n`;
        this.pos++;
        if (this.pos === this.parts.length) {
          value += `--${this.boundary}--\r\n`;
        }
        value = this.textEnc.encode(value);
      }
      resolve({
        done,
        value
      });
      if (done) {
        this.onDone();
      }
    });
  }
};

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
  let apiMock;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    jest.clearAllMocks();
    log.resetLevel();
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
    //log.setLevel('debug');
    const result = renderWithProviders(<DisplayDialog>
      <AdminActionsComponent {...props} />
    </DisplayDialog>, { store });
    fireEvent.click(result.getByText('Export game'));
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
    //log.setLevel('debug');
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
      }
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

    const progress = [
      { text: 'users', pct: 12 },
      { text: 'albums', pct: 24 },
      { text: 'artists', pct: 36 },
      { text: 'directories', pct: 48 },
      { text: 'songs', pct: 60 },
      { text: 'games', pct: 72 },
      { text: 'tracks', pct: 84 },
      { text: 'bingo tickets', pct: 96 },
      { text: 'import complete', pct: 100, done: true },
    ].map((phase) => {
      const status = {
        "errors": [],
        "text": "",
        "pct": 0,
        "phase": 1,
        "numPhases": 1,
        "done": false,
        ...phase
      };
      return status;
    });
    await new Promise((resolve) => {
      const mockReadableStream = new MockReadableStream(progress, resolve);
      fetchMock.put('/api/database', (url, opts) => {
        //const body = progress.map((stage) => `--${boundary}\r\n\r\n${JSON.stringify(stage)}\r\n\r\n`).join('');
        const resp = new MockResponse(mockReadableStream, {
          status: 200,
          headers: {
            'Content-Type': `multipart/mixed; boundary=${mockReadableStream.boundary}`
          }
        });
        resp.body = {
          getReader: () => mockReadableStream
        };
        //jest.spyOn(resp.body, 'getReader').mockImplementation(() => mockReader);
        return resp;
      });
      const result = renderWithProviders(<DisplayDialog>
        <AdminActionsComponent {...props} />
      </DisplayDialog>, { store });
      fireEvent.click(result.getByText('Import Database'));
      fireEvent.change(screen.getByTestId("choose-file"), {
        target: {
          files: [file],
        },
      });
      fireEvent.click(screen.getByText('Import database'));
    });
  });
});
