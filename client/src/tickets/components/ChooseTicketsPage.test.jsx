import { vi } from 'vitest';
import { act } from '@testing-library/react';
import log from 'loglevel';

import * as ticketsSlice from '../ticketsSlice';
import { fetchMock, renderWithProviders } from '../../../tests';
import { adminUser, normalUser, MockBingoServer } from '../../../tests/MockServer';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import tickets from '../../../tests/fixtures/game/159/tickets.json';

import { ChooseTicketsPage } from './ChooseTicketsPage';

describe('ChooseTicketsPage component', () => {
  const fixedDateTime = new Date('08 Feb 2023 10:12:00 GMT').getTime();
  let apiMock, user;

  beforeEach(() => {
    apiMock = new MockBingoServer(fetchMock, { loggedIn: true });
    user = apiMock.getUserState(normalUser);
  });

  afterEach(() => {
    apiMock.shutdown();
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
    vi.clearAllTimers();
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('shows a list of tickets', async () => {
    vi.useFakeTimers();
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
    vi.useFakeTimers();
    vi.setSystemTime(fixedDateTime);
    vi.spyOn(ticketsSlice, 'fetchTicketsStatusUpdateIfNeeded');
    const intervalSpy = vi.spyOn(window, 'setInterval');
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

    const { findByText } = renderWithProviders(<ChooseTicketsPage />, { store });
    expect(ticketsSlice.fetchTicketsStatusUpdateIfNeeded).toHaveBeenCalledTimes(0);
    expect(fetchMock.calls('/api/game/159/status', 'GET').length).toEqual(0);
    expect(intervalSpy).toHaveBeenCalledTimes(1);
    await findByText('The theme of this round is "Various Artists"');
    const endTime = Date.now() + ticketsSlice.initialState.updateInterval;
    act(() => {
      while (Date.now() <= endTime) {
        vi.advanceTimersToNextTimer();
        vi.runOnlyPendingTimers();
      }
    });
    expect(ticketsSlice.fetchTicketsStatusUpdateIfNeeded).toHaveBeenCalled();
    act(() => {
      vi.advanceTimersToNextTimer();
      vi.runOnlyPendingTimers();
    });
    expect(fetchMock.calls('/api/game/159/status', 'GET').length).toEqual(1);
  });

  it('reloads a list of tickets by an admin user', async () => {
    const admin = apiMock.getUserState(adminUser);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: admin.pk
      },
      routes: {
        params: {
          gameId: "18-04-22-2"
        },
      },
      user: admin,
    });
    const getGamePromise = apiMock.addResponsePromise('/api/game/159', 'GET');
    const { events, findByText, findByTestId } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    await getGamePromise;
    expect(fetchMock).toHaveFetched('/api/game/159', 'GET');
    expect(fetchMock.calls('/api/game/159', 'GET').length).toEqual(1);
    await events.click(await findByTestId('refresh-game-button'));
    await findByText('The theme of this round is "Various Artists"');
    expect(fetchMock.calls('/api/game/159', 'GET').length).toEqual(2);
  });

  it.each([1, 2])('allow a non-admin user to select %d tickets', async (numTickets) => {
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
      user,
    });
    //log.setLevel('debug');
    const { events, findByText, findBySelector } = renderWithProviders(<ChooseTicketsPage />, { store });
    findByText('The theme of this round is "Various Artists"');
    for (let i = 0; i < numTickets; ++i) {
      const ticket = tickets[i];
      const elt = await findBySelector(`button[data-pk="${ticket.pk}"]`);
      await events.click(elt);
      const confirm = await findByText('Yes Please');
      await events.click(confirm);
      if (i === 0) {
        await findByText("You have selected a ticket");
      } else {
        await findByText(`You have selected ${i + 1} tickets and cannot select any additional tickets`);
      }
    }
    await fetchMock.flush(true);
  });

  it('shows a failure dialog when a non-admin user selects a ticket that is already taken', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: normalUser.pk
      },
      routes: {
        params: {
          gameId: "18-04-22-2"
        },
      },
      user: {
        ...user,
        ...normalUser,
        groups: {
          user: true
        }
      }
    });
    //log.setLevel('debug');
    const { events, findBySelector, findByText } = renderWithProviders(<ChooseTicketsPage />, { store });
    await findByText('The theme of this round is "Various Artists"');
    await findBySelector('button[data-pk="3483"]');
    await events.click(document.querySelector('button[data-pk="3483"]'));
    const confirm = await findByText('Yes Please');
    await apiMock.claimTicketForUser(159, 3483, adminUser);
    await events.click(confirm);
    await findByText("Sorry that ticket has already been taken");
  });
});
