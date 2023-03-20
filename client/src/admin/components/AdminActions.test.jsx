import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';
import { saveAs } from 'file-saver';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { AdminActionsComponent } from './AdminActions';
import { DisplayDialog } from '../../components/DisplayDialog';

import * as user from '../../fixtures/userState.json';
import * as game from '../../fixtures/game/159.json';

jest.mock('file-saver');

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
});
