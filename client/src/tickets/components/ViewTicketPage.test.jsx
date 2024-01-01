import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { ViewTicketPage } from './ViewTicketPage';
import { initialState } from '../../store/initialState';
import { createStore } from '../../store/createStore';

describe('ViewTicketPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('renders the selected ticket', async () => {
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          gameId: "18-04-22-2",
          ticketPk: 3483
        }
      }
    });
    const { tracks } = await import('../../fixtures/game/159/ticket/3483.json');
    const { asFragment } = renderWithProviders(<ViewTicketPage />, { store });
    await Promise.all(tracks.map(ticket => {
      return screen.findByText(ticket.title.trim());
    }));
    expect(asFragment()).toMatchSnapshot();
  });
});
