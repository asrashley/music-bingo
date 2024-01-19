import React from 'react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import { createMemoryHistory } from 'history';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';
import { act, screen, waitFor } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../../tests';
import { GuestAccessPage } from './GuestAccessPage';
import { routes } from '../../routes';
import { initialState } from '../../store/initialState';
import { createStore } from '../../store/createStore';
import { adminUser } from '../../../tests/MockServer';

function GuestAccessPageTest() {
  return (
    <Routes>
      <Route path="/" element={<div>Index Page</div>} />
      <Route path={routes.guestAccess} element={<GuestAccessPage />} />
    </Routes>);
}

async function renderGuestAccessPageComponent(apiMocks, guest, waitForServer = true) {
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
  const checkTokenProm = waitForServer ? apiMocks.addResponsePromise('/api/user/guest', 'POST') : Promise.resolve();
  const result = renderWithProviders(<GuestAccessPageTest />, { store, history });
  await waitFor(async () => {
    await checkTokenProm;
  });
  return result;
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
    apiMocks = installFetchMocks(fetchMock);
  });

  afterEach(() => {
    apiMocks.shutdown();
    apiMocks = null;
    log.resetLevel();
    pushSpy.mockClear();
    vi.useRealTimers();
  });

  it('allows playing as a guest if token is valid', async () => {
    const token = apiMocks.guestTokens[0].jti;
    const history = createMemoryHistory({
      initialEntries: [`/invite/${token}`],
      initialIndex: 0,
    });
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false,
        token,
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const createGuestUserProm = apiMocks.addResponsePromise('/api/user/guest', 'PUT');
    const { events, findByText, getByText } = renderWithProviders(
      <GuestAccessPageTest />, { preloadedState, history });
    await findByText('Play as a guest');
    await events.click(getByText('Play as a guest'));
    await createGuestUserProm;
    expect(fetchMock.calls('/api/user/guest', 'POST').length).toEqual(0);
    expect(fetchMock.calls('/api/user/guest', 'PUT').length).toEqual(1);
  });

  it('matches snapshot', async () => {
    const token = apiMocks.guestTokens[0].jti;
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false,
        token,
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const history = createMemoryHistory({
      initialEntries: [`/invite/${token}`],
      initialIndex: 0,
    });

    vi.useFakeTimers();
    vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    const { asFragment, findByText } = renderWithProviders(
      <GuestAccessPageTest />, { preloadedState, history });
    await findByText('Play as a guest');
    expect(asFragment()).toMatchSnapshot();
  });

  it('shows an error message if checking guest token fails', async () => {
    const preloadedState = {
      ...initialState,
    };
    const history = createMemoryHistory({
      initialEntries: ['/invite/123abc'],
      initialIndex: 0,
    });
    const checkTokenProm = apiMocks.addResponsePromise('/api/user/guest', 'POST');
    const { findByText } = renderWithProviders(
      <GuestAccessPageTest />, { history, preloadedState });
    await waitFor(async () => {
      await checkTokenProm;
    });
    await findByText('Sorry, the link you have used is not recognized');
  });

  it('shows a message while token is being checked', async () => {
    const guest = {
      valid: null,
      token: 'abc123', // apiMocks.guestTokens[0].jti,
      isFetching: false
    };
    let checkResolve;
    const blockResponse = new Promise(resolve => {
      checkResolve = resolve;
    });
    apiMocks.setResponseModifier('/api/user/guest', 'POST', async (_url, _opts, data) => {
      await blockResponse;
      return data;
    });
    const { findByText } = await renderGuestAccessPageComponent(apiMocks, guest, false);
    await findByText('Checking if guest link is valid...');
    act(() => {
      checkResolve();
    });
    await fetchMock.flush(true);
    await findByText('Sorry, the link you have used is not recognized');
  });

  it('shows an error if token is invalid', async () => {
    const guest = {
      token: 'abc123',
      valid: false,
      isFetching: false
    };
    //log.setLevel('debug');
    const { findByText } = await renderGuestAccessPageComponent(apiMocks, guest);
    await findByText('Sorry, the link you have used is not recognized');
  });

  it('shows a generic error', async () => {
    const guest = {
      token: 'abc123',
      valid: true,
      isFetching: false,
      error: 'a generic error'
    };
    const { findByText } = await renderGuestAccessPageComponent(apiMocks, guest, false);
    await findByText(guest.error);
  });

  it('redirects if user is logged in', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/invite/123abc'],
      initialIndex: 0,
    });
    const preloadedState = {
      ...initialState,
      user: apiMocks.getUserState(adminUser),
    };
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
    await waitFor(async () => history.push('/'));
    await screen.findByText('Index Page');
  });

});
