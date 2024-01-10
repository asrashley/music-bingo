import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders } from '../../../tests';
import { adminUser, MockBingoServer } from '../../../tests/MockServer';
import { PlayGamePage } from './PlayGamePage';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { tracks } from '../../../tests/fixtures/game/159/ticket/3483.json';

describe('PlayGamePage component', () => {
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
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          gameId: "18-04-22-2",
          ticketPk: 3483
        }
      },
    });
    renderWithProviders(<PlayGamePage />, { store });
    await screen.findByText('You need to choose a ticket to be able to play!');
  });

  it('renders the selected game', async () => {
    const gamePk = 159;
    const ticketPk = 3483;
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          gameId: "18-04-22-2",
          ticketPk,
        },
      },
    });
    apiMock.claimTicketForUser(gamePk, ticketPk, adminUser);
    const { asFragment, findByText } = renderWithProviders(<PlayGamePage />, { store });
    await findByText(tracks[0].title);
    expect(asFragment()).toMatchSnapshot();
  });
});
