import React from 'react';
import { act } from '@testing-library/react';
import log from 'loglevel';

import * as ticketsSlice from '../ticketsSlice';
import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import user from '../../fixtures/userState.json';
import tickets from '../../fixtures/game/159/tickets.json';

import { ChooseTicketsPage } from './ChooseTicketsPage';
import { vi } from 'vitest';

describe('ChooseTicketsPage component', () => {
  let apiMock = null;
  const fixedDateTime = new Date('08 Feb 2023 10:12:00 GMT').getTime();

  beforeAll(() => {
  });

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
    vi.clearAllTimers();
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('shows a list of tickets', async () => {
    vi.useFakeTimers('modern');
    vi.setSystemTime(fixedDateTime);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          gameId: "18-04-22-2"
        }
      },
      user
    });
    const { findBySelector, findByText } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    await findBySelector(`button[data-pk="${tickets[0].pk}"]`);
    await Promise.all(tickets.map(ticket => findBySelector(`button[data-pk="${ticket.pk}"]`)));
  });

  it('polls for ticket updates', async () => {
    vi.useFakeTimers('modern');
    vi.setSystemTime(fixedDateTime);
    vi.spyOn(ticketsSlice, 'fetchTicketsStatusUpdateIfNeeded');
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          gameId: "18-04-22-2"
        },
      },
      user
    });

    let pollCallback = null;
    apiMock.setResponseModifier('/api/game/159/status', (url, data) => {
      if (pollCallback) {
        pollCallback();
      }
      return data;
    });

    const testPollStatus = async (loop, updateCount) => {
      const pollProm = new Promise(resolve => {
        pollCallback = resolve;
      });
      let duration = 0;
      while (duration <= initialState.tickets.updateInterval) {
        expect(ticketsSlice.fetchTicketsStatusUpdateIfNeeded).toHaveBeenCalledTimes(updateCount);
        await act(() => {
          vi.advanceTimersByTime(ChooseTicketsPage.ticketPollInterval);
          vi.runAllTicks();
        });
        duration += ChooseTicketsPage.ticketPollInterval;
        updateCount++;
        expect(ticketsSlice.fetchTicketsStatusUpdateIfNeeded).toHaveBeenCalledTimes(updateCount);
      }
      await act(() => {
        vi.runAllTicks();
      });
      await pollProm;
    };

    const { container, findByText, findByLastUpdate } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    log.debug(`lastUpdate = ${container.querySelector('.ticket-chooser').dataset.lastUpdate}`);
    await act(() => vi.advanceTimersByTime(10));
    for (let loop = 1; loop < 3; ++loop) {
      const lastUpdate = parseInt(container.querySelector('.ticket-chooser').dataset.lastUpdate, 10);
      await testPollStatus(loop, (loop - 1) * 7);
      expect(fetchMock.calls('/api/game/159/status', 'GET').length).toEqual(loop);
      await findByLastUpdate(lastUpdate, { comparison: 'greaterThan' });
    }
  }, 8000);

  it('reloads a list of tickets', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          gameId: "18-04-22-2"
        },
      },
      user
    });
    const { events, findByText } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    expect(fetchMock).toHaveFetched('/api/game/159', 'GET');
    expect(fetchMock.calls('/api/game/159', 'GET').length).toEqual(1);
    const apiProm = new Promise(resolve => {
      apiMock.setResponseModifier('/api/game/159', (url, data) => {
        resolve(url);
        return data;
      });
    });
    await events.click(document.querySelector('button.refresh-icon'));
    await apiProm;
    await findByText('The theme of this round is "Various Artists"');
  });

  it.each([1, 2])('allow a non-admin user to selected %d tickets', async (numTickets) => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          gameId: "18-04-22-2"
        },
      },
      user: {
        ...user,
        groups: {
          user: true
        }
      }
    });
    const claimTicketApi = vi.fn(() => apiMock.jsonResponse('', 200)); // status 406 == already claimed
    for (let i = 0; i < numTickets; ++i) {
      const ticket = tickets[i];
      fetchMock.put(`/api/game/159/ticket/${ticket.pk}`, claimTicketApi);
    }
    //log.setLevel('debug');
    const { events, findByText, findBySelector } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    for (let i = 0; i < numTickets; ++i) {
      const ticket = tickets[i];
      await findBySelector(`button[data-pk="${tickets[0].pk}"]`);
      await events.click(document.querySelector(`button[data-pk="${ticket.pk}"]`));
      const confirm = await findByText('Yes Please');
      await events.click(confirm);
      if (i === 0) {
        await findByText("You have selected a ticket");
      } else {
        await findByText(`You have selected ${i + 1} tickets and cannot select any additional tickets`);
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
      routes: {
        params: {
          gameId: "18-04-22-2"
        },
      },
      user: {
        ...user,
        groups: {
          user: true
        }
      }
    });
    const claimTicketApi = vi.fn(() => apiMock.jsonResponse('', 406));
    fetchMock.put('/api/game/159/ticket/3483', claimTicketApi);
    //log.setLevel('debug');
    const { events, findBySelector, findByText } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    await findBySelector('button[data-pk="3483"]');
    await events.click(document.querySelector('button[data-pk="3483"]'));
    const confirm = await findByText('Yes Please');
    await events.click(confirm);
    await findByText("Sorry that ticket has already been taken");
  });
});
