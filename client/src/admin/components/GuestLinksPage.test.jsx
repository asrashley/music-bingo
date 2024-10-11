import React from 'react';
import { act, fireEvent, getByRole, waitFor } from '@testing-library/react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import fetchMock from 'fetch-mock';

import { renderWithProviders, installFetchMocks } from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { routes } from '../../routes';
import { GuestLinksPage } from './GuestLinksPage';

import { adminUser } from '../../../tests/MockServer';

describe('GuestLinksPage component', () => {
  let apiMock = null;

  beforeAll(() => {
    vi.useFakeTimers();
  });

  beforeEach(() => {
    vi.setSystemTime(new Date('08 Apr 2023 18:02:00 GMT').getTime());
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.reset();
    log.resetLevel();
    vi.restoreAllMocks();
    vi.clearAllTimers();
    apiMock = null;
  });

  afterAll(() => {
    vi.useRealTimers();
  });

  it('to shows a list of guest links', async () => {
    const user = apiMock.getUserState(adminUser);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk,
        guest: {
          tokens: apiMock.guestTokens,
          invalid: false,
          error: null,
          lastUpdated: Date.now(),
        },
      },
      user
    });
    const { asFragment, findByText } = renderWithProviders(<GuestLinksPage />, { store });
    await Promise.all(apiMock.guestTokens.map((token) => {
      const link = reverse(`${routes.guestAccess}`, { token: token.jti });
      return findByText(link);
    }));
    expect(asFragment()).toMatchSnapshot();
  });

  it('reloads guest links', async () => {
    const user = apiMock.getUserState(adminUser);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const { findByText, findByLastUpdate } = renderWithProviders(<GuestLinksPage />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: apiMock.guestTokens[0].jti });
    await findByText(link);
    const update = parseInt(document.querySelector('div.guest-tokens').dataset.lastUpdate, 10);
    act(() => {
      vi.advanceTimersByTime(150);
      vi.runOnlyPendingTimers();
    });
    fireEvent.click(document.querySelector('.refresh-icon'));
    await findByLastUpdate(update, { comparison: 'greaterThan' });
    expect(fetchMock.calls('/api/user/guest', 'GET').length).toEqual(2);
  });

  it('to allows a guest link to be added', async () => {
    const user = apiMock.getUserState(adminUser);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const addTokenPromise = apiMock.addResponsePromise('/api/user/guest/add', 'PUT');
    const { findByText, getByText } = renderWithProviders(<GuestLinksPage />, { store });
    const before = apiMock.guestTokens.length;
    fireEvent.click(getByText('Add link'));
    await waitFor(async () => {
      await addTokenPromise;
    })
    await fetchMock.flush(true);
    expect(fetchMock.calls('/api/user/guest/add', 'PUT').length).toEqual(1);
    expect(apiMock.guestTokens.length).toEqual(before + 1);
    const token = apiMock.guestTokens[apiMock.guestTokens.length - 1];
    await findByText(`/invite/${token.jti}`, { exact: false });
  });

  it('to allows a guest link to be deleted', async () => {
    const user = apiMock.getUserState(adminUser);
    const tokens = apiMock.guestTokens;
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk,
        guest: {
          tokens,
          invalid: false,
          error: null,
          lastUpdated: Date.now(),
        },
      },
      user
    });
    const deleteLinkProm = apiMock.addResponsePromise(
      `/api/user/guest/delete/${tokens[0].jti}`, 'DELETE');
    const { findByText, getByTestId } = renderWithProviders(<GuestLinksPage />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: tokens[0].jti });
    await findByText(link);
    const row = getByTestId(`token.${tokens[0].pk}`);
    fireEvent.click(getByRole(row, 'button'));
    await deleteLinkProm;
  });

});
