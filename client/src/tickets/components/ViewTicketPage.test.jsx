import React from 'react';
import log from 'loglevel';
import fetchMock from 'fetch-mock';

import { renderWithProviders } from '../../../tests';
import { ViewTicketPage } from './ViewTicketPage';
import { initialState } from '../../store/initialState';
import { createStore } from '../../store/createStore';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';

import { tracks } from '../../../tests/fixtures/game/159/ticket/3483.json';

describe('ViewTicketPage component', () => {
  afterEach(() => {
    fetchMock.reset();
    log.resetLevel();
  });

  it('renders the selected ticket', async () => {
    const mockServer = new MockBingoServer(fetchMock, { currentUser: normalUser });
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          gameId: "18-04-22-2",
          ticketPk: 3483
        }
      },
      user: mockServer.getUserState(normalUser),
    });
    const { asFragment, findByText } = renderWithProviders(<ViewTicketPage />, { store });
    await Promise.all(tracks.map(ticket => findByText(ticket.title.trim())));
    await fetchMock.flush(true);
    expect(asFragment()).toMatchSnapshot();
  });
});
