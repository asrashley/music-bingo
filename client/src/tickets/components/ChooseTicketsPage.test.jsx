import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import * as ticketsSlice from '../ticketsSlice';
import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import user from '../../fixtures/userState.json';
import tickets from '../../fixtures/game/159/tickets.json';

import { ChooseTicketsPage } from './ChooseTicketsPage';

describe('ChooseTicketsPage component', () => {
  let apiMock = null;

  beforeEach(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    jest.spyOn(global, 'setInterval');
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
    jest.clearAllTimers();
    jest.restoreAllMocks();
  });

  it('to shows a list of tickets', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const history = {
      push: jest.fn()
    };
    const match = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    const { asFragment, findByBySelector } = renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    await findByBySelector(`button[data-pk="${tickets[0].pk}"]`);
    for (const ticket of tickets) {
      const btn = document.querySelector(`button[data-pk="${ticket.pk}"]`);
      expect(btn).not.toBeNull();
    }
    expect(asFragment()).toMatchSnapshot();
  });

  let pollCallback = null;

  const testPollStatus = async (loop, updateCount) => {
    let duration = 0;
    log.debug(`****** loop ${loop} ******`);
    return new Promise((resolve) => {
      pollCallback = resolve;
      while (duration <= initialState.tickets.updateInterval) {
        expect(ticketsSlice.fetchTicketsStatusUpdateIfNeeded).toHaveBeenCalledTimes(updateCount);
        jest.advanceTimersByTime(ChooseTicketsPage.ticketPollInterval);
        jest.runAllTicks();
        duration += ChooseTicketsPage.ticketPollInterval;
        updateCount++;
        expect(ticketsSlice.fetchTicketsStatusUpdateIfNeeded).toHaveBeenCalledTimes(updateCount);
      }
      jest.runAllTicks();
    });
  };

  it('polls for ticket updates', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
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
    jest.spyOn(ticketsSlice, 'fetchTicketsStatusUpdateIfNeeded');
    apiMock.setResponseModifier('/api/game/159/status', (url, data) => {
      log.debug(`----------------- /api/game/159/status ---------------- ${Date.now()}`);
      if (pollCallback) {
        pollCallback();
      }
      return data;
    });

    const { container, findByLastUpdate } = renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    expect(setInterval).toHaveBeenCalledTimes(1);
    await screen.findByText('The theme of this round is "Various Artists"');
    log.debug(`lastUpdate = ${container.querySelector('.ticket-chooser').dataset.lastUpdate}`);
    jest.advanceTimersByTime(10);
    for (let loop = 1; loop < 4; ++loop) {
      const lastUpdate = parseInt(container.querySelector('.ticket-chooser').dataset.lastUpdate, 10);
      log.debug(`lastUpdate = ${lastUpdate}`);
      await testPollStatus(loop, (loop - 1) * 7);
      expect(fetchMock.calls('/api/game/159/status', 'GET')).toBeArrayOfSize(loop);
      log.debug(`wait for re-render ${lastUpdate}`);
      await findByLastUpdate(lastUpdate, { comparison: 'greaterThan' });
    }
  });

  it('to reloads a list of tickets', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const history = {
      push: jest.fn()
    };
    const match = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    expect(fetchMock).toHaveFetched('/api/game/159', 'GET');
    expect(fetchMock.calls('/api/game/159', 'GET')).toBeArrayOfSize(1);
    fireEvent.click(document.querySelector('button.refresh-icon'));
    await screen.findByText('The theme of this round is "Various Artists"');
    expect(fetchMock.calls('/api/game/159', 'GET')).toBeArrayOfSize(2);
  });

  it.each([1, 2])('allow a non-admin user to selected %d tickets', async (numTickets) => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user: {
        ...user,
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
    for (let i = 0; i < numTickets; ++i) {
      const ticket = tickets[i];
      fetchMock.put(`/api/game/159/ticket/${ticket.pk}`, claimTicketApi);
    }
    //log.setLevel('debug');
    const { findByBySelector } = renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    for (let i = 0; i < numTickets; ++i) {
      const ticket = tickets[i];
      await findByBySelector(`button[data-pk="${tickets[0].pk}"]`);
      fireEvent.click(document.querySelector(`button[data-pk="${ticket.pk}"]`));
      const confirm = await screen.findByText('Yes Please');
      fireEvent.click(confirm);
      if (i === 0) {
        await screen.findByText("You have selected a ticket");
      } else {
        await screen.findByText(`You have selected ${i + 1} tickets and cannot select any additional tickets`);
      }
    }
  });

  it('shows a failure dialog when a non-admin user selects a ticket that is already taken', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user: {
        ...user,
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
    fetchMock.put('/api/game/159/ticket/3483', claimTicketApi);
    //log.setLevel('debug');
    const { findByBySelector } = renderWithProviders(<ChooseTicketsPage match={match} history={history} />, { store });
    await screen.findByText('The theme of this round is "Various Artists"');
    await findByBySelector('button[data-pk="3483"]');
    fireEvent.click(document.querySelector('button[data-pk="3483"]'));
    const confirm = await screen.findByText('Yes Please');
    fireEvent.click(confirm);
    await screen.findByText("Sorry that ticket has already been taken");
  });
});
