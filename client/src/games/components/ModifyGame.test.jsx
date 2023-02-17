import React from 'react';
import { fireEvent, screen, waitForElement } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { ImportInitialFields } from '../../admin/adminSlice';
import { gamesSlice } from '../gamesSlice';
import { ModifyGame } from './ModifyGame';

describe('ModifyGame component', () => {
  let apiMock = null;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
  });

  it('to delete a game', async () => {
    const deleteGameApi = jest.fn(() => apiMock.jsonResponse('', 204));
    fetchMock.delete('/api/game/159', deleteGameApi);
    const { pk, options } = await import('../../fixtures/userState.json');
    const gameData = await import('../../fixtures/game/159.json');
    const store = createStore(initialState);
    const onDelete = jest.fn();
    const props = {
      dispatch: store.dispatch,
      game: gameData['default'],
      importing: { ...ImportInitialFields },
      options,
      onReload: jest.fn(),
      onDelete
    };
    onDelete.mockImplementation((game) => log.debug(`onDelete game ${game.pk}`));
    store.dispatch(gamesSlice.actions.receiveGames({
      timestamp: Date.now(),
      payload: {
        games: [gameData['default']],
        past: []
      },
      user: { pk }
    }));

    const result = renderWithProviders(<ModifyGame {...props} />);
    expect(result.getByLabelText("Title", { exact: false }).value).toBe(props.game.title);
    expect(result.getByLabelText("Colour Scheme", { exact: false }).value).toBe(props.game.options.colour_scheme);
    fireEvent.click(result.getByText('Delete game'));
    await screen.findByText("Confirm delete game");
    fireEvent.click(screen.getByText("Yes Please"));
    await waitForElement(() => {
      expect(deleteGameApi).toHaveBeenCalledTimes(1);
      log.debug('game has been deleted using server API');
      return true;
    });
    log.debug('game has been deleted using server API');
    await waitForElement(() => {
      expect(onDelete).toHaveBeenCalledTimes(1);
      log.debug('AdminGameActions has called onDelete() to confirm deletion');
      return true;
    });
  });
  
  it('to save a modified game', async () => {
    const { pk, options } = await import('../../fixtures/userState.json');
    const gameData = await import('../../fixtures/game/159.json');
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      game: gameData['default'],
      importing: { ...ImportInitialFields },
      options,
      onReload: jest.fn(),
      onDelete: jest.fn(),
    };
    const modifyGameApi = jest.fn((changes) => {
      const response = {
        success: true,
        game: {
          ...props.game,
          ...changes
        }
      };
      return apiMock.jsonResponse(response);
    });
    fetchMock.post('/api/game/159', modifyGameApi);
    store.dispatch(gamesSlice.actions.receiveGames({
      timestamp: Date.now(),
      payload: {
        games: [gameData['default']],
        past: []
      },
      user: { pk }
    }));

    const result = renderWithProviders(<ModifyGame {...props} />);
    const titleField = result.getByLabelText("Title", { exact: false })
    expect(titleField.value).toBe(props.game.title);
    fireEvent.input(titleField, {
      target: {
        value: 'new game title'
      }
    });
    fireEvent.click(result.getByText('Save Changes'));
    await screen.findByText("Confirm change game");
    screen.getByText('Change title to new game title');
    fireEvent.click(screen.getByText('Yes Please'));
    await waitForElement(() => {
      expect(modifyGameApi).toHaveBeenCalledTimes(1);
      log.debug('game has been modified using server API');
      return true;
    });
    const { messages } = store.getState();
    const msgList = Object.values(messages.messages);
    expect(msgList.length).toBe(1);
    expect(msgList[0].text).toBe(`Changes to game "${props.game.id}" saved successfully`);
  });
});
