import React from 'react';
import { screen } from '@testing-library/react';
import { createMemoryHistory } from 'history';
import log from 'loglevel';

import { fetchMock, renderWithProviders } from '../../../tests';
import { adminUser, MockBingoServer } from '../../../tests/MockServer';
import { TestGameWrapper } from './TestGameWrapper.test'

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { tracks } from '../../../tests/fixtures/game/159/ticket/3483.json';

describe('PlayGamePage component', () => {
  const gameId = "18-04-22-2";
  const gamePk = 159;
  const ticketPk = 3483;
  let apiMock = null;

  beforeEach(() => {
    apiMock = new MockBingoServer(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
  });

  it('shows an error message if user has not selected any tickets', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/', `/game/${gameId}/tickets`],
      initialIndex: 1,
    });

    const store = createStore({
      ...initialState,
      routes: {
        params: {
          gameId,
        }
      },
    });
    renderWithProviders(<TestGameWrapper />, { history, store });
    await screen.findByText('You need to choose a ticket to be able to play!');
  });

  it('renders the selected game', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/', `/game/${gameId}/tickets`],
      initialIndex: 1,
    });

    const user = apiMock.getUserState(adminUser);
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        user: user.pk,
      },
      routes: {
        params: {
          gameId,
        },
      },
      user,
    });
    apiMock.claimTicketForUser(gamePk, ticketPk, adminUser);
    const { asFragment, findByText } = renderWithProviders(
      <TestGameWrapper />, { history, store });
    await findByText(tracks[0].title);
    expect(asFragment()).toMatchSnapshot();
  });
});
