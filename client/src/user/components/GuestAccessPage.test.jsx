import React from 'react';
import { screen } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';
import { reverse } from 'named-urls';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { GuestAccessPage, GuestAccessPageComponent } from './GuestAccessPage';
import routes from '../../routes';
import { initialState } from '../../store/initialState';
import { gameInitialFields } from '../../games/gamesSlice';
import { ticketInitialState } from '../../tickets/ticketsSlice';

describe('GuestAccessPage component', () => {
  let apiMocks;

  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMocks = null;
  });

  afterAll(() => jest.useRealTimers());

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  it('allows playing as a guest if token is valid', async () => {
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const match = {
      params: {
        token: '123abc'
      }
    };
    const history = {
      push: jest.fn()
    };
    fetchMock.post('/api/user/guest', (url, opts) => {
      return apiMocks.jsonResponse({
        ...user,
        success: true,
        username: 'guest005',
        accessToken: 'guest.access.token',
        password: 'random.secret',
        expires: 3600,
        refreshToken: 'guest.refresh.token',
      });
    });
    const { asFragment } = renderWithProviders(<GuestAccessPage match={match} history={history} />, { preloadedState });
    await screen.findByText('Play as a guest');
    expect(asFragment()).toMatchSnapshot();
  });

  const renderGuestAccessPageComponent = (guest) => {
    const history = {
      push: jest.fn()
    };
    const game = {
      ...gameInitialFields,
      id: '2023-03-10'
    };
    const ticket = {
      ...ticketInitialState(),
      number: 21,
    };
    const props = {
      dispatch: jest.fn(),
      game,
      token: '123abc',
      history,
      ticket,
      user: {
        ...initialState.user,
        guest
      }
    };
    return renderWithProviders(<GuestAccessPageComponent {...props} />);
  };

  it('shows a message if token is being checked', () => {
    const guest = {
      valid: true,
      isFetching: true
    };
    const result = renderGuestAccessPageComponent(guest);
    result.getByText('Checking if guest link is valid...');
  });

  it('shows an error if token is invalid', () => {
    const guest = {
      valid: false,
      isFetching: false
    };
    const result = renderGuestAccessPageComponent(guest);
    result.getByText('Sorry, the link you have used is not recognised');
  });

  it('shows a generic error', () => {
    const guest = {
      valid: true,
      isFetching: false,
      error: 'a generic error'
    };
    const result = renderGuestAccessPageComponent(guest);
    result.getByText(guest.error);
  });

  it('redirects if user is logged in', () => {
    const history = {
      push: jest.fn()
    };
    const game = {
      ...gameInitialFields,
      id: '2023-03-10'
    };
    const ticket = {
      ...ticketInitialState(),
      number: 21,
    };
    const props = {
      dispatch: jest.fn(),
      game,
      token: '123abc',
      history,
      ticket,
      user: {
        ...initialState.user,
        loggedIn: true
      }
    };
    renderWithProviders(<GuestAccessPageComponent {...props} />);
    expect(history.push).toHaveBeenCalledTimes(1);
  });

  it('calls login if guest username and password are provided', async () => {
    const user = {
      ...initialState.user,
      guest: {
        valid: true,
        isFetching: false,
        username: 'guest123',
        email: 'guest123',
        password: 'random.secret'
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };
    const match = {
      params: {
        token: '123abc'
      }
    };
    fetchMock.post('/api/user/guest', (url, opts) => {
      return apiMocks.jsonResponse({
        ...user,
        success: true,
        username: user.guest.username,
        accessToken: apiMocks.getAccessToken(),
        password: user.guest.password,
        expires: 3600,
        refreshToken: 'guest.refresh.token',
      });
    });
    apiMocks.addUser(user.guest);
    const url = await new Promise((resolve) => {
      const history = {
        push: resolve
      };
      renderWithProviders(<GuestAccessPage match={match} history={history} />, { preloadedState });
    });
    expect(url).toEqual(reverse(`${routes.index}`));
  });

});
