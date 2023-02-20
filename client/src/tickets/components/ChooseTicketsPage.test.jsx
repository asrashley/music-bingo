import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { ChooseTicketsPage } from './ChooseTicketsPage';

describe('ChooseTicketsPage component', () => {
  let apiMock = null;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
  });

  it('to shows a list of tickets', async () => {
    const [userData] = await Promise.all([
      import('../../fixtures/userState.json')
    ]);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: userData['default']
    });
    const history = {
      push: jest.fn()
    };
    const match = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    //log.setLevel('debug');
    const { asFragment } = renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    waitForExpect(() => {
      const btn = document.querySelector('button[data-pk="6597"]');
      expect(btn).not.toBeNull();
    });
    const { games } = store.getState();
    games.games[159].tracks.forEach((track) => {
      const btn = document.querySelector(`button[data-pk="${track.pk}"]`);
      log.debug(`track ${track.pk}`);
      expect(btn).not.toBeNull();
    });
    expect(asFragment()).toMatchSnapshot();
  });

  it('allow a non-admin user to selected a ticket', async () => {
    const [userData] = await Promise.all([
      import('../../fixtures/userState.json')
    ]);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: {
        ...userData['default'],
        groups: {
          user: true
        }
       }
    });
    const history = {
      push: jest.fn()
    };
    const match = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    const claimTicketApi = jest.fn(() => apiMock.jsonResponse('', 200)); // status 406 == already claimed
    fetchMock.put('/api/game/159/ticket/6597', claimTicketApi);
    //log.setLevel('debug');
    renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    waitForExpect(() => {
      const btn = document.querySelector('button[data-pk="6597"]');
      expect(btn).not.toBeNull();
    });
    fireEvent.click(document.querySelector('button[data-pk="6597"]'));
    const confirm = await screen.findByText('Yes Please');
    fireEvent.click(confirm);
  });

  it('shows a failure dialog when a non-admin user selects a ticket that is already taken', async () => {
    const [userData] = await Promise.all([
      import('../../fixtures/userState.json')
    ]);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: {
        ...userData['default'],
        groups: {
          user: true
        }
      }
    });
    const history = {
      push: jest.fn()
    };
    const match = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    const claimTicketApi = jest.fn(() => apiMock.jsonResponse('', 406));
    fetchMock.put('/api/game/159/ticket/6597', claimTicketApi);
    //log.setLevel('debug');
    renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    waitForExpect(() => {
      const btn = document.querySelector('button[data-pk="6597"]');
      expect(btn).not.toBeNull();
    });
    fireEvent.click(document.querySelector('button[data-pk="6597"]'));
    const confirm = await screen.findByText('Yes Please');
    fireEvent.click(confirm);
    await screen.findByText("Sorry that ticket has already been taken");
  });
});


