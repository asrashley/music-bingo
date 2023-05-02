import React from 'react';
import { fireEvent, screen, getByRole } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { reverse } from 'named-urls';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import routes from '../../routes';
import { GuestLinksPage } from './GuestLinksPage';

import user from '../../fixtures/userState.json';
import guests from '../../fixtures/user/guest.json';

describe('GuestLinksPage component', () => {
  let apiMock = null;

  beforeEach(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Apr 2023 18:02:00 GMT').getTime());
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    jest.restoreAllMocks();
    jest.clearAllTimers();
    jest.useRealTimers();
    apiMock = null;
  });

  it('to shows a list of guest links', async () => {
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
    const { asFragment } = renderWithProviders(<GuestLinksPage history={history} />, { store });
    await Promise.all(guests.map((token) => {
      const link = reverse(`${routes.guestAccess}`, { token: token.jti });
      return screen.findByText(link);
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
    const history = {
      push: jest.fn()
    };
    const fetchGuestSpy = jest.fn((url, data) => data);
    apiMock.setResponseModifier('/api/user/guest', fetchGuestSpy);
    const { findByLastUpdate } = renderWithProviders(<GuestLinksPage history={history} />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: guests[0].jti });
    await screen.findByText(link);
    const update = parseInt(document.querySelector('div.guest-tokens').dataset.lastUpdate, 10);
    jest.advanceTimersByTime(150);
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
    const history = {
      push: jest.fn()
    };
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
    const addLinkApi = jest.fn(() => apiMock.jsonResponse({
      success: true,
      token
    }));
    fetchMock.put('/api/user/guest/add', addLinkApi);
    const { findByLastUpdate } = renderWithProviders(<GuestLinksPage history={history} />, { store });
    const update = parseInt(document.querySelector('div.guest-tokens').dataset.lastUpdate, 10);
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
        user: user.pk
      },
      user
    });
    const history = {
      push: jest.fn()
    };
    const deleteLinkProm = new Promise((resolve) => {
      const deleteLinkApi = jest.fn(() => {
        resolve();
        return apiMock.jsonResponse('', 204);
      });
      fetchMock.delete(`/api/user/guest/delete/${guests[0].jti}`, deleteLinkApi);
    });
    renderWithProviders(<GuestLinksPage history={history} />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: guests[0].jti });
    await screen.findByText(link);
    const row = screen.getByTestId(`token.${guests[0].pk}`);
    fireEvent.click(getByRole(row, 'button'));
    await deleteLinkProm;
  });

});
