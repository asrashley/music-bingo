import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { PlayGamePage } from './PlayGamePage';

describe('PlayGamePage component', () => {
  let apiMock = null;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
  });

  it('shows an error message if user has not selected any tickets', async () => {
    const match = {
      params: {
        gameId: "18-04-22-2",
        ticketPk: 3483
      }
    };
    renderWithProviders(<PlayGamePage match={match} />);
    await screen.findByText('You need to choose a ticket to be able to play!');
  });

  it('renders the selected game', async () => {
    const ticketPk = 3483;
    const match = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    apiMock.setResponseModifier('/api/game/159/tickets', (url, tickets) => {
      return tickets.map(ticket => {
        if (ticket.pk === ticketPk) {
          return {
            ...ticket,
            user: 1
          };
        }
        return ticket;
      });
    });
    const { tracks } = await import(`../../fixtures/game/159/ticket/${ticketPk}.json`);
    //log.setLevel('debug');
    const { asFragment } = renderWithProviders(<PlayGamePage match={match} />);
    await screen.findByText(tracks[0].title);
    expect(asFragment()).toMatchSnapshot();
  });
});
