import React from 'react';
import { waitFor } from '@testing-library/react';
import log from 'loglevel';

import {
  fetchMock,
  renderWithProviders,
  setFormFields
} from '../../../tests';
import { MockBingoServer, adminUser } from '../../../tests/MockServer';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { ImportInitialFields } from '../../admin/adminSlice';
import { ModifyGame } from './ModifyGame';

import gameData from '../../../tests/fixtures/game/159.json';

const game = {
  ...gameData,
  slug: 'slug',
};

describe('ModifyGame component', () => {
  let apiMock;

  beforeEach(() => {
    apiMock = new MockBingoServer(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    apiMock.shutdown();
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to delete a game', async () => {
    const user = apiMock.getUserState(adminUser);
    const { pk, options } = user;
    const testInitialState = {
      ...initialState,
      user,
      games: {
        ...initialState.games,
        user: pk,
        games: {
          [game.pk]: game,
        },
        gameIds: {
          [game.id]: game.pk
        },
        order: [
          game.pk
        ],
        invalid: false,
        lastUpdated: Date.now()
      }
    };
    //console.log(JSON.stringify(testInitialState));
    const store = createStore(testInitialState);
    const onDelete = vi.fn();
    const props = {
      dispatch: store.dispatch,
      game,
      importing: {
        ...ImportInitialFields,
        added: []
      },
      options,
      onReload: vi.fn(),
      onDelete
    };
    onDelete.mockImplementation((game) => log.debug(`onDelete game ${game.pk}`));
    const { events, findByText, getByText, getByLabelText } = renderWithProviders(<ModifyGame {...props} />, { store });
    expect(getByLabelText("Title", { exact: false }).value).toBe(props.game.title);
    expect(getByLabelText("Colour Scheme", { exact: false }).value).toBe(props.game.options.colour_scheme);
    await events.click(await findByText('Delete game'));
    await findByText("Confirm delete game");
    await events.click(getByText("Yes Please"));
    await waitFor(() => {
      expect(fetchMock.called(`/api/game/${game.pk}`, 'DELETE')).toEqual(true);
    });
    await waitFor(() => {
      expect(onDelete).toHaveBeenCalledTimes(1);
    });
  });

  it('to save a modified game', async () => {
    const user = apiMock.getUserState(adminUser);
    const { options } = user;
    const store = createStore({
      ...initialState,
      user,
    });
    const props = {
      dispatch: store.dispatch,
      game,
      importing: {
        ...ImportInitialFields,
        added: []
      },
      options,
      onReload: vi.fn(),
      onDelete: vi.fn(),
    };
    const { events, getByText, getByLabelText, findByText } = renderWithProviders(
      <ModifyGame {...props} />, { store });
    const titleField = getByLabelText("Title", { exact: false });
    expect(titleField.value).toBe(props.game.title);
    await setFormFields([{
      label: 'Title',
      value: 'new game title',
      exact: false,
    }], events);
    await events.click(getByText('Save Changes'));
    await findByText("Confirm change game");
    getByText('Change title to new game title');
    await events.click(getByText('Yes Please'));
    await waitFor(() => {
      expect(fetchMock.called(`/api/game/${game.pk}`, 'POST')).toEqual(true);
    });
    const { messages } = store.getState();
    const msgList = Object.values(messages.messages);
    expect(msgList.length).toBe(1);
    expect(msgList[0].text).toBe(`Changes to game "${props.game.id}" saved successfully`);
  });
});
