import React from 'react';
import { fireEvent, screen, getByRole } from '@testing-library/react';
import log from 'loglevel';
import { reverse } from 'named-urls';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { routes } from '../../routes';
import { GuestLinksPage } from './GuestLinksPage';

import user from '../../fixtures/userState.json';
import tokens from '../../fixtures/user/guest.json';

describe('GuestLinksPage component', () => {
  let apiMock = null;

  beforeAll(() => {
    vi.useFakeTimers('modern');
  });

  beforeEach(() => {
    vi.setSystemTime(new Date('08 Apr 2023 18:02:00 GMT').getTime());
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    vi.restoreAllMocks();
    vi.clearAllTimers();
    apiMock = null;
  });

  afterAll(() => {
    vi.useRealTimers();
  });

  it('to shows a list of guest links', async () => {
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
    const { asFragment, findByText } = renderWithProviders(<GuestLinksPage />, { store });
    await Promise.all(tokens.map((token) => {
      const link = reverse(`${routes.guestAccess}`, { token: token.jti });
      return findByText(link);
    }));
    expect(asFragment()).toMatchSnapshot();
  });

  it('reloads guest links', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const fetchGuestSpy = vi.fn((url, data) => data);
    apiMock.setResponseModifier('/api/user/guest', fetchGuestSpy);
    const { findByLastUpdate } = renderWithProviders(<GuestLinksPage />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: tokens[0].jti });
    await screen.findByText(link);
    const update = parseInt(document.querySelector('div.guest-tokens').dataset.lastUpdate, 10);
    vi.advanceTimersByTime(150);
    fireEvent.click(document.querySelector('.refresh-icon'));
    await findByLastUpdate(update, { comparison: 'greaterThan' });
    expect(fetchGuestSpy).toHaveBeenCalledTimes(2);
  });

  it('to allows a guest link to be added', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const token = {
      "pk": 46,
      "jti": "cT34TCj7vg",
      "token_type": 3,
      "username": "cT34TCj7vg",
      "created": "2023-02-20T08:12:54Z",
      "expires": "2023-02-27T08:12:54.014843Z",
      "revoked": false,
      "user": null
    };
    const addLinkApi = vi.fn(() => apiMock.jsonResponse({
      success: true,
      token
    }));
    fetchMock.put('/api/user/guest/add', addLinkApi);
    const { findByLastUpdate } = renderWithProviders(<GuestLinksPage />, { store });
    const guestTokens = document.querySelector('div.guest-tokens');
    expect(guestTokens).not.toBeNull();
    const update = parseInt(guestTokens.dataset.lastUpdate, 10);
    fireEvent.click(screen.getByText('Add link'));
    await findByLastUpdate(update, { comparison: 'greaterThan' });
    expect(addLinkApi).toHaveBeenCalledTimes(1);
    await screen.findByText(token.jti, { exact: false });
  });

  it('to allows a guest link to be deleted', async () => {
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
    const deleteLinkProm = new Promise((resolve) => {
      const deleteLinkApi = vi.fn(() => {
        resolve();
        return apiMock.jsonResponse('', 204);
      });
      fetchMock.delete(`/api/user/guest/delete/${tokens[0].jti}`, deleteLinkApi);
    });
    const { findByText, getByTestId } = renderWithProviders(<GuestLinksPage />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: tokens[0].jti });
    await findByText(link);
    const row = getByTestId(`token.${tokens[0].pk}`);
    fireEvent.click(getByRole(row, 'button'));
    await deleteLinkProm;
  });

});
