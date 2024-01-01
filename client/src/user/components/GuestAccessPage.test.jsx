import React from 'react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import { createMemoryHistory } from 'history';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';
import { act, screen, waitFor } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { GuestAccessPage } from './GuestAccessPage';
import { routes } from '../../routes';
import { initialState } from '../../store/initialState';
import { createStore } from '../../store/createStore';
import userState from '../../fixtures/userState.json';

function GuestAccessPageTest() {
  return (
    <Routes>
      <Route path="/" element={<div>Index Page</div>} />
      <Route path={routes.guestAccess} element={<GuestAccessPage />} />
    </Routes>);
}

describe('GuestAccessPage component', () => {
  const pushSpy = vi.spyOn(reduxReactRouter, 'push').mockImplementation((url) => {
    return {
      type: 'changeLocation',
      payload: {
        url,
      },
    };
  });
  let apiMocks;

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMocks = null;
    pushSpy.mockClear();
    vi.useRealTimers();
  });

  const renderGuestAccessPageComponent = async (guest) => {
    const history = createMemoryHistory({
      initialEntries: [`/invite/${guest.token}`],
      initialIndex: 0,
    });
    const store = createStore({
      ...initialState,
      user: {
        ...initialState.user,
        guest
      }
    });
    const checkTokenProm = new Promise(resolve => {
      fetchMock.post('/api/user/guest', async () => {
        resolve();
        return apiMocks.jsonResponse({
          success: true
        });
      });
    });

    const result = renderWithProviders(<GuestAccessPageTest />, { store, history });
    await checkTokenProm;
    return result;
  };

  it('allows playing as a guest if token is valid', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/invite/123abc'],
      initialIndex: 0,
    });
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false,
        token: '123abc',
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const username = 'guest005';
    const checkTokenRequest = vi.fn(async (url, opts) => {
      const { token } = JSON.parse(opts.body);
      expect(token).toEqual('123abc');
      return apiMocks.jsonResponse({
        success: true
      });
    });
    fetchMock.post('/api/user/guest', checkTokenRequest);
    const createGuestRequest = vi.fn(async () => {
      return apiMocks.jsonResponse({
        pk: 123,
        username,
        email: username,
        last_login: "2023-02-06T18:23:23.324248Z",
        reset_expires: null,
        reset_token: null,
        groups: ["guests"],
        options: {
          colourScheme: "cyan",
          colourSchemes: ["blue", "red", "yellow"],
          maxTickets: 2,
          rows: 3,
          columns: 5
        },
        accessToken: apiMocks.getAccessToken(),
        refreshToken: apiMocks.getRefreshToken()
      });
    });
    fetchMock.put('/api/user/guest', createGuestRequest);
    const { events, findByText, getByText } = renderWithProviders(
      <GuestAccessPageTest />, { preloadedState, history });
    await findByText('Play as a guest');
    await events.click(getByText('Play as a guest'));
    expect(checkTokenRequest).toHaveBeenCalledTimes(1);
    expect(createGuestRequest).toHaveBeenCalledTimes(1);
  });

  it('matches snapshot', async () => {
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false,
        token: '123abc',
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const history = createMemoryHistory({
      initialEntries: ['/invite/123abc'],
      initialIndex: 0,
    });

    vi.useFakeTimers('modern');
    vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    const checkTokenProm = new Promise(resolve => {
      fetchMock.post('/api/user/guest', async () => {
        resolve();
        return apiMocks.jsonResponse({
          success: true
        });
      });
    });
    const { asFragment, findByText } = renderWithProviders(
      <GuestAccessPageTest />, { preloadedState, history });
    await waitFor(async () => await checkTokenProm);
    await findByText('Play as a guest');
    expect(asFragment()).toMatchSnapshot();
  });

  it('shows an error message if checking guest token fails', async () => {
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false
      },
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const history = createMemoryHistory({
      initialEntries: ['/invite/123abc'],
      initialIndex: 0,
    });

    fetchMock.post('/api/user/guest', async () => 500);
    const { findByText } = renderWithProviders(
      <GuestAccessPageTest />, { preloadedState, history });
    await findByText('Sorry, the link you have used is not recognized');
  });

  it('shows a message if token is being checked', async () => {
    const guest = {
      valid: true,
      token: 'abc123',
      isFetching: true
    };
    const { findByText } = await renderGuestAccessPageComponent(guest);
    await findByText('Checking if guest link is valid...');
  });

  it('shows an error if token is invalid', async () => {
    const guest = {
      token: 'abc123',
      valid: false,
      isFetching: false
    };
    const { findByText } = await renderGuestAccessPageComponent(guest);
    await findByText('Sorry, the link you have used is not recognized');
  });

  it('shows a generic error', async () => {
    const guest = {
      token: 'abc123',
      valid: true,
      isFetching: false,
      error: 'a generic error'
    };
    const { findByText } = await renderGuestAccessPageComponent(guest);
    await findByText(guest.error);
  });

  it('redirects if user is logged in', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/invite/123abc'],
      initialIndex: 0,
    });
    const preloadedState = {
      ...initialState,
      user: {
        ...userState,
        pk: 1,
        loggedIn: true
      }
    };
    fetchMock.post('/api/user/guest', async () => {
      return apiMocks.jsonResponse({
        success: true
      });
    });
    await expect(new Promise(resolve => {
      pushSpy.mockImplementationOnce((url) => {
        resolve(url);
        return {
          type: 'changeLocation',
          payload: {
            url,
          },
        };
      });
      renderWithProviders(<GuestAccessPageTest />, { preloadedState, history });
    })).resolves.toEqual(reverse(`${routes.index}`));
    await act(async () => history.push('/'));
    await screen.findByText('Index Page');
  });

});
